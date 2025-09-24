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

# 3. MCP 서버 설정 파일 생성 (Confluence + GitHub 환경변수 포함)
cat > mcp.json << 'EOF'
{
  "mcpServers": {
    "SpecGate": {
      "command": "/Users/yy.cho/Desktop/클테코/SpecGate/development/mcp-server/venv/bin/python",
      "args": ["/Users/yy.cho/Desktop/클테코/SpecGate/development/mcp-server/server.py"],
      "env": {
        "CONFLUENCE_DOMAIN": "your-domain.atlassian.net",
        "CONFLUENCE_EMAIL": "your-email@company.com",
        "CONFLUENCE_API_TOKEN": "your-api-token",
        "GITHUB_TOKEN": "your-github-pat",
        "GITHUB_OWNER": "your-github-username",
        "GITHUB_REPO": "your-test-repo"
      }
    }
  }
}
EOF
```

### 2. 테스트 데이터 확인
- Confluence에 "design" 라벨이 붙은 설계 문서 2-3개 준비
- HTML 원본 저장 경로: `.specgate/data/html_files/` (프로젝트 폴더 내)
- Markdown 변환 저장 경로: `.specgate/data/md_files/` (프로젝트 폴더 내)
- 품질 리포트 저장 경로: `.specgate/data/quality_reports/` (프로젝트 폴더 내)

## 데모 시나리오

### 1단계: MCP Server 연결 및 기본 테스트
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

### 2단계: 자동 파이프라인 실행 (테스트 문서 활용)
**목표**: 로컬 테스트 문서들로 자동 파이프라인 전체 과정 시연

**데모 방법**:
Cursor IDE 채팅에서 다음 프롬프트 입력:

```
documentation/templates/test-documents/ 폴더의 모든 테스트 문서들을 품질 검사해줘.
```

**예상 결과** (자동으로 순차 실행):
1. **5개 테스트 문서 품질 검사 완료**:
   - **01-API-Design-Perfect.md**: 95점 (자동승인) ✅
   - **02-Architecture-Design-TitleError.md**: 75점 (HITL 검토 필요) ⚠️
   - **03-Data-Model-Design-MissingRules.md**: 65점 (필수수정) ❌
   - **04-Security-Design-MissingCode.md**: 45점 (필수수정) ❌
   - **05-Performance-Design-MissingHistory.md**: 55점 (필수수정) ❌

2. **자동 처리 결과**:
   - 품질 등급별 자동 분류 완료
   - 70점 미만 문서들(3개)에 대해 GitHub Issue 자동 생성
   - 각 이슈에 품질 점수, 위반 사항, 수정 가이드 포함
   - 처리 시간 및 성능 통계 출력

**생성되는 파일들**:
- 품질 리포트: `.specgate/data/quality_reports/quality_report_{score}pts_{level}_{타임스탬프}.json`
- GitHub Issue: 자동 생성된 이슈 링크 출력

### 3단계: HITL 프로세스 시연
**목표**: 70-89점 문서의 HITL(Human-in-the-Loop) 검토 과정 시연

**데모 방법**:
Cursor IDE 채팅에서 다음 프롬프트 입력:

```
"02-Architecture-Design-TitleError.md" 문서의 품질 문제를 수정해줘.
```

**예상 결과**:
- 제목 오류 감지: "잘못된 제목" → "SpecGate 아키텍처 설계서"
- 수정된 문서로 재검사: 75점 → 90점
- 자동승인 처리 완료

### 4단계: Confluence 연동 시연 (선택사항)
**목표**: 실제 Confluence 환경에서 자동 파이프라인 실행

**데모 방법**:
Cursor IDE 채팅에서 다음 프롬프트 입력:

```
Confluence에서 "design" 라벨이 붙은 문서 3개를 수집하고, 자동으로 전체 파이프라인을 실행해줘.
```

**예상 결과**:
- 3개 설계 문서 수집 성공
- HTML 원본 자동 저장
- HTML→Markdown 자동 변환
- 품질 검사 및 점수 계산 자동 실행
- 품질 등급별 자동 처리 완료

**생성되는 파일들**:
- HTML 원본: `.specgate/data/html_files/{제목}_{타임스탬프}.html`
- Markdown: `.specgate/data/md_files/{제목}_{타임스탬프}.md`
- 품질 리포트: `.specgate/data/quality_reports/quality_report_{score}pts_{level}_{타임스탬프}.json`

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

2. **자동 파이프라인** (핵심 혁신!)
   - **한 번의 요청으로 전체 워크플로우 자동 실행**
   - Confluence 수집 → HTML→MD 변환 → 품질검사 → GitHub Issue 생성
   - `auto_pipeline=True` 옵션으로 완전 자동화
   - 에러 발생 시 적절한 롤백 및 복구

3. **Confluence 문서 수집** (US-001)
   - Confluence API 완전 연동
   - 라벨 기반 필터링 (CQL 쿼리)
   - HTML 원본 자동 저장
   - SpecGate 형식 변환

4. **문서 품질 검사** (US-002)
   - SpecLint 완전 구현
   - 0-100점 품질 점수 계산
   - HITL 프로세스 (GitHub Issue 연동)
   - 배치 처리 및 에러 처리

5. **HTML→MD 변환** (US-003)
   - 완벽한 HTML→Markdown 변환
   - 헤딩, 리스트, 표, 코드블록 지원
   - Confluence 특화 요소 처리
   - 파일 저장 기능

6. **다양한 품질 등급 처리**
   - **Perfect 문서**: 95점 (자동승인)
   - **Title Error**: 75점 (HITL 검토)
   - **Missing Rules**: 65점 (GitHub Issue 생성)
   - **Missing Code**: 45점 (GitHub Issue 생성)
   - **Missing History**: 55점 (GitHub Issue 생성)

### 🎯 데모 성공 기준
- [x] MCP Server 정상 연결
- [x] **자동 파이프라인 완전 동작** (핵심!)
- [x] Confluence 문서 수집 성공
- [x] HTML→MD 변환 완벽 동작
- [x] 품질 검사 및 점수 계산 정상
- [x] **GitHub Issue 자동 생성** 성공
- [x] **다양한 품질 등급 처리** 시연
- [x] **HITL 프로세스** 검토 과정 시연
- [x] 실제 Confluence 문서에서 테스트 성공

## 📌 스프린트 1 마감 요약

- **자동 파이프라인 HITL 연동 추가**: 품질 점수 기준(≥90/70–89/<70)에 따라 GitHub Issue 자동 생성 연동 완료. `confluence_fetch(..., auto_pipeline=True)` 경로에서도 이슈 생성.
- **옵션 추가**: `auto_create_github_issues`(기본값 True)로 자동 파이프라인 내 이슈 생성 On/Off 가능.
- **파일 이름/타임스탬프 정렬**:
  - 동일 제목 재수집 시 기존 MD 타임스탬프 파일 정리(HTML과 동일 정책).
  - HTML/MD/quality_reports 파일명이 동일 타임스탬프를 공유하도록 통일.

### ▶ 주요 산출물 경로
- HTML: `.specgate/data/html_files/{제목}_{타임스탬프}.html`
- MD: `.specgate/data/md_files/{제목}_{타임스탬프}.md` 또는 `{html파일명에서_타임스탬프_승계}.md`
- 품질 리포트: `.specgate/data/quality_reports/quality_report_{score}pts_{level}_{타임스탬프}.json`

## 🔁 다음 스프린트 이관 항목

- GitHub 환경변수 점검 로그 메시지 개선(GITHUB_TOKEN/OWNER/REPO 미설정 가이드)
- 통합 테스트로 실제 이슈 생성/라벨/코멘트 플로우 검증
- `speclint_lint` 단독 호출 시에도(수동 경로) 필요 시 HTML 타임스탬프 주입 파라미터화 검토
