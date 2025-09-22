# Sprint #1 데모 시나리오

## 데모 개요
**목표**: Phase 1 완전 구현 기능 시연 (MCP Server → Confluence 수집 → HTML→MD 변환 → 품질 검사)  
**시간**: 15분  
**환경**: Cursor IDE + SpecGate MCP Server

## 데모 준비사항

### 1. Cursor IDE 설정
```bash
# 1. 새로운 프로젝트 폴더 생성
mkdir SpecGate-Demo
cd SpecGate-Demo

# 2. MCP 설정 파일 생성
cat > .cursorrules << 'EOF'
# SpecGate MCP Server 연결 설정
EOF

# 3. MCP 서버 설정 파일 생성
cat > mcp.json << 'EOF'
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
EOF
```

### 2. 테스트 데이터 확인
- Confluence에 "design" 라벨이 붙은 설계 문서 2-3개 준비
- HTML 원본 저장 경로: `SpecGate/data/html_files/` (프로젝트 폴더 내)
- Markdown 변환 저장 경로: `SpecGate/data/md_files/` (프로젝트 폴더 내)
- 품질 리포트 저장 경로: `SpecGate/data/quality_reports/` (프로젝트 폴더 내)

## 데모 시나리오

### 1단계: MCP Server 연결 및 기본 테스트 (3분)
**목표**: SpecGate MCP Server가 정상적으로 연결되었는지 확인

**데모 방법**:
1. Cursor IDE 재시작
2. 하단 상태바에서 MCP 서버 연결 상태 확인
3. Cursor IDE 채팅에서 다음 프롬프트 입력:

```
SpecGate MCP Server에 연결된 도구들을 보여줘
```

**예상 결과**:
- SpecGate MCP Server 연결 성공
- 3개 도구 등록 확인: `confluence_fetch`, `speclint_lint`, `html_to_md`
- 서버 이름: "SpecGate Server 🚀"

### 2단계: Confluence 문서 수집 (4분)
**목표**: 실제 Confluence에서 설계 문서를 수집하고 HTML 원본 저장

**데모 방법**:
Cursor IDE 채팅에서 다음 프롬프트를 순서대로 입력:

```
1. Confluence에서 "design" 라벨이 붙은 문서 3개를 수집해줘.
```

**예상 결과**:
- 3개 설계 문서 수집 성공
- HTML 원본 파일이 `SpecGate/data/html_files/design_YYYYMMDD_HHMMSS/` 경로에 저장 (프로젝트 폴더 내)
- 각 문서의 제목, 라벨, 수정일 등 메타데이터 출력
- `SpecGate/data` 폴더가 자동으로 생성됨

### 3단계: HTML→MD 변환 (3분)
**목표**: 수집한 HTML 문서를 Markdown으로 변환

**데모 방법**:
Cursor IDE 채팅에서 다음 프롬프트 입력:

```
2. 방금 수집한 문서 중 "SpecGate 보안 설계서"를 Markdown으로 변환해줘.
```

**예상 결과**:
- HTML이 완벽하게 Markdown으로 변환
- 헤딩, 리스트, 표, 코드블록 등 구조 보존
- Markdown 파일이 `SpecGate/data/md_files/` 경로에 저장 (프로젝트 폴더 내)
- 변환된 Markdown 내용이 채팅에 표시됨

### 4단계: 문서 품질 검사 (3분)
**목표**: 변환된 Markdown 문서의 품질을 검사하고 점수 계산

**데모 방법**:
Cursor IDE 채팅에서 다음 프롬프트 입력:

```
3. 방금 변환한 Markdown 내용의 품질을 검사해줘. 점수와 개선사항도 알려줘.
```

**예상 결과**:
- 품질 점수 75-95점 (설계 문서 특성상)
- 위반 사항 및 개선 제안 출력
- 품질 등급에 따른 처리 결과 안내 (자동승인/HITL검토/필수수정)

### 5단계: 전체 파이프라인 자동화 (2분)
**목표**: 전체 워크플로우를 한 번에 실행하여 자동화 확인

**데모 방법**:
Cursor IDE 채팅에서 다음 프롬프트 입력:

```
4. 전체 파이프라인을 한 번에 실행해줘. Confluence에서 문서를 수집하고, HTML을 Markdown으로 변환하고, 품질 검사까지 모두 자동으로 해줘.
```

