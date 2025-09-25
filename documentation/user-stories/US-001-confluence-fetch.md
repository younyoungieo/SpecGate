# US-001: Confluence 문서 수집 기능

### Story 정보
- **Story ID**: US-001
- **Epic**: Epic 2 - Phase 1 입력 표준화
- **Story Point**: 4
- **상태**: Ready for Review

### User Story
**As a** 개발자,  
**I want to** Confluence MCP Server를 통해 설계 문서를 수집할 수 있는 기능,  
**So that** SpecGate에서 설계 규칙을 추출할 수 있는 문서를 얻을 수 있다.

### Note
- **멀티 클라이언트 구조**: 기존 Confluence MCP Server 활용
- **환경변수 통합**: mcp.json의 env 섹션으로 모든 설정 관리
- **라벨 기반 필터링**: CQL 쿼리로 정확한 문서 검색
- **자동 HTML→MD 변환**: Confluence MCP Server에서 처리
- **8시간 스프린트 제약으로 기본 기능만 구현**

### AC
- [x] Confluence MCP Server와 성공적으로 연동할 수 있다
- [x] 특정 라벨로 문서를 필터링할 수 있다 (CQL 쿼리 사용)
- [x] 문서의 Markdown 변환된 내용을 가져올 수 있다
- [x] 수집된 문서를 SpecGate 형식으로 변환할 수 있다
- [x] Confluence MCP Server 연결 실패 시 적절한 에러 메시지를 출력한다 (`.specgate/logs/` 로그 파일)
- [x] mcp.json의 env 섹션으로 Confluence 설정을 관리할 수 있다

### TC
- **정상 케이스**: Confluence MCP Server 연결 → 라벨 필터링 → 문서 수집 → SpecGate 형식 변환
- **에러 케이스**: Confluence MCP Server 연결 실패 → 에러 메시지 출력 (`.specgate/logs/` 로그 파일)
- **경계값 케이스**: 없는 라벨 검색 → 빈 결과 처리
- **데이터 케이스**: 복잡한 Confluence 문서 → Markdown 변환 품질 확인
- **통합 케이스**: SpecGate MCP Server → Confluence MCP Server → Confluence API 전체 플로우

### 아키텍처
```
AI Client → SpecGate MCP Server → Confluence MCP Server → Confluence API
                ↓                        ↓
         [confluence_fetch]      [search_confluence_pages, get_confluence_page]
                ↓
         [SpecGate 형식 변환]
```

### Out Of Scope
- Confluence MCP Server 직접 구현 (기존 서버 활용)
- 실시간 동기화
- 캐싱 시스템
- 고급 에러 핸들링

