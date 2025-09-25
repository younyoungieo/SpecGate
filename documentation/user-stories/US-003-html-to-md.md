# US-003: HTML→MD 변환 기능

### Story 정보
- **Story ID**: US-003
- **Epic**: Epic 2 - Phase 1 입력 표준화
- **Story Point**: 3
- **상태**: Ready for Review

### User Story
**As a** 개발자,  
**I want to** Confluence에서 수집한 HTML 문서를 Markdown 형식으로 변환할 수 있는 기능,  
**So that** 설계 규칙 추출을 위해 표준화된 문서 형식을 사용할 수 있다.

### Note
- **MCP 도구에서는 제거**: 독립적인 `html_to_md` MCP 도구는 로직 중복으로 인해 제거
- **내부 엔진 유지**: `HTMLToMarkdownConverter` 클래스는 `confluence_fetch` 내부에서 사용
- **복잡한 HTML 구조는 단순화하여 처리**: 기본 변환을 넘어 (표, Confluence 매크로, 인라인 요소 등은 일부 지원)

### AC
- [x] HTML 문서를 Markdown 형식으로 변환할 수 있다
- [x] 헤딩 태그(h1, h2, h3, h4, h5, h6)를 Markdown 헤딩으로 변환할 수 있다
- [x] 리스트 태그(ul, ol)를 Markdown 리스트로 변환할 수 있다
- [x] 코드 블록과 인라인 코드를 Markdown으로 변환할 수 있다
- [x] 표(table)를 Markdown 표 형식으로 변환할 수 있다
- [x] 인용문(blockquote)을 Markdown 인용문으로 변환할 수 있다
- [x] Confluence 매크로를 Markdown으로 변환할 수 있다
- [x] 변환된 Markdown을 파일로 저장할 수 있다
- [x] 변환 실패 시 에러 처리 및 로그 기록
- [x] 인라인 요소(strong, em, code) 처리
- [x] 변환 성능 측정 및 상세 로그

### TC
- **기본 변환**: HTML 헤딩, 리스트, 문단 → 올바른 Markdown 형식
- **표 변환**: HTML table → Markdown 표 (헤더 + 구분선)
- **코드 변환**: pre/code 태그 → ```언어``` 코드 블록 (언어 자동 감지)
- **인라인 요소**: strong, em, code → **굵게**, *기울임*, `코드`
- **Confluence 매크로**: ac:structured-macro → Markdown 형식 변환
- **파일 저장**: save_to_file=True → 지정된 경로에 .md 파일 생성
- **에러 처리**: 잘못된 HTML → 로그 기록 + 부분 변환 결과 반환
- **성능 측정**: 각 변환 단계별 소요 시간 측정 및 로깅
- **빈 문서 처리**: 빈 HTML → 빈 Markdown 또는 기본 구조

### Out Of Scope
- 복잡한 HTML 구조 처리
- 고급 Markdown 기능 (이미지, 다이어그램 등)
- 실시간 변환
- 변환 품질 최적화