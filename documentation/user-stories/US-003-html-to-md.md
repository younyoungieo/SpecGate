# US-003: HTML→MD 변환 기능

### Story 정보
- **Story ID**: US-003
- **Epic**: Epic 2 - Phase 1 입력 표준화
- **Story Point**: 1
- **상태**: 대기 중

### User Story
**As a** 개발자,  
**I want to** Confluence에서 수집한 HTML 문서를 Markdown 형식으로 변환할 수 있는 기능,  
**So that** 설계 규칙 추출을 위해 표준화된 문서 형식을 사용할 수 있다.

### Note
- 기본적인 HTML→MD 변환만 구현
- 복잡한 HTML 구조는 단순화하여 처리
- 8시간 스프린트 제약으로 기본 변환만 지원

### AC
- [ ] HTML 문서를 Markdown 형식으로 변환할 수 있다
- [ ] 헤딩 태그(h1, h2, h3)를 Markdown 헤딩으로 변환할 수 있다
- [ ] 리스트 태그(ul, ol)를 Markdown 리스트로 변환할 수 있다
- [ ] 코드 블록을 Markdown 코드 블록으로 변환할 수 있다
- [ ] 변환된 Markdown을 파일로 저장할 수 있다
- [ ] 변환 실패 시 적절한 에러 메시지를 출력한다

### TC (Test Cases)
- **정상 케이스**: 기본 HTML → Markdown 변환 성공
- **에러 케이스**: 잘못된 HTML → 에러 메시지 출력
- **경계값 케이스**: 빈 HTML → 빈 Markdown 출력
- **복잡성 케이스**: 복잡한 HTML → 단순화된 Markdown 출력

### Out Of Scope
- 복잡한 HTML 구조 처리
- 고급 Markdown 기능 (표, 이미지 등)
- 실시간 변환
- 변환 품질 최적화
