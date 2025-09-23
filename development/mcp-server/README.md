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

#### 필수 환경변수 (Confluence API)
Cursor의 `mcp.json`에 다음 설정을 추가하세요:

```json
{
  "mcpServers": {
    "SpecGate": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/specgate/mcp-server/server.py"],
      "env": {
        "CONFLUENCE_DOMAIN": "your-domain.atlassian.net",
        "CONFLUENCE_EMAIL": "your-email@example.com",
        "CONFLUENCE_API_TOKEN": "your-api-token",
        "CLIENT_WORK_DIR": "/path/to/your/project"
      }
    }
  }
}
```

#### 환경변수 설명

| 변수명 | 필수여부 | 설명 | 예시 |
|--------|----------|------|------|
| `CONFLUENCE_DOMAIN` | ✅ 필수 | Confluence 도메인 | `company.atlassian.net` |
| `CONFLUENCE_EMAIL` | ✅ 필수 | Confluence 계정 이메일 | `user@company.com` |
| `CONFLUENCE_API_TOKEN` | ✅ 필수 | Confluence API 토큰 | `ATATT3xFfGF... |
| `CLIENT_WORK_DIR` | 🔧 권장 | 파일 저장 위치 | `/Users/user/my-project` |

#### 파일 저장 위치 설정

**`CLIENT_WORK_DIR` 환경변수**를 설정하지 않으면 SpecGate가 실행되는 디렉토리에 파일이 저장됩니다.

**권장 설정**: 프로젝트별로 파일을 저장하려면 `CLIENT_WORK_DIR`을 설정하세요:

```json
"CLIENT_WORK_DIR": "/Users/username/my-project"
```

그러면 다음 구조로 파일이 저장됩니다:
```
/Users/username/my-project/
└── .specgate/
    ├── data/
    │   ├── html_files/        # Confluence 원본 HTML
    │   ├── md_files/          # 변환된 Markdown
    │   └── quality_reports/   # 품질 분석 리포트
    └── logs/
        └── specgate.log       # 실행 로그
```

#### Confluence API 토큰 생성 방법

1. **Confluence 접속**: `https://your-domain.atlassian.net`
2. **계정 설정**: 우측 상단 프로필 → `계정 설정`
3. **보안**: `보안` 탭 → `API 토큰`
4. **토큰 생성**: `API 토큰 만들기` → 레이블 입력 → `만들기`
5. **토큰 복사**: 생성된 토큰을 안전한 곳에 보관

⚠️ **보안 주의사항**: API 토큰은 외부에 노출되지 않도록 주의하세요.

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