**예상 결과**:
- 전체 파이프라인이 자동으로 실행
- 처리된 문서 수, 성공률, 평균 품질 점수 출력
- 에러 발생 시 적절한 에러 메시지 표시

## 📝 데모 실행 방법

### Cursor IDE에서 MCP 도구 사용하기

**기본 원리**: Cursor IDE는 MCP 서버에 연결되면, 채팅에서 자연어로 요청하면 자동으로 적절한 MCP 도구를 호출합니다.

**실행 순서**:
1. **Cursor IDE 재시작** → MCP 서버 연결
2. **채팅에서 자연어로 요청** → AI가 MCP 도구 자동 호출
3. **결과 확인** → 채팅에 결과 표시 + 파일 저장

**예시**:
```
사용자: "Confluence에서 design 라벨 문서 3개 수집해줘"
↓
AI: confluence_fetch 도구 호출
↓
결과: 수집된 문서 정보 + HTML 파일 저장 완료
```

### 🎯 데모할 핵심 기능

### ✅ 완전 구현된 기능들
1. **MCP Server 기본 구조** (US-000)
   - FastMCP 서버 완전 동작
   - 3개 도구 등록 및 연동 (`confluence_fetch`, `speclint_lint`, `html_to_md`)
   - 데이터 전달 구조 완벽 구현

2. **Confluence 문서 수집** (US-001)
   - Confluence API 완전 연동
   - 라벨 기반 필터링 (CQL 쿼리)
   - HTML 원본 자동 저장
   - SpecGate 형식 변환

3. **문서 품질 검사** (US-002)
   - SpecLint 완전 구현
   - 0-100점 품질 점수 계산
   - HITL 프로세스 (GitHub Issue 연동)
   - 배치 처리 및 에러 처리

4. **HTML→MD 변환** (US-003)
   - 완벽한 HTML→Markdown 변환
   - 헤딩, 리스트, 표, 코드블록 지원
   - Confluence 특화 요소 처리
   - 파일 저장 기능

### 🎯 데모 성공 기준
- [x] MCP Server 정상 연결
- [x] Confluence 문서 수집 성공
- [x] HTML→MD 변환 완벽 동작
- [x] 품질 검사 및 점수 계산 정상
- [x] 전체 파이프라인 자동화 동작
- [x] 실제 Confluence 문서에서 테스트 성공

## 데모 후 질문 대응

### Q: 실제 프로덕션에서 사용할 수 있나요?
**A**: 네, 현재 구현된 기능들은 실제 프로덕션 환경에서 사용 가능합니다. Confluence API 연동, HTML→MD 변환, 품질 검사 모두 실제 데이터로 테스트를 완료했습니다.

### Q: 다른 Confluence 인스턴스에서도 동작하나요?
**A**: 네, 환경변수만 변경하면 다른 Confluence 인스턴스에서도 동작합니다. `CONFLUENCE_DOMAIN`, `CONFLUENCE_EMAIL`, `CONFLUENCE_API_TOKEN`만 설정하면 됩니다.

### Q: 품질 검사 기준을 커스터마이징할 수 있나요?
**A**: 네, `speclint/rules.py` 파일에서 품질 검사 규칙과 점수 기준을 자유롭게 수정할 수 있습니다.

### Q: Cursor IDE에서 직접 MCP 도구를 호출할 수 있나요?
**A**: 네, 자연어로 요청하면 AI가 자동으로 적절한 MCP 도구를 호출합니다. 예: "Confluence 문서 수집해줘" → `confluence_fetch` 도구 자동 호출

### Q: Phase 2는 언제 구현되나요?
**A**: Sprint 2에서 Phase 2 (설계 규칙 추출 및 DesignRuleSpec 생성)를 구현할 예정입니다.

### Q: 데모 중 에러가 발생하면 어떻게 하나요?
**A**: 
1. Cursor IDE 하단 상태바에서 MCP 서버 연결 상태 확인
2. 로그 파일 확인: `SpecGate/logs/specgate.log`
3. 환경변수 설정 확인
4. 필요시 Cursor IDE 재시작

---

**작성일**: 2024-09-18  
**작성자**: Product Owner (Sarah)  
**버전**: 1.0
