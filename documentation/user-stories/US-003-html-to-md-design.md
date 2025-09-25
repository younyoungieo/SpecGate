# US-003: HTML→MD 변환 기능 설계 문서

## 1. 기능 개요

### 1.1 목적
Confluence에서 수집한 HTML 문서를 Markdown 형식으로 변환하여 Phase 2에서 설계 규칙 추출이 가능한 표준화된 문서를 생성한다.

### 1.2 핵심 기능
- **단일 모듈 구조**: HTMLToMarkdownConverter 클래스 중심 (HTMLParser, HTMLValidator는 미구현)
- **MCP 도구 제거**: 독립적인 html_to_md MCP 도구는 제거, confluence_fetch 내부에서만 사용
- **파일 저장 기능**: save_to_file 매개변수로 제어 (기본 경로: `.specgate/data/md_files/`)
- **성능 측정**: 단계별 변환 시간 측정 및 로깅
- **Confluence 특화**: 매크로(ac:structured-macro) 변환 지원
- **중급 변환**: 표, 코드 블록, 인라인 요소, 인용문 등 포괄적 지원

## 2. 변환 규칙

### 2.1 기본 변환 매핑
```python
CONVERSION_MAPPING = {
    'headings': {
        'h1': '# ',
        'h2': '## ',
        'h3': '### ',
        'h4': '#### ',
        'h5': '##### ',
        'h6': '###### '
    },
    'text_formatting': {
        'strong': '**{}**',
        'em': '*{}*',
        'code': '`{}`',
        'del': '~~{}~~'
    },
    'lists': {
        'ul': '- ',
        'ol': '1. ',
        'li': '  '  # 들여쓰기
    },
    'code_blocks': {
        'pre': '```\n{}\n```',
        'code': '`{}`'
    },
    'tables': {
        'table': '| {} |',
        'thead': '| {} |\n| --- |',
        'tbody': '| {} |'
    }
}
```

### 2.2 Confluence 특화 변환
```python
CONFLUENCE_SPECIFIC = {
    'macros': {
        'code': '```{}\n{}\n```',
        'info': '> **정보**: {}',
        'warning': '> **경고**: {}',
        'note': '> **참고**: {}'
    },
    'attachments': {
        'image': '![{}]({})',
        'file': '[{}]({})'
    },
    'links': {
        'internal': '[{}]({})',
        'external': '[{}]({})'
    }
}
```

## 3. HTML 파싱 로직

### 3.1 문서 구조 분석
```python
def parse_html_structure(html_content):
    """HTML 문서의 구조를 분석한다."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    structure = {
        'title': extract_title(soup),
        'headings': extract_headings(soup),
        'tables': extract_tables(soup),
        'code_blocks': extract_code_blocks(soup),
        'lists': extract_lists(soup),
        'links': extract_links(soup),
        'images': extract_images(soup)
    }
    
    return structure
```

### 3.2 요소별 추출 함수
```python
def extract_headings(soup):
    """헤딩 요소를 추출한다."""
    headings = []
    for i in range(1, 7):
        for heading in soup.find_all(f'h{i}'):
            headings.append({
                'level': i,
                'text': heading.get_text().strip(),
                'id': heading.get('id', '')
            })
    return headings

def extract_tables(soup):
    """표 요소를 추출한다."""
    tables = []
    for table in soup.find_all('table'):
        table_data = {
            'headers': [],
            'rows': []
        }
        
        # 헤더 추출
        thead = table.find('thead')
        if thead:
            for th in thead.find_all('th'):
                table_data['headers'].append(th.get_text().strip())
        
        # 행 추출
        tbody = table.find('tbody') or table
        for tr in tbody.find_all('tr'):
            row = []
            for td in tr.find_all(['td', 'th']):
                row.append(td.get_text().strip())
            if row:
                table_data['rows'].append(row)
        
        tables.append(table_data)
    
    return tables
```

## 4. Markdown 변환 로직

### 4.1 기본 변환 함수 (HTMLToMarkdownConverter.convert)
```python
async def convert(self, html_content: str, ...):
    """HTML을 Markdown으로 변환한다."""
    import time
    start_time = time.time()
    
    # 1단계: HTML 파싱
    self.logger.info(f"HTML→MD | step=parse | parser=html.parser | length={len(html_content)}")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 2단계: 요소별 변환
    markdown_parts = []
    elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                             'p', 'ul', 'ol', 'table', 'pre', 'blockquote',
                             'ac:structured-macro'])  # Confluence 매크로 포함
    
    for element in elements:
        converted = self._convert_element(element, preserve_structure)
        if converted.strip():
            markdown_parts.append(converted)
    
    # 3단계: 최종 조합 및 정리
    markdown = '\n\n'.join(markdown_parts)
    
    # 4단계: 성능 로깅
    processing_time = time.time() - start_time
    self.logger.info(f"HTML→MD | total={processing_time:.3f}s")
    
    return {"markdown": markdown, "processing_time_seconds": processing_time}
```

