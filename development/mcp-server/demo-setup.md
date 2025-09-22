# SpecGate MCP Server 데모 설정 가이드

## 🚀 빠른 시작

### 1. Cursor IDE에서 새 프로젝트 생성
```bash
mkdir SpecGate-Demo
cd SpecGate-Demo
```

### 2. MCP 서버 설정 파일 복사
```bash
# SpecGate 프로젝트에서 데모용 설정 파일 복사
cp /Users/yy.cho/Desktop/클테코/SpecGate/development/mcp-server/demo-mcp.json ./mcp.json
```

### 3. 환경변수 설정
`mcp.json` 파일에서 다음 값들을 실제 값으로 변경:
```json
{
  "mcpServers": {
    "SpecGate": {
      "command": "/Users/yy.cho/Desktop/클테코/SpecGate/development/mcp-server/venv/bin/python",
      "args": ["/Users/yy.cho/Desktop/클테코/SpecGate/development/mcp-server/server.py"],
      "env": {
        "CONFLUENCE_DOMAIN": "your-domain.atlassian.net",
        "CONFLUENCE_EMAIL": "your-email@company.com",
        "CONFLUENCE_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

### 4. Cursor IDE 재시작
- Cursor IDE를 완전히 종료
- 다시 실행하여 MCP 서버 연결

### 5. MCP 서버 연결 확인
Cursor IDE에서 MCP 서버가 정상적으로 연결되었는지 확인:
- 하단 상태바에서 MCP 서버 상태 확인
- 3개 도구가 등록되었는지 확인: `confluence_fetch`, `speclint_lint`, `html_to_md`

## 🎯 데모 실행

### 1단계: Confluence 문서 수집
```bash
# Cursor IDE에서 실행
confluence_fetch(label="design", limit=3, save_html=true)
```

### 2단계: HTML→MD 변환
```bash
# Cursor IDE에서 실행 (HTML 내용 직접 변환)
html_to_md(html_content="<h1>제목</h1><p>내용</p>", save_to_file=true)
```

### 3단계: 품질 검사
```bash
# Cursor IDE에서 실행 (Markdown 내용 직접 검사)
speclint_lint(content="# 제목\n\n문서 내용...", check_type="full")
```

## 📁 생성되는 파일들

### HTML 원본 저장
- 경로: `SpecGate/data/html_files/design_YYYYMMDD_HHMMSS/` (프로젝트 폴더 내)
- 파일: `문서명.html`
- 자동 생성: `data` 폴더가 없으면 자동으로 생성됩니다

### Markdown 변환 저장
- 경로: `SpecGate/data/markdown_files/` (프로젝트 폴더 내)
- 파일: `confluence_converted.md`

### 품질 검사 결과
- 경로: `SpecGate/data/quality_reports/` (프로젝트 폴더 내)
- 파일: `quality_report_YYYYMMDD_HHMMSS.md`

## 🔧 문제 해결

### MCP 서버 연결 실패
1. Python 경로 확인: `which python`
2. 서버 파일 경로 확인: `/Users/yy.cho/Desktop/클테코/SpecGate/development/mcp-server/server.py`
3. Cursor IDE 재시작

### Confluence API 연결 실패
1. 환경변수 확인: `CONFLUENCE_DOMAIN`, `CONFLUENCE_EMAIL`, `CONFLUENCE_API_TOKEN`
2. API 토큰 유효성 확인
3. 네트워크 연결 확인

### 파일 경로 오류
1. 프로젝트 폴더 내 경로 확인: `SpecGate/data/` 경로가 올바른지 확인
2. 디렉토리 생성: `SpecGate/data` 폴더가 자동 생성되는지 확인

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 로그 파일: `SpecGate/logs/specgate.log` (프로젝트 폴더 내)
2. 에러 메시지: Cursor IDE 하단 상태바
3. 테스트 실행: `python test_us003_integration.py`
