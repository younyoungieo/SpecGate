# Sprint 계획서

## Sprint 개요

### Sprint #1 (완료) - Phase 1 입력 표준화
**목표**: Confluence 문서 수집, HTML→MD 변환, 품질 검사 완전 구현
**기간**: 1일 (8시간)
**Story Points**: 13점
**완료일**: 2024-09-22

### Sprint #2 (예정) - Phase 2 중간 생성
**목표**: 설계 규칙 추출 및 DesignRuleSpec 생성
**기간**: 2일 (16시간)
**Story Points**: 10점

## Sprint #1 상세 계획 (완료)

### 목표
- MCP Server 기본 구조 구축 (US-000)
- Confluence 문서 수집 기능 완전 구현 (US-001)
- 문서 품질 검사 시스템 구축 (US-002)
- HTML→MD 변환 기능 완전 구현 (US-003)

### 구현 범위
1. **US-000: MCP Server 기본 구조** (2시간)
   - FastMCP 서버 설정
   - 기본 도구들 등록 (confluence_fetch, speclint_lint, html_to_md)
   - 데이터 전달 구조 구현
   - 에러 처리 구현

2. **US-001: Confluence 문서 수집** (3시간)
   - Confluence API 연동
   - 라벨 기반 문서 필터링 (CQL 쿼리)
   - HTML 원본 저장 기능
   - SpecGate 형식 변환
   - 환경변수 관리

3. **US-002: 문서 품질 검사** (2시간)
   - SpecLint 모듈 구현
   - 품질 점수 계산 (0-100점)
   - HITL 프로세스 (GitHub Issue 연동)
   - 배치 처리 및 에러 처리
   - 폴더 구조 재구성

4. **US-003: HTML→MD 변환** (1시간)
   - HTML to Markdown 변환기 구현
   - 헤딩, 리스트, 코드블록, 표 변환
   - 파일 저장 기능
   - Confluence 특화 요소 처리

### 완료된 결과
- ✅ MCP Server 완전 동작
- ✅ Confluence에서 문서 수집 가능
- ✅ HTML→MD 변환 완벽 동작
- ✅ 품질 검사 및 점수 계산 완료
- ✅ 전체 파이프라인 테스트 통과
- ✅ 실제 Confluence 문서 테스트 성공

### 데모 시나리오
1. Cursor IDE에서 SpecGate MCP Server 연결
2. Confluence 문서 수집 (design 라벨)
3. HTML→MD 변환 실행
4. 품질 검사 및 점수 계산
5. 전체 파이프라인 자동화 실행
6. 결과 파일 확인 및 검증

## Sprint #2 상세 계획 (예정)

### 목표
- 설계 규칙 추출 기능 구현 (US-004)
- DesignRuleSpec 생성 기능 구현 (US-005)
- 중간 생성 품질 검증 구현 (US-006)

### 구현 범위
1. **US-004: 설계 규칙 추출** (6시간)
   - 정규식 기반 규칙 추출
   - RULE-[영역]-[번호] 패턴 인식
   - 규칙 유형별 분류 (MUST/SHOULD/MUST NOT)
   - 적용 범위, 근거, 참조 정보 추출

2. **US-005: DesignRuleSpec 생성** (4시간)
   - JSON Schema 기반 DesignRuleSpec 생성
   - 규칙-기술스펙 참조 관계 매핑
   - 메타데이터 보존 및 버전 관리
   - 표준화된 출력 형식

3. **US-006: 중간 생성 품질 검증** (2시간)
   - 추출된 규칙의 완전성 검증
   - 규칙 간 일관성 검사
   - 기술 스펙과의 매핑 검증
   - 품질 점수 계산

4. **MCP Server 통합** (2시간)
   - Phase 2 도구들 등록
   - 전체 파이프라인 통합
   - 에러 처리 및 로깅

5. **통합 테스트** (2시간)
   - Phase 1 → Phase 2 전체 워크플로우 테스트
   - 실제 Confluence 문서로 End-to-End 테스트
   - 성능 및 안정성 검증

### 예상 결과
- Phase 1에서 Phase 2로 완전한 데이터 전달
- 설계 규칙 자동 추출 및 분류
- 표준화된 DesignRuleSpec JSON 생성
- 품질 검증된 중간 생성물

### 데모 시나리오
1. Phase 1 완료된 Markdown 문서 로드
2. 설계 규칙 자동 추출 실행
3. DesignRuleSpec JSON 생성
4. 품질 검증 및 점수 계산
5. Phase 3 전달 준비 완료

## 전체 Sprint 목표

### 기능적 목표
- **Phase 1**: 입력 표준화 완료
- **Phase 2**: 중간 표현 생성 완료
- **실제 사용 가능**: 개발자가 쓸 수 있는 MCP Server

### 프로세스 목표
- **애자일 프로세스 경험**: Sprint Planning, Daily Standup, Review, Retrospective
- **User Story 관리**: 작성, 추정, 진행 상황 추적
- **데모 중심 개발**: 각 Sprint마다 데모 가능한 결과물

### 학습 목표
- **MCP 프로토콜 이해**: Model Context Protocol 구현
- **Confluence API 연동**: 외부 API 사용 경험
- **품질 검사 시스템**: 자동화된 품질 관리
- **규칙 기반 시스템**: 설계 규칙 자동화

## 위험 요소 및 대응

### Sprint #1 위험
- **Confluence API 연결 실패**: Mock 데이터로 대체
- **시간 부족**: 핵심 기능만 구현

### Sprint #2 위험
- **통합 복잡도**: 단순한 통합으로 제한
- **MCP 프로토콜 복잡도**: 기본 구현만 진행
- **시간 부족**: 기본 기능만 구현

### 대응 방안
- **Mock 데이터 준비**: API 연결 실패 시 대체
- **기본 기능 우선**: 복잡한 기능은 제외
- **단계별 구현**: 각 기능을 단계별로 구현
- **에러 핸들링**: 기본적인 에러 처리만 구현

## 성공 기준

### Sprint #1 성공 기준 (완료)
- [x] MCP Server 기본 구조 구축 완료
- [x] Confluence에서 문서 수집 가능
- [x] HTML→MD 변환 기능 완전 구현
- [x] 품질 검사 및 점수 계산 동작
- [x] 전체 파이프라인 테스트 통과
- [x] 실제 Confluence 문서 테스트 성공
- [x] 모듈화 및 폴더 구조 정리 완료

### Sprint #2 성공 기준
- [ ] 전체 MCP Server 동작
- [ ] Cursor IDE에서 사용 가능한 룰 생성
- [ ] 설계 규칙 추출 및 적용
- [ ] 실제 사용 가능한 도구

### 전체 성공 기준
- [ ] 실제 사용 가능한 MCP Server
- [ ] 애자일 프로세스 경험
- [ ] 데모 가능한 결과물
- [ ] 학습 목표 달성

---

**작성일**: 2024-09-18  
**작성자**: Product Owner (Sarah)  
**버전**: 1.0