### 4.2 요소별 변환 함수
```python
def _convert_element(self, element: Tag, preserve_structure: bool) -> str:
    """개별 HTML 요소를 Markdown으로 변환한다."""
    tag = element.name
    
    # 헤딩 변환 (h1~h6)
    if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        return self._convert_heading(element)
    
    # 문단 변환 (인라인 요소 포함 처리)
    elif tag == 'p':
        return self._convert_paragraph(element)
    
    # 리스트 변환 (ul, ol)
    elif tag in ['ul', 'ol']:
        return self._convert_list(element)
    
    # 표 변환 (header + separator + rows)
    elif tag == 'table':
        return self._convert_table(element)
    
    # 코드 블록 변환 (언어 감지)
    elif tag == 'pre':
        return self._convert_code_block(element)
    
    # 인용문 변환
    elif tag == 'blockquote':
        return self._convert_blockquote(element)
    
    # Confluence 매크로 변환
    elif tag == 'ac:structured-macro':
        return self._convert_confluence_macro(element)
    
    # 기타 요소는 텍스트만 추출
    else:
        return element.get_text().strip()
```

### 4.3 고급 변환 함수
```python
def convert_paragraph(p_element):
    """문단을 변환하고 인라인 요소를 처리한다."""
    text = p_element.get_text()
    
    # 인라인 요소 처리
    for strong in p_element.find_all('strong'):
        text = text.replace(strong.get_text(), f"**{strong.get_text()}**")
    
    for em in p_element.find_all('em'):
        text = text.replace(em.get_text(), f"*{em.get_text()}*")
    
    for code in p_element.find_all('code'):
        text = text.replace(code.get_text(), f"`{code.get_text()}`")
    
    return text

def convert_table(table_element):
    """표를 Markdown 형식으로 변환한다."""
    rows = []
    
    # 헤더 행
    thead = table_element.find('thead')
    if thead:
        header_row = []
        for th in thead.find_all('th'):
            header_row.append(th.get_text().strip())
        rows.append('| ' + ' | '.join(header_row) + ' |')
        rows.append('| ' + ' | '.join(['---'] * len(header_row)) + ' |')
    
    # 데이터 행
    tbody = table_element.find('tbody') or table_element
    for tr in tbody.find_all('tr'):
        if tr.find('th'):  # 헤더 행인 경우
            continue
        row = []
        for td in tr.find_all('td'):
            row.append(td.get_text().strip())
        if row:
            rows.append('| ' + ' | '.join(row) + ' |')
    
    return '\n'.join(rows)
```

## 5. API 설계 (실제 구현)

### 5.1 HTMLToMarkdownConverter 클래스
```python
class HTMLToMarkdownConverter:
    async def convert(
        self, 
        html_content: str, 
        preserve_structure: bool = True, 
        save_to_file: bool = False, 
        output_path: str = None, 
        document_title: str = None
    ) -> Dict[str, Any]:
        """HTML을 Markdown으로 변환한다.
        
        Args:
            html_content: 변환할 HTML 내용 (필수)
            preserve_structure: 구조 보존 여부 (기본값: True)
            save_to_file: 파일로 저장 여부 (기본값: False)
            output_path: 저장할 파일 경로 (기본값: None, 자동 생성)
            document_title: 문서 제목 (로깅용)
        
        Returns:
            Dict[str, Any]: {
                "markdown": str,  # 변환된 Markdown 내용
                "metadata": dict,  # 변환 메타데이터
                "conversion_info": dict  # 변환 상세 정보
            }
        """
```

**주요 차이점**:
- MCP 도구가 아닌 일반 클래스 메서드
- `document_title` 매개변수 추가
- save_to_file 기본값: True → False

### 5.2 사용 예시
```python
# confluence_fetch 내부에서 사용되는 방식
from html_to_md.converter import HTMLToMarkdownConverter
converter = HTMLToMarkdownConverter()

# 1. transformer.py에서 기본 변환 (응답용)
converted = converter.convert(html_content, document_title=title)

# 2. server.py auto_pipeline에서 파일 저장용 변환
result = await converter.convert(
    html_content=html_content,
    preserve_structure=True,
    save_to_file=bool(md_output_path),
    output_path=md_output_path,
    document_title=document_title
)
```

