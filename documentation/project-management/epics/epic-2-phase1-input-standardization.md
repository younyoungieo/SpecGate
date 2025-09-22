# Epic 2: Phase 1 - 입력 표준화

## 📋 Epic 정보

- **Epic ID**: EPIC-002
- **제목**: Phase 1 - 입력 표준화
- **목적**: Confluence 문서를 표준화된 형식으로 수집하고 정규화
- **범위**: 문서 수집, 품질 검사, 정규화
- **예상 기간**: 2-3 스프린트
- **우선순위**: 높음 (핵심)
- **상태**: 대기 중

## 🎯 Epic 목표

Confluence에 저장된 설계 문서를 자동으로 수집하고, 표준화된 형식으로 정규화하여 Phase 2에서 DesignRuleSpec을 추출할 수 있는 기반을 마련한다.

## 📝 Epic 설명

Phase 1은 SpecGate MCP Server의 입력 표준화 단계입니다. Confluence API를 통해 설계 문서를 수집하고, 품질 검사를 통해 신뢰할 수 있는 문서만 선별한 후, HTML을 Markdown으로 변환하여 일관된 형식으로 정규화합니다.

## 🎯 성공 기준 (업데이트됨)

- [x] Confluence API를 통해 문서를 자동 수집할 수 있음
- [x] HTML 원본 파일이 로컬에 저장됨 (html_files/)
- [x] 라벨 기반 필터링이 정상 작동함
- [x] HTML→MD 변환이 정확하게 수행됨
- [x] 변환된 Markdown이 파일로 저장됨 (markdown_files/)
- [x] 문서 품질 검사가 자동화됨 (내용 직접 + 파일 기반)
- [x] 단계별 워크플로우가 자연스럽게 연결됨
- [ ] HITL 프로세스가 구현됨
- [x] 정규화된 문서가 저장됨

## 📊 포함된 User Story (업데이트됨)

### **US-001: Confluence 문서 수집 기능 (완료)**
- **Story Point**: 5  
- **상태**: ✅ 완료
- **설명**: confluence_fetch MCP 도구 구현 (HTML 원본 저장 포함)

### **US-002: 문서 품질 검사 기능 (완료)**
- **Story Point**: 3
- **상태**: ✅ 완료  
- **설명**: speclint_lint 및 check_document_quality MCP 도구 구현

### **US-003: HTML→MD 변환 기능 (완료)**
- **Story Point**: 2
- **상태**: ✅ 완료
- **설명**: html_to_md 및 convert_saved_html MCP 도구 구현

### **US-006: 단계별 워크플로우 구현 (새로 추가됨)**
- **Story Point**: 3
- **상태**: ✅ 완료
- **설명**: 파일 기반 단계별 처리 워크플로우 구현

### **US-005: HITL 프로세스 구현**
- **Story Point**: 3
- **상태**: 대기 중
- **설명**: GitHub Issues 기반 검토 프로세스

## 🔄 구현 계획

### **Sprint #1 (2일)**
- **US-002**: Confluence 문서 수집 기능 (기본 버전)
- **US-003**: 문서 품질 검사 기능 (기본 버전)

### **Sprint #2 (2일)**
- **US-004**: HTML→MD 변환 기능
- **US-005**: HITL 프로세스 구현

### **Sprint #3 (2일)**
- 통합 테스트 및 최적화
- 문서화 및 검증

## 🛠️ 기술적 요구사항

### **필수 도구 (업데이트됨)**
- **Confluence API**: 문서 수집 ✅
- **HTML Parser**: HTML→MD 변환 ✅  
- **정규식 엔진**: 품질 검사 ✅
- **파일 시스템**: HTML, MD, 품질 결과 저장 ✅
- **aiofiles**: 비동기 파일 I/O ✅
- **GitHub API**: HITL 프로세스 (대기 중)

### **의존성**
- **Epic 1**: 프로젝트 기반 구축 (완료 필요)
- **Confluence 접근 권한**: 읽기 전용 토큰
- **GitHub 저장소**: Issues 생성 권한

## 🚨 위험 요소

### **높음**
- **Confluence API 제한**: API 호출 제한 및 권한 문제
- **문서 품질**: 비표준 형식 문서의 처리

### **중간**
- **HTML→MD 변환**: 복잡한 HTML 구조 처리
- **HITL 프로세스**: 사용자 참여도

### **낮음**
- **성능**: 대량 문서 처리 시 성능 이슈

## 📊 메트릭 (업데이트됨)

- **총 Story Points**: 16 (13 + 3 새로운 워크플로우)
- **완료된 Story Points**: 13 ✅ 
- **남은 Story Points**: 3 (HITL 프로세스)
- **완료율**: 81% (13/16)
- **핵심 성공 지표**: 
  - 문서 수집 성공률 95% 이상 ✅
  - HTML 원본 저장률 100% ✅
  - 단계별 워크플로우 작동률 100% ✅

## 🔄 다음 단계

1. **Epic 1 완료 대기**: 프로젝트 기반 구축 완료
2. **Sprint #1 시작**: Confluence 문서 수집 기능 구현
3. **테스트 데이터 준비**: 클테코 3기 문서 준비

---

**작성일**: 2024-09-18  
**작성자**: Product Owner (Sarah)  
**버전**: 1.0
