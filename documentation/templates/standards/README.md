# SpecGate 표준 설계 문서

이 폴더는 SpecGate 프로젝트의 표준 설계 문서들을 포함합니다. 이 문서들은 Phase1_SpecGate_Input_Standardization.md의 표준에 따라 작성되었으며, 개인 Confluence에 업로드하여 테스트할 수 있습니다.

## 📁 문서 목록

### 1. **SpecGate API 설계서** (`SpecGate-API-Design.md`)
- **목적**: SpecGate MCP Server의 API 설계 규칙 및 인터페이스 정의
- **라벨**: `design`, `api`, `specgate`
- **주요 내용**:
  - MCP 도구 설계 규칙 (confluence_fetch, speclint_lint, html_to_md)
  - OpenAPI 3.0 스펙 정의
  - Pydantic 모델 정의
  - 테스트 케이스

### 2. **SpecGate 아키텍처 설계서** (`SpecGate-Architecture-Design.md`)
- **목적**: SpecGate 시스템의 전체 아키텍처 및 Phase별 구성 요소 정의
- **라벨**: `architecture`, `design`, `specgate`
- **주요 내용**:
  - 4단계 Phase 구조 (Phase 0, 1, 2, 3)
  - 시스템 아키텍처 다이어그램
  - 데이터 흐름 시퀀스 다이어그램
  - 컴포넌트 상세 설계

### 3. **SpecGate 데이터 모델 설계서** (`SpecGate-Data-Model-Design.md`)
- **목적**: SpecGate 시스템의 표준화된 데이터 구조 및 스키마 정의
- **라벨**: `data-model`, `design`, `specgate`
- **주요 내용**:
  - JSON Schema 정의
  - Pydantic 모델 정의
  - 데이터 변환 유틸리티
  - 검증 규칙

### 4. **SpecGate 보안 설계서** (`SpecGate-Security-Design.md`)
- **목적**: SpecGate 시스템의 보안 정책 및 보호 메커니즘 정의
- **라벨**: `security`, `design`, `specgate`
- **주요 내용**:
  - OWASP 보안 가이드라인 준수
  - 인증 및 권한 관리
  - 입력 검증 및 이스케이프
  - 암호화 및 보안 통신

### 5. **SpecGate 성능 설계서** (`SpecGate-Performance-Design.md`)
- **목적**: SpecGate 시스템의 성능 최적화 및 확장성 설계
- **라벨**: `performance`, `design`, `specgate`
- **주요 내용**:
  - 비동기 처리 최적화
  - 캐싱 전략
  - 메모리 최적화
  - 성능 모니터링

### 6. **Confluence 업로드 가이드** (`Confluence-Upload-Guide.md`)
- **목적**: 개인 Confluence에 표준 설계 문서 업로드 방법 안내
- **주요 내용**:
  - 스페이스 생성 방법
  - 문서 업로드 단계
  - 라벨 설정 방법
  - 테스트 시나리오

## 🏷️ 라벨 체계

### 기본 라벨
- `design`: 모든 설계 문서
- `specgate`: SpecGate 프로젝트 관련 문서

### 문서별 특화 라벨
- `api`: API 설계 관련
- `architecture`: 아키텍처 설계 관련
- `data-model`: 데이터 모델 설계 관련
- `security`: 보안 설계 관련
- `performance`: 성능 설계 관련

### 테스트용 라벨
- `test`: 테스트용 문서
- `non-standard`: 비표준 형식 문서 (오류 케이스)
- `complex-html`: 복잡한 HTML 구조 문서

## 🚀 사용 방법

### 1. Confluence 업로드
1. `Confluence-Upload-Guide.md` 참조
2. 개인 Confluence에 SPECGATE 스페이스 생성
3. 각 문서를 해당 라벨과 함께 업로드

### 2. SpecGate MCP 서버 테스트
```bash
# 기본 검색 테스트
SpecGate MCP 서버의 confluence_fetch 도구를 사용해서 "design" 라벨로 문서를 검색해줘.

# 특정 라벨 검색 테스트
SpecGate MCP 서버의 confluence_fetch 도구를 사용해서 "api" 라벨로 문서를 검색해줘.

# 스페이스별 검색 테스트
SpecGate MCP 서버의 confluence_fetch 도구를 사용해서 "SPECGATE" 스페이스에서 "design" 라벨로 문서를 검색해줘.
```

### 3. 다음 단계 개발
- **US-002 (speclint_lint)**: 품질 검사 엔진 구현
- **US-003 (html_to_md)**: HTML→Markdown 변환 엔진 구현
- **Phase 2**: 규칙 추출 및 Spec 생성 엔진 구현
- **Phase 3**: CI 게이트 스코어링 및 자동화 구현

## 📊 문서 구조

모든 설계 문서는 Phase1 표준에 따라 다음 구조를 따릅니다:

1. **개요** - 목적, 배경, 참고사항
2. **설계 규칙** - MUST, SHOULD, 금지 규칙
3. **기술 스펙** - 아키텍처, 데이터 모델, API 스펙
4. **구현 가이드** - 코드 예시, 테스트 케이스
5. **변경 이력** - 버전 관리

## 🔧 개발 환경

- **Python**: 3.11+
- **FastMCP**: 2.12+
- **Pydantic**: v2
- **Confluence API**: REST API v2
- **개인 Confluence**: your-domain.atlassian.net

## 📝 참고 자료

- [Phase1_SpecGate_Input_Standardization.md](../design/Phase1_SpecGate_Input_Standardization.md)
- [US-001-confluence-fetch.md](../stories/US-001-confluence-fetch.md)
- [FastMCP 공식 문서](https://gofastmcp.com/)
- [Confluence REST API 문서](https://developer.atlassian.com/cloud/confluence/rest/)

---

**📅 생성일**: 2024-01-15  
**👥 작성자**: SpecGate Team  
**🔄 최종 수정**: 2024-01-15


