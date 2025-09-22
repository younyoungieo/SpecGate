# Confluence 업로드 가이드

## 📋 개인 Confluence에 표준 설계 문서 업로드하기

이 가이드는 SpecGate 프로젝트의 표준 설계 문서들을 개인 Confluence에 업로드하는 방법을 설명합니다.

## 🏗️ 생성된 표준 설계 문서들

### 1. **SpecGate API 설계서** (`SpecGate-API-Design.md`)
- **라벨**: `design`, `api`, `specgate`
- **스페이스**: `SpecGate`
- **목적**: SpecGate MCP Server의 API 설계 규칙 및 인터페이스 정의

### 2. **SpecGate 아키텍처 설계서** (`SpecGate-Architecture-Design.md`)
- **라벨**: `architecture`, `design`, `specgate`
- **스페이스**: `SpecGate`
- **목적**: SpecGate 시스템의 전체 아키텍처 및 Phase별 구성 요소 정의

### 3. **SpecGate 데이터 모델 설계서** (`SpecGate-Data-Model-Design.md`)
- **라벨**: `data-model`, `design`, `specgate`
- **스페이스**: `SpecGate`
- **목적**: SpecGate 시스템의 표준화된 데이터 구조 및 스키마 정의

### 4. **SpecGate 보안 설계서** (`SpecGate-Security-Design.md`)
- **라벨**: `security`, `design`, `specgate`
- **스페이스**: `SpecGate`
- **목적**: SpecGate 시스템의 보안 정책 및 보호 메커니즘 정의

### 5. **SpecGate 성능 설계서** (`SpecGate-Performance-Design.md`)
- **라벨**: `performance`, `design`, `specgate`
- **스페이스**: `SpecGate`
- **목적**: SpecGate 시스템의 성능 최적화 및 확장성 설계

## 🚀 Confluence 업로드 단계

### 1단계: 스페이스 생성
1. **Confluence 대시보드** 접속
2. **"Create"** → **"Space"** 클릭
3. **스페이스 이름**: `SpecGate`
4. **스페이스 키**: `SPECGATE` (또는 `SPECGATE`)
5. **설명**: "SpecGate 프로젝트 표준 설계 문서 저장소"

### 2단계: 문서 업로드
각 문서에 대해 다음 단계를 반복:

1. **"Create"** → **"Page"** 클릭
2. **제목 입력** (예: "SpecGate API 설계서")
3. **스페이스 선택**: `SpecGate`
4. **내용 복사**: 해당 `.md` 파일 내용을 복사하여 붙여넣기
5. **라벨 추가**:
   - `design` (모든 문서)
   - `specgate` (모든 문서)
   - 추가 라벨 (문서별 특화)

### 3단계: 라벨 설정
각 문서에 다음 라벨들을 추가:

| 문서 | 필수 라벨 | 추가 라벨 |
|------|-----------|-----------|
| SpecGate API 설계서 | `design`, `specgate` | `api` |
| SpecGate 아키텍처 설계서 | `design`, `specgate` | `architecture` |
| SpecGate 데이터 모델 설계서 | `design`, `specgate` | `data-model` |
| SpecGate 보안 설계서 | `design`, `specgate` | `security` |
| SpecGate 성능 설계서 | `design`, `specgate` | `performance` |

### 4단계: 문서 구조화
1. **문서 계층 구조** 생성:
   ```
   SpecGate 스페이스
   ├── 📋 SpecGate 프로젝트 개요
   ├── 🏗️ 아키텍처 설계서
   ├── 🔌 API 설계서
   ├── 📊 데이터 모델 설계서
   ├── 🔒 보안 설계서
   └── ⚡ 성능 설계서
   ```

2. **문서 간 링크** 설정:
   - 각 문서에서 관련 문서로 링크 추가
   - 목차 페이지 생성

## 🧪 테스트 시나리오

### 1. 기본 검색 테스트
```
SpecGate MCP 서버의 confluence_fetch 도구를 사용해서 "design" 라벨로 문서를 검색해줘.
```

**예상 결과**: 5개 문서 모두 반환

### 2. 특정 라벨 검색 테스트
```
SpecGate MCP 서버의 confluence_fetch 도구를 사용해서 "api" 라벨로 문서를 검색해줘.
```

**예상 결과**: SpecGate API 설계서만 반환

### 3. 스페이스별 검색 테스트
```
SpecGate MCP 서버의 confluence_fetch 도구를 사용해서 "SpecGate" 스페이스에서 "design" 라벨로 문서를 검색해줘.
```

**예상 결과**: SpecGate 스페이스의 design 라벨 문서들만 반환

### 4. HTML→Markdown 변환 테스트
각 문서의 HTML 콘텐츠가 올바르게 Markdown으로 변환되는지 확인

### 5. SpecGate 형식 변환 테스트
변환된 문서가 SpecGate 표준 형식에 맞게 구조화되는지 확인

## 📝 추가 테스트 문서 생성

### 6. **테스트용 비표준 문서** (오류 케이스)
- **라벨**: `test`, `non-standard`
- **목적**: speclint_lint 도구 테스트용
- **내용**: 표준 템플릿을 따르지 않는 문서

### 7. **복잡한 HTML 구조 문서** (변환 테스트)
- **라벨**: `test`, `complex-html`
- **목적**: html_to_md 도구 테스트용
- **내용**: 테이블, 리스트, 이미지 등이 포함된 복잡한 HTML

## 🔧 Confluence 설정 팁

### 1. 라벨 관리
- **라벨 정책** 설정: 일관된 라벨 사용
- **라벨 색상** 지정: 시각적 구분
- **라벨 설명** 추가: 용도 명시

### 2. 권한 설정
- **스페이스 권한**: 읽기 전용으로 설정
- **문서 권한**: 편집자만 수정 가능
- **댓글 권한**: 모든 사용자 허용

### 3. 검색 최적화
- **문서 제목** 명확하게 작성
- **문서 요약** 추가
- **키워드** 포함

## 📊 업로드 완료 체크리스트

- [ ] SpecGate 스페이스 생성 완료
- [ ] 5개 표준 설계 문서 업로드 완료
- [ ] 각 문서에 올바른 라벨 설정 완료
- [ ] 문서 간 링크 설정 완료
- [ ] 기본 검색 테스트 통과
- [ ] 특정 라벨 검색 테스트 통과
- [ ] 스페이스별 검색 테스트 통과
- [ ] HTML→Markdown 변환 테스트 통과
- [ ] SpecGate 형식 변환 테스트 통과

## 🎯 다음 단계

1. **US-002 (speclint_lint) 개발**
   - 품질 검사 엔진 구현
   - 표준 템플릿 검증 로직 개발

2. **US-003 (html_to_md) 개발**
   - HTML 파서 구현
   - Markdown 변환 엔진 개발

3. **Phase 2 개발**
   - 규칙 추출 엔진 구현
   - Spec 생성 엔진 개발

4. **Phase 3 개발**
   - CI 게이트 스코어링 구현
   - 자동화 워크플로우 구축

---

**📁 파일 위치**: `docs/standard-design-documents/`
**🔗 Confluence URL**: `https://your-domain.atlassian.net/wiki/spaces/SPECGATE`
**🏷️ 주요 라벨**: `design`, `specgate`, `api`, `architecture`, `data-model`, `security`, `performance`
