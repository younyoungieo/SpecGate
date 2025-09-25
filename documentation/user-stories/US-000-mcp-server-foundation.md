# US-000: MCP Server 기본 구조 구축

### Story 정보
- **Story ID**: US-000
- **Epic**: Epic 1 - 프로젝트 기반 구축
- **Story Point**: 2
- **상태**: Ready for Review

### User Story
**As a** 개발자,  
**I want to** SpecGate MCP Server의 기본 구조를 구축할 수 있는 기능,  
**So that** Phase 1의 MCP 도구들(confluence.fetch, speclint.lint)을 구현할 수 있는 기반을 마련할 수 있다.

### Note
- MCP Server 프레임워크 설정
- 기본 도구 구조 생성
- 도구 간 연동 구조
- 기본 구조만 구현

### AC
- [x] MCP Server 프레임워크가 설정되어 있다
- [x] confluence.fetch 도구의 기본 구조가 생성되어 있다
- [x] speclint.lint 도구의 기본 구조가 생성되어 있다
- [x] HTML→MD 변환 모듈의 기본 구조가 생성되어 있다
- [x] 도구 간 데이터 전달 구조가 구현되어 있다
- [x] MCP Server가 정상적으로 시작되고 종료된다

### TC
- **정상 케이스**: MCP Server 시작 → 도구 목록 확인 → 기본 동작 테스트
- **에러 케이스**: 잘못된 설정 → 에러 메시지 출력

### Out Of Scope
- 고급 MCP Server 기능
- 도구별 실제 작동 구현
- 복잡한 도구 간 연동
- 성능 최적화
- 모니터링 시스템