**실제 사용 위치**:
- `confluence_fetch/transformer.py`: ConfluenceTransformer 내부
- `server.py`: confluence_fetch의 auto_pipeline 섹션

## 6. 메타데이터 처리

### 5.1 메타데이터 추출
```python
def extract_metadata(html_content, confluence_data):
    """HTML에서 메타데이터를 추출한다."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    metadata = {
        'title': extract_title_from_html(soup),
        'project': extract_project_from_labels(confluence_data.get('labels', [])),
        'type': extract_type_from_labels(confluence_data.get('labels', [])),
        'priority': extract_priority_from_labels(confluence_data.get('labels', [])),
        'status': extract_status_from_labels(confluence_data.get('labels', [])),
        'last_modified': confluence_data.get('version', {}).get('modified', ''),
        'confluence_url': confluence_data.get('_links', {}).get('webui', ''),
        'labels': confluence_data.get('labels', [])
    }
    
    return metadata
```

### 5.2 라벨 파싱
```python
def extract_project_from_labels(labels):
    """라벨에서 프로젝트명을 추출한다."""
    for label in labels:
        if label.startswith('specgate:project:'):
            return label.replace('specgate:project:', '')
    return 'unknown'

def extract_type_from_labels(labels):
    """라벨에서 문서 유형을 추출한다."""
    for label in labels:
        if label.startswith('specgate:type:'):
            return label.replace('specgate:type:', '')
    return 'unknown'
```

## 6. 품질 검증

### 6.1 변환 품질 검사
```python
def validate_conversion(original_html, converted_markdown):
    """변환 품질을 검증한다."""
    issues = []
    
    # 기본 검사
    if not converted_markdown.strip():
        issues.append("변환된 Markdown이 비어있습니다")
    
    # 헤딩 검사
    html_headings = count_headings_in_html(original_html)
    md_headings = count_headings_in_markdown(converted_markdown)
    if html_headings != md_headings:
        issues.append(f"헤딩 수 불일치: HTML {html_headings}개, MD {md_headings}개")
    
    # 표 검사
    html_tables = count_tables_in_html(original_html)
    md_tables = count_tables_in_markdown(converted_markdown)
    if html_tables != md_tables:
        issues.append(f"표 수 불일치: HTML {html_tables}개, MD {md_tables}개")
    
    return {
        'is_valid': len(issues) == 0,
        'issues': issues,
        'quality_score': calculate_quality_score(issues)
    }
```

## 7. 에러 처리

### 7.1 변환 실패 처리
```python
def handle_conversion_error(error, html_content):
    """변환 중 오류 발생 시 처리"""
    return {
        'status': 'error',
        'message': f'HTML→MD 변환 중 오류가 발생했습니다: {str(error)}',
        'fallback_content': html_content,  # 원본 HTML 보존
        'requires_manual_review': True
    }
```

### 7.2 부분 변환 처리
```python
def partial_conversion(html_content, failed_elements):
    """일부 요소 변환 실패 시 부분 변환 수행"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 실패한 요소 제거
    for element in failed_elements:
        element.decompose()
    
    # 나머지 요소 변환
    return convert_to_markdown(str(soup))
```

## 8. 성능 최적화

### 8.1 메모리 관리
```python
def convert_large_html(html_content):
    """대용량 HTML을 효율적으로 변환한다."""
    # 스트리밍 파싱 사용
    parser = BeautifulSoup(html_content, 'html.parser')
    
    # 청크 단위로 처리
    chunks = []
    for element in parser.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                                   'p', 'ul', 'ol', 'table', 'pre']):
        chunks.append(convert_element(element))
    
    return '\n\n'.join(chunks)
```

## 9. 테스트 케이스

### 9.1 정상 케이스
- 기본 HTML → Markdown 변환
- 복잡한 HTML 구조 → 구조화된 Markdown
- Confluence 특화 요소 → 표준 Markdown

### 9.2 에러 케이스
- 잘못된 HTML 형식 → 에러 처리
- 변환 실패 → 원본 HTML 보존
- 메모리 부족 → 스트리밍 처리

### 9.3 경계값 케이스
- 빈 HTML → 빈 Markdown
- 매우 큰 HTML → 청크 처리
- 특수 문자 포함 → 이스케이프 처리

## 10. 구현 우선순위

### 10.1 1단계 (핵심 기능)
- 기본 HTML→MD 변환
- 헤딩, 리스트, 코드블록 변환
- 메타데이터 추출

### 10.2 2단계 (고도화)
- 표 변환
- Confluence 특화 요소 처리
- 품질 검증

### 10.3 3단계 (확장)
- 성능 최적화
- 고급 에러 처리
- 변환 품질 개선
