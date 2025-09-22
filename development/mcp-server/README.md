# SpecGate MCP Server

SpecGate MCP Server는 Phase 1의 Confluence 문서 처리 기능을 제공하는 FastMCP 2.0 기반 서버입니다.

## 기능

- **confluence.fetch**: Confluence 문서 수집 및 HTML→MD 변환
- **speclint.lint**: 문서 품질 검사 및 점수 계산  
- **html.to_md**: HTML을 Markdown으로 변환

## 설치 및 실행

### 1. 의존성 설치
```bash
# requirements.txt 사용
pip install -r requirements.txt

# 또는 pyproject.toml 사용
pip install -e .
```

### 2. 환경 변수 설정
Cursor의 `mcp.json`에 Confluence API 설정을 추가하세요:
```json
{
  "mcpServers": {
    "specgate": {
      "command": "python",
      "args": ["/path/to/specgate/mcp-server/server.py"],
      "env": {
        "CONFLUENCE_DOMAIN": "your-domain.atlassian.net",
        "CONFLUENCE_EMAIL": "your-email@example.com",
        "CONFLUENCE_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

### 3. 서버 실행
```bash
# STDIO 모드 (개발용)
python server.py

# HTTP 모드
fastmcp run server.py --transport http --port 8000
```

### 4. 테스트 실행
```bash
pytest tests/ -v
```

## 아키텍처

- **FastMCP 2.0**: 현대적인 MCP 서버 프레임워크
- **Context 기반**: 로깅, 진행상황 보고, 사용자 상호작용
- **미들웨어**: 로깅, 에러처리, 인증 지원
- **표준화된 데이터 구조**: 도구 간 일관된 데이터 전달

## 개발 상태

- ✅ 기본 서버 구조 구축
- ✅ 3개 핵심 도구 구현 (기본 구조)
- ✅ 데이터 구조 표준화
- ✅ 테스트 코드 작성
- 🔄 실제 API 연동 (향후 구현 예정)
