# Epic 4: Phase 3 - CI 게이트 스코어링

## 📋 Epic 정보

- **Epic ID**: EPIC-004
- **제목**: Phase 3 - CI 게이트 스코어링
- **목적**: 설계 위반을 자동 검출하고 PR을 차단하는 CI 게이트 구축
- **범위**: 테스트 생성, Drift Score 계산, PR 코멘트
- **예상 기간**: 2-3 스프린트
- **우선순위**: 중간
- **상태**: 대기 중

## 🎯 Epic 목표

Phase 2에서 생성된 DesignRuleSpec을 바탕으로 자동화된 테스트를 생성하고, Drift Score를 계산하여 설계 위반 시 PR을 자동으로 차단하는 CI 게이트 시스템을 구축한다.

## 📝 Epic 설명

Phase 3은 SpecGate MCP Server의 CI/PR 검증 단계입니다. DesignRuleSpec을 기반으로 ArchUnit, Semgrep, OpenAPI Diff 테스트를 자동 생성하고, 검사 결과를 Drift Score로 변환하여 PR 화면에 Drift Radar를 표시합니다.

## 🎯 성공 기준

- [ ] ArchUnit 테스트 자동 생성이 가능함
- [ ] Semgrep 규칙 자동 생성이 가능함
- [ ] OpenAPI Diff 테스트가 구현됨
- [ ] Drift Score 계산이 정확함
- [ ] Drift Radar가 PR에 표시됨
- [ ] PR 차단 기능이 작동함

## 📊 포함된 User Story

### **US-012: 테스트 코드 자동 생성**
- **Story Point**: 5
- **상태**: 대기 중
- **설명**: tests.generate MCP 도구 구현

### **US-013: Drift Score 계산 모델**
- **Story Point**: 4
- **상태**: 대기 중
- **설명**: drift.score MCP 도구 구현

### **US-014: PR 코멘트 생성 기능**
- **Story Point**: 3
- **상태**: 대기 중
- **설명**: github.comment MCP 도구 구현

### **US-015: GitHub Actions 워크플로우 생성**
- **Story Point**: 4
- **상태**: 대기 중
- **설명**: workflow.generate MCP 도구 구현

### **US-016: CI 게이트 통합**
- **Story Point**: 3
- **상태**: 대기 중
- **설명**: 전체 CI/CD 파이프라인 통합

## 🔄 구현 계획

### **Sprint #8 (2일)**
- **US-012**: 테스트 코드 자동 생성 (ArchUnit, Semgrep)

### **Sprint #9 (2일)**
- **US-013**: Drift Score 계산 모델
- **US-014**: PR 코멘트 생성 기능

### **Sprint #10 (2일)**
- **US-015**: GitHub Actions 워크플로우 생성
- **US-016**: CI 게이트 통합

## 🛠️ 기술적 요구사항

### **필수 도구**
- **ArchUnit**: Java 아키텍처 테스트
- **Semgrep**: 다중 언어 정적 분석
- **OpenAPI Diff**: API 스펙 변경사항 검증
- **GitHub Actions**: CI/CD 파이프라인
- **Python**: Drift Score 계산 및 PR 코멘트 생성

### **의존성**
- **Epic 3**: Phase 2 중간 표현 생성 (완료 필요)
- **GitHub 저장소**: Actions 실행 권한
- **검사 도구 라이선스**: ArchUnit, Semgrep 등

## 🚨 위험 요소

### **높음**
- **검사 도구 의존성**: ArchUnit, Semgrep 라이선스 및 호환성
- **Drift Score 정확도**: 점수 계산의 정확성

### **중간**
- **GitHub Actions 제한**: 실행 시간 및 리소스 제한
- **PR 차단 정확도**: 오탐지 및 미탐지

### **낮음**
- **성능**: 대량 테스트 실행 시 성능 이슈

## 📊 메트릭

- **총 Story Points**: 19
- **예상 완료일**: 2024-10-30
- **핵심 성공 지표**: PR 차단 정확도 95% 이상

## 🔄 다음 단계

1. **Epic 3 완료 대기**: Phase 2 중간 표현 생성 완료
2. **검사 도구 설정**: ArchUnit, Semgrep 설치 및 설정
3. **GitHub Actions 구성**: CI/CD 파이프라인 환경 준비

---

**작성일**: 2024-09-18  
**작성자**: Product Owner (Sarah)  
**버전**: 1.0
