# US-003: HTML→MD 변환 기능 설계 문서

## 1. 기능 개요

### 1.1 목적
Confluence에서 수집한 HTML 문서를 Markdown 형식으로 변환하여 Phase 2에서 설계 규칙 추출이 가능한 표준화된 문서를 생성한다.

### 1.2 핵심 기능 (업데이트됨)
- **리팩토링된 모듈 구조**: HTMLToMarkdownConverter, HTMLParser, HTMLValidator 분리
- **HTML 내용 직접 변환**: html_to_md 도구 (기본 저장 활성화)
- **파일 저장 기능**: 변환된 Markdown을 파일로 저장 (기본 경로: `data/markdown_files/`)
- **메타데이터 보존**: 소스 파일 경로 추적
- **변환 품질 검증**: 변환 성공률 및 정확도 검사

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

### 4.1 기본 변환 함수
```python
def convert_to_markdown(html_content):
    """HTML을 Markdown으로 변환한다."""
    soup = BeautifulSoup(html_content, 'html.parser')
    markdown_parts = []
    
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                                 'p', 'ul', 'ol', 'table', 'pre', 'blockquote']):
        markdown_parts.append(convert_element(element))
    
    return '\n\n'.join(markdown_parts)
```

### 4.2 요소별 변환 함수
```python
def convert_element(element):
    """개별 HTML 요소를 Markdown으로 변환한다."""
    tag = element.name
    
    if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        level = int(tag[1])
        return f"{'#' * level} {element.get_text().strip()}"
    
    elif tag == 'p':
        return convert_paragraph(element)
    
    elif tag in ['ul', 'ol']:
        return convert_list(element)
    
    elif tag == 'table':
        return convert_table(element)
    
    elif tag == 'pre':
        return convert_code_block(element)
    
    elif tag == 'blockquote':
        return convert_blockquote(element)
    
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

## 5. API 설계 (새로 추가됨)

### 5.1 html_to_md 인터페이스 (HTML 내용 직접 변환)
```python
@mcp.tool()
async def html_to_md(
    html_content: str,
    preserve_structure: bool = True,
    save_to_file: bool = True,
    output_path: str = None
) -> dict:
    """HTML 내용을 Markdown 형식으로 변환
    
    Args:
        html_content: 변환할 HTML 내용 (필수)
        preserve_structure: 구조 보존 여부 (기본값: True)
        save_to_file: 파일로 저장 여부 (기본값: False)
        output_path: 저장할 파일 경로 (기본값: None, 자동 생성)
    
    Returns:
        dict: {
            "markdown": str,
            "metadata": dict,
            "conversion_info": dict
        }
    """
    return await html_converter.convert(html_content, preserve_structure, save_to_file, output_path)
```

### 5.3 사용 예시
```python
# 방법 1: HTML 내용 직접 변환
result1 = await html_to_md("""
<h1>API 설계서</h1>
<h2>설계 규칙</h2>
<p><strong>RULE-API-001</strong> (MUST): 모든 API는 RESTful 원칙을 따라야 한다</p>
""", save_to_file=True)

# 방법 2: 저장된 HTML 파일 변환 (새로운 워크플로우)
result2 = await convert_saved_html("html_files/API_20241219_143022/API_Design_1.html")
```

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
