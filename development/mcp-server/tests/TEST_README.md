# US-002 speclint.lint 테스트 가이드

Test Architect Quinn이 설계한 US-002 speclint.lint 기능의 포괄적인 테스트 케이스입니다.

## 📊 테스트 개요

- **총 테스트 시나리오**: 24개
- **Unit Tests**: 12개 (50%) - 순수 로직 및 검증
- **Integration Tests**: 8개 (33%) - 컴포넌트 상호작용 및 API 호출
- **E2E Tests**: 4개 (17%) - 핵심 사용자 워크플로우

## 🎯 우선순위별 테스트

### P0 (Critical) - 12개 테스트
핵심 기능과 에러 처리에 대한 필수 테스트

```bash
# P0 테스트만 실행
python -m pytest tests/test_server.py::TestSpecLintLint::test_us002_unit_001_perfect_document_structure -v
```

### P1 (High) - 8개 테스트
통합 기능과 사용자 경험에 대한 중요 테스트

### P2 (Medium) - 4개 테스트
배치 처리와 사용자 메시지 표시 테스트

## 🚀 테스트 실행 방법

### 1. 전체 테스트 실행
```bash
cd mcp-server
python run_tests.py
```

### 2. 우선순위별 테스트 실행
```bash
# P0 (Critical) 테스트만
python -m pytest tests/test_server.py::TestSpecLintLint -k "unit" -v

# P1 (High) 테스트만
python -m pytest tests/test_server.py::TestSpecLintIntegration -v

# P2 (Medium) 테스트만
python -m pytest tests/test_server.py::TestSpecLintE2E -v
```

### 3. 특정 테스트 실행
```bash
# 특정 테스트 케이스 실행
python -m pytest tests/test_server.py::TestSpecLintLint::test_us002_unit_001_perfect_document_structure -v

# 패턴 매칭으로 테스트 실행
python -m pytest tests/test_server.py -k "perfect_document" -v
```

## 📋 테스트 데이터

### 완벽한 문서 (PERFECT_DOCUMENT)
- 90점 이상 예상
- 모든 필수 섹션 포함
- 올바른 규칙 형식
- 기술 스펙 포함

### 불완전한 문서 (INCOMPLETE_DOCUMENT)
- 70점 미만 예상
- 필수 섹션 누락
- 잘못된 규칙 형식

### 빈 문서 (EMPTY_DOCUMENT)
- 0점 예상
- 파싱 실패 처리

### 잘못된 형식 문서 (MALFORMED_DOCUMENT)
- 60점 예상
- 규칙 ID 형식 오류

## 🔍 테스트 검증 포인트

### 1. 문서 구조 검사
- 제목 형식: `[프로젝트명] [문서유형] 설계서`
- 설계 규칙 섹션 존재
- 기술 스펙 섹션 존재

### 2. 품질 점수 계산
- 0-100점 범위 보장
- 규칙별 차감 점수 적용
- 최종 점수 산정

### 3. 에러 처리
- 파싱 실패 시 0점 반환
- 적절한 에러 메시지 생성
- 시스템 중단 방지

### 4. 품질 등급별 처리
- 90점 이상: 자동 승인
- 70-89점: HITL 검토
- 70점 미만: 필수 수정

## 📈 성능 요구사항

- **단일 문서 처리**: < 5초 (1MB 문서)
- **배치 처리**: < 30초 (10개 문서)
- **메모리 제한**: 10MB per document, 100MB total

## 🛠️ 개발 환경 설정

### 필수 의존성
```bash
pip install pytest pytest-asyncio
```

### pytest 설정
`pytest.ini` 파일이 포함되어 있어 자동으로 설정됩니다.

## 📝 테스트 결과 해석

### 성공 케이스
```
✅ P0 테스트 통과!
✅ P1 테스트 통과!
✅ P2 테스트 통과!
```

### 실패 케이스
```
❌ P0 테스트 실패!
⚠️ P1 테스트 일부 실패 (개발 중이므로 계속 진행)
ℹ️ P2 테스트 일부 실패 (선택사항이므로 계속 진행)
```

## 🔧 문제 해결

### 1. Import 에러
```bash
# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 테스트 실패
```bash
# 상세한 에러 정보 확인
python -m pytest tests/test_server.py -v --tb=long

# 특정 테스트만 실행하여 디버깅
python -m pytest tests/test_server.py::TestSpecLintLint::test_us002_unit_001_perfect_document_structure -v -s
```

### 3. 비동기 테스트 문제
```bash
# asyncio 모드 확인
python -m pytest tests/test_server.py --asyncio-mode=auto -v
```

## 📚 추가 정보

- **테스트 설계 문서**: `docs/qa/assessments/US-002-test-design-20241219.md`
- **품질 게이트**: `docs/qa/gates/US-002-speclint-lint.yml`
- **스토리 문서**: `docs/stories/US-002-speclint-lint.md`

---

**Test Architect**: Quinn  
**Last Updated**: 2024-12-19  
**Quality Gate**: PASS ✅


