# Epic 3: Phase 2 - 중간 표현 생성

## 📋 Epic 정보

- **Epic ID**: EPIC-003
- **제목**: Phase 2 - 중간 표현 생성
- **목적**: 표준화된 문서에서 DesignRuleSpec 중간 표현 생성
- **범위**: 규칙 추출, IDE 룰 생성, 실시간 지원
- **예상 기간**: 3-4 스프린트
- **우선순위**: 중간
- **상태**: 대기 중

## 🎯 Epic 목표

Phase 1에서 정규화된 문서를 바탕으로 DesignRuleSpec 중간 표현을 생성하고, 이를 통해 Cursor IDE에서 사용할 수 있는 룰과 스니펫을 자동 생성하여 개발자에게 실시간 지원을 제공한다.

## 📝 Epic 설명

Phase 2는 SpecGate MCP Server의 개발 지원 단계입니다. Phase 1에서 수집된 정규화된 문서를 분석하여 설계 규칙을 추출하고, 이를 DesignRuleSpec DSL로 변환한 후, Cursor IDE에서 사용할 수 있는 .mdc 파일과 스니펫을 자동 생성합니다.

## 🎯 성공 기준

- [ ] DesignRuleSpec 스키마가 정의됨
- [ ] 규칙 추출 알고리즘이 구현됨
- [ ] .mdc 파일 자동 생성이 가능함
- [ ] 스니펫 자동완성이 작동함
- [ ] 실시간 가이드가 제공됨
- [ ] 위반 감지가 가능함

## 📊 포함된 User Story

### **US-006: DesignRuleSpec 스키마 정의**
- **Story Point**: 3
- **상태**: 대기 중
- **설명**: 중간 표현 DSL 스키마 설계

### **US-007: 규칙 추출 알고리즘 구현**
- **Story Point**: 5
- **상태**: 대기 중
- **설명**: rules.extract MCP 도구 구현

### **US-008: .mdc 파일 생성 기능**
- **Story Point**: 4
- **상태**: 대기 중
- **설명**: rules.generate.mdc MCP 도구 구현

### **US-009: 스니펫 자동완성 기능**
- **Story Point**: 3
- **상태**: 대기 중
- **설명**: snippet.generate MCP 도구 구현

### **US-010: 실시간 가이드 기능**
- **Story Point**: 2
- **상태**: 대기 중
- **설명**: realtime.guide MCP 도구 구현

### **US-011: 위반 감지 기능**
- **Story Point**: 3
- **상태**: 대기 중
- **설명**: violation.detect MCP 도구 구현

## 🔄 구현 계획

### **Sprint #4 (2일)**
- **US-006**: DesignRuleSpec 스키마 정의
- **US-007**: 규칙 추출 알고리즘 구현 (기본 버전)

### **Sprint #5 (2일)**
- **US-008**: .mdc 파일 생성 기능
- **US-009**: 스니펫 자동완성 기능

### **Sprint #6 (2일)**
- **US-010**: 실시간 가이드 기능
- **US-011**: 위반 감지 기능

### **Sprint #7 (2일)**
- 통합 테스트 및 최적화
- 성능 튜닝 및 문서화

## 🛠️ 기술적 요구사항

### **필수 도구**
- **Azure OpenAI**: 자연어 규칙 추출
- **JSON Schema**: DesignRuleSpec 검증
- **Markdown Parser**: .mdc 파일 생성
- **정규식 엔진**: 패턴 매칭

### **의존성**
- **Epic 2**: Phase 1 입력 표준화 (완료 필요)
- **Azure OpenAI 리소스**: API 키 및 엔드포인트
- **Cursor IDE**: .mdc 파일 적용

## 🚨 위험 요소

### **높음**
- **Azure OpenAI 의존성**: API 제한 및 비용
- **규칙 추출 정확도**: 자연어 처리의 한계

### **중간**
- **.mdc 파일 호환성**: Cursor IDE 버전 호환성
- **성능**: 실시간 처리 시 지연

### **낮음**
- **스키마 변경**: DesignRuleSpec 스키마 진화

## 📊 메트릭

- **총 Story Points**: 20
- **예상 완료일**: 2024-10-16
- **핵심 성공 지표**: 규칙 추출 정확도 90% 이상

## 🔄 다음 단계

1. **Epic 2 완료 대기**: Phase 1 입력 표준화 완료
2. **DesignRuleSpec 스키마 설계**: 중간 표현 표준화
3. **Azure OpenAI 설정**: API 키 및 엔드포인트 구성

---

**작성일**: 2024-09-18  
**작성자**: Product Owner (Sarah)  
**버전**: 1.0
