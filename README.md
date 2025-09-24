# SpecGate

애자일 프로세스를 기반으로 한 설계 문서 품질 검증 및 CI 게이트 도구

## 🗂️ 프로젝트 구조 (2024.12.19 재정리)

```
SpecGate/
├── 📚 documentation/                     # 모든 문서 통합
│   ├── architecture/                     # 전체 시스템 설계
│   │   ├── Phase0_SpecGate_Overall.md
│   │   ├── Phase1_SpecGate_Input_Standardization.md
│   │   ├── Phase2_SpecGate_Intermediate_Generation.md
│   │   ├── Phase3_SpecGate_CI_Gate_Scoring.md
│   │   ├── DesignRuleSpec_Examples.json
│   │   └── assets/                       # 이미지/다이어그램
│   │       ├── images/                   # PNG, SVG 파일
│   │       └── diagrams/                 # 시퀀스 다이어그램
│   ├── user-stories/                     # 세부 유저스토리/설계
│   │   ├── US-000-mcp-server-*.md
│   │   ├── US-001-confluence-fetch*.md
│   │   ├── US-002-speclint*.md
│   │   └── US-003-html-to-md*.md
│   ├── project-management/               # 프로젝트 관리
│   │   ├── epics/                        # Epic 문서
│   │   ├── sprints/                      # 스프린트 계획
│   │   └── qa/                          # 품질 보증
│   └── templates/                        # 템플릿 및 가이드
│       ├── standards/                    # 표준 설계 문서
│       └── UserStory_Template.md
├── 💻 development/                       # 모든 개발 코드
│   ├── mcp-server/                       # MCP 서버 (Python)
│   │   ├── confluence_fetch/             # Confluence API 연동 모듈
│   │   ├── speclint_lint/                # 품질 검사 모듈
│   │   ├── html_to_md/                   # HTML→MD 변환 모듈
│   │   ├── workflows/                    # HITL 워크플로우
│   │   ├── integrations/                 # GitHub 연동
│   │   ├── tests/                        # 테스트 코드
│   │   ├── server.py                     # 메인 서버
│   │   ├── requirements.txt              # Python 의존성
│   │   └── README.md                     # 서버 사용법
│   └── rules/                           # SpecLint 규칙 정의
│       └── speclint-rules.yaml
├── 🎥 presentations/                     # 발표 자료
│   ├── SpecGate_keynote.pdf
│   └── SpecGate_keynote_jpeg/
├── 📋 confluence-guide/                  # Confluence 가이드
│   ├── authoring-guide.md
│   └── confluence-policy.md
└── 📄 README.md                          # 프로젝트 개요
```

## 📂 폴더별 설명

### 📚 documentation/
- **architecture/**: 전체 시스템 아키텍처 및 Phase별 설계
- **user-stories/**: 세부 기능별 유저스토리 및 설계 문서
- **project-management/**: Epic, 스프린트, QA 등 프로젝트 관리
- **templates/**: 표준 문서 템플릿 및 가이드

### 💻 development/
- **mcp-server/**: FastMCP 기반 Python 서버 (메인 개발 영역)
  - `confluence_fetch/`: Confluence API 연동 모듈
  - `speclint_lint/`: 문서 품질 검사 엔진
  - `html_to_md/`: HTML→Markdown 변환기
  - `workflows/`: HITL 워크플로우 관리
  - `integrations/`: GitHub API 연동
  - `tests/`: 단위/통합/E2E 테스트
- **rules/**: SpecLint 품질 검사 규칙 정의

### 🎥 presentations/
- 프로젝트 발표 자료 (Keynote PDF, 이미지)

### 📋 confluence-guide/
- Confluence 문서 작성 가이드 및 정책

## 🚀 개발 시작하기

### 1. 환경변수 설정

Cursor의 `mcp.json`에 다음 설정을 추가하세요:

```json
{
  "mcpServers": {
    "SpecGate": {
      "command": "/path/to/SpecGate/development/mcp-server/venv/bin/python",
      "args": ["/path/to/SpecGate/development/mcp-server/server.py"],
      "env": {
        "CONFLUENCE_DOMAIN": "your-domain.atlassian.net",
        "CONFLUENCE_EMAIL": "your-email@example.com", 
        "CONFLUENCE_API_TOKEN": "your-api-token",
        "GITHUB_TOKEN": "your-github-token",
        "GITHUB_OWNER": "your-github-username",
        "GITHUB_REPO": "your-repository-name",
        "CLIENT_WORK_DIR": "/path/to/your/project"
      }
    }
  }
}
```

**⚠️ 중요**: 
- `CLIENT_WORK_DIR`을 설정하면 해당 프로젝트 폴더에 `.specgate/` 디렉토리가 생성되어 모든 파일이 저장됩니다.
- GitHub 관련 환경변수는 HITL(Human-in-the-Loop) 워크플로우와 이슈 자동 생성 기능에 필요합니다.

### 2. MCP 서버 실행
```bash
cd development/mcp-server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

### 3. 주요 MCP 도구들
- `confluence_fetch`: Confluence 문서 수집 및 HTML 저장
- `convert_saved_html`: 저장된 HTML을 Markdown으로 변환
- `check_document_quality`: 저장된 MD 파일의 품질 검사
- `speclint_lint`: 문서 내용 직접 품질 검사
- `html_to_md`: HTML 내용 직접 변환

### 4. 단계별 워크플로우
```
1. confluence_fetch(label="API") 
   → HTML 원본 저장 (data/html_files/)

2. convert_saved_html(html_file_path="...") 
   → Markdown 변환 (data/markdown_files/)

3. check_document_quality(markdown_file_path="...") 
   → 품질 검사 (data/quality_reports/)
```
