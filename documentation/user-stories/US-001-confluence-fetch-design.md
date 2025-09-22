# US-001: Confluence 문서 수집 기능 설계 문서

## 1. 기능 개요

### 1.1 목적
Confluence API를 통해 설계 문서를 수집하고 HTML 원본을 파일로 저장하여 추후 단계별 처리가 가능한 워크플로우를 제공한다.

### 1.2 핵심 기능 (업데이트됨)
- **리팩토링된 모듈 구조**: ConfluenceService, ConfluenceAPIClient, ConfluenceDataTransformer 분리
- **HTML 원본 저장**: HTML 파일을 로컬에 저장하여 중간 데이터 보존 (기본 경로: `data/html_files/`)
- **단계별 워크플로우**: 수집 → 변환 → 검사 단계를 독립적으로 실행 가능
- **CQL 기반 검색**: 라벨 필터링을 위한 정확한 쿼리
- **자연스러운 대화 지원**: "가져온 문서를 변환해줘" 같은 요청 가능
- **SpecGate 형식 변환**: 일관된 데이터 구조 제공

## 2. 아키텍처 설계

### 2.1 새로운 모듈 기반 아키텍처
```
AI Client → SpecGate MCP Server → Confluence API
                ↓
         [confluence_fetch(save_html=True)]
                ↓
    ConfluenceService → ConfluenceAPIClient → Confluence API
                ↓                ↓
    ConfluenceDataTransformer    HTML 원본 저장 (html_files/)
                ↓
         [SpecGate 형식 변환]
```

### 2.2 환경변수 통합
```bash
# .env (SpecGate MCP Server용 - 모든 설정 포함)
# SpecGate MCP Server 설정
SPECGATE_LOG_LEVEL=INFO
SPECGATE_PORT=8000

# Confluence 설정 (Confluence MCP Server에서도 사용)
CONFLUENCE_DOMAIN=company.atlassian.net
CONFLUENCE_EMAIL=user@company.com
CONFLUENCE_API_TOKEN=ATATT3xFfGF0...
```

### 2.3 새로운 API 인터페이스 (업데이트됨)
```python
# 기본 문서 수집 (HTML 원본 저장)
@mcp.tool()
async def confluence_fetch(
    label: str, 
    space_key: str | None = None, 
    limit: int = 10,
    save_html: bool = True  # 새로 추가된 매개변수
) -> dict:
    """Confluence에서 문서를 수집하고 HTML 원본을 저장"""
    return await confluence_service.fetch_documents(label, space_key, limit, save_html)
```

## 3. API 설계

### 3.1 CQL 기반 검색
```python
# 라벨 기반 검색 쿼리
CQL_QUERIES = {
    'label_search': 'type = "page" AND label = "{label}"',
    'space_label_search': 'type = "page" AND space.key = "{space_key}" AND label = "{label}"',
    'recent_pages': 'type = "page" AND created >= "{date}" AND label = "{label}"'
}
```

### 3.2 SpecGate 형식 변환
```python
# Confluence MCP Server 응답 → SpecGate 형식
def transform_to_specgate_format(confluence_response):
    return {
        "id": confluence_response.get("id"),
        "title": confluence_response.get("title"),
        "content": confluence_response.get("content"),  # 이미 Markdown
        "space_key": confluence_response.get("space", {}).get("key"),
        "space_name": confluence_response.get("space", {}).get("name"),
        "url": confluence_response.get("_links", {}).get("webui"),
        "labels": confluence_response.get("labels", []),
        "created": confluence_response.get("version", {}).get("created"),
        "modified": confluence_response.get("version", {}).get("modified"),
        "version": confluence_response.get("version", {}).get("number", 1)
    }
```

## 3. 데이터 구조

### 3.1 입력 데이터
```python
# Confluence API 응답 구조
ConfluencePage = {
    'id': str,
    'title': str,
    'body': {
        'storage': str  # HTML content
    },
    'version': {
        'number': int,
        'created': str,
        'modified': str
    },
    'labels': List[str],
    'space': {
        'key': str,
        'name': str
    }
}
```

### 3.2 출력 데이터
```python
# 변환된 문서 구조
ProcessedDocument = {
    'metadata': {
        'id': str,
        'title': str,
        'project': str,
        'type': str,
        'priority': str,
        'status': str,
        'last_modified': str,
        'confluence_url': str,
        'labels': List[str]
    },
    'content': {
        'html': str,
        'markdown': str
    },
    'extracted_info': {
        'headings': List[str],
        'tables': List[dict],
        'code_blocks': List[dict]
    }
}
```

## 4. HTML→MD 변환 규칙

### 4.1 변환 매핑
```python
CONVERSION_RULES = {
    'headings': {
        'h1': '# ',
        'h2': '## ',
        'h3': '### ',
        'h4': '#### '
    },
    'tables': {
        'preserve_structure': True,
        'markdown_format': 'pipe',
        'header_detection': True
    },
    'code_blocks': {
        'preserve_language': True,
        'fence_format': '```',
        'indent_preservation': True
    },
    'lists': {
        'unordered': '- ',
        'ordered': '1. ',
        'preserve_nesting': True
    }
}
```

### 4.2 메타데이터 추출
```python
METADATA_EXTRACTION = {
    'title_pattern': r'^#\s*(.+?)\s*$',
    'project_pattern': r'specgate:project:(.+)',
    'type_pattern': r'specgate:type:(.+)',
    'priority_pattern': r'specgate:priority:(.+)',
    'status_pattern': r'specgate:status:(.+)'
}
```

## 5. 기본 에러 처리
- API 연결 실패 시 Mock 데이터 사용
- HTML 파싱 오류 시 원본 HTML 보존
- 변환 실패 시 기본 텍스트 추출
