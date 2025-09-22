# US-002: 문서 품질 검사 기능 설계 문서

## 1. 기능 개요

### 1.1 목적
수집된 Markdown 문서의 품질을 검사하고 0-100점 점수를 계산하여 Phase 2 진행 여부를 결정한다.

### 1.2 핵심 기능 (업데이트됨)
- **리팩토링된 모듈 구조**: SpecLint, TemplateValidator, QualityScorer, ImprovementSuggester 분리
- **문서 내용 직접 검사**: speclint_lint 도구 (단일 인터페이스)
- **품질 점수 계산**: 0-100점 정확한 계산
- **개선 사항 제안**: 구체적인 수정 방향 제시
- **배치 처리 지원**: 여러 파일 일괄 처리

## 2. 품질 검사 규칙

### 2.1 필수 구조 검사
```python
STRUCTURE_CHECKS = {
    'title_format': {
        'pattern': r'^#\s*\[.+\]\s*\[.+\]\s*설계서\s*$',
        'weight': 20,
        'description': '문서 제목이 "[프로젝트명] [문서유형] 설계서" 형식인가?'
    },
    'design_rules_section': {
        'pattern': r'##\s*2\.\s*설계\s*규칙',
        'weight': 30,
        'description': '설계 규칙 섹션이 존재하는가?'
    },
    'rule_format': {
        'pattern': r'\*\*RULE-[A-Z]+-[0-9]+\*\*\s*\([A-Z\s]+\):',
        'weight': 3,
        'description': '규칙이 "RULE-[영역]-[번호] (유형): [규칙]" 형식을 따르는가?'
    },
    'technical_spec_section': {
        'pattern': r'##\s*3\.\s*기술\s*스펙',
        'weight': 25,
        'description': '기술 스펙 섹션이 존재하는가?'
    }
}
```

### 2.2 품질 점수 산정
```python
QUALITY_SCORING = {
    'base_score': 100,
    'deductions': {
        'title_format_mismatch': -20,
        'design_rules_missing': -30,
        'rule_id_format_mismatch': -3,  # per rule
        'rule_type_mismatch': -2,       # per rule
        'scope_missing': -2,            # per rule
        'reason_missing': -2,           # per rule
        'reference_missing': -1,        # per rule
        'technical_spec_missing': -25,
        'rule_spec_relation_missing': -10,
        'code_example_missing': -5,
        'change_history_missing': -5
    },
    'thresholds': {
        'high_quality': 90,      # 자동 승인
        'medium_quality': 70,    # HITL 검토
        'low_quality': 0         # 필수 수정
    }
}
```

## 3. 검사 로직

### 3.1 문서 구조 분석
```python
def analyze_document_structure(markdown_content):
    """문서 구조를 분석하고 점수를 계산한다."""
    score = 100
    issues = []
    
    # 제목 형식 검사
    if not check_title_format(markdown_content):
        score -= 20
        issues.append("제목 형식이 표준을 준수하지 않습니다")
    
    # 설계 규칙 섹션 검사
    if not check_design_rules_section(markdown_content):
        score -= 30
        issues.append("설계 규칙 섹션이 누락되었습니다")
    
    # 규칙 형식 검사
    rule_issues = check_rule_format(markdown_content)
    score -= len(rule_issues) * 3
    issues.extend(rule_issues)
    
    return {
        'score': max(0, score),
        'issues': issues,
        'quality_level': get_quality_level(score)
    }
```

### 3.2 규칙 추출 및 검증
```python
def extract_and_validate_rules(markdown_content):
    """문서에서 규칙을 추출하고 형식을 검증한다."""
    rules = []
    issues = []
    
    # 규칙 패턴 매칭
    rule_pattern = r'\*\*RULE-([A-Z]+)-([0-9]+)\*\*\s*\(([A-Z\s]+)\):\s*([^\n]+)'
    matches = re.findall(rule_pattern, markdown_content)
    
    for match in matches:
        rule = {
            'id': f"RULE-{match[0]}-{match[1]}",
            'type': match[2].strip(),
            'content': match[3].strip()
        }
        
        # 규칙 유효성 검사
        if not validate_rule(rule):
            issues.append(f"규칙 {rule['id']} 형식이 올바르지 않습니다")
        
        rules.append(rule)
    
    return rules, issues
```

## 4. API 설계 (새로 추가됨)

### 4.1 기존 speclint_lint 인터페이스 (문서 내용 직접 검사)
```python
@mcp.tool()
async def speclint_lint(
    content: str,
    check_type: str = "full"
) -> dict:
    """문서 내용 직접 품질 검사
    
    Args:
        content: 검사할 문서 내용 (필수)
        check_type: 검사 유형 ("full", "basic", "structure")
    
    Returns:
        dict: {
            "score": int,  # 0-100 점수
            "violations": List[dict],
            "suggestions": List[str],
            "metadata": dict
        }
    """
    return await speclint_engine.lint(content, check_type)
```

### 4.2 파일 기반 사용 가이드 (단일 인터페이스 활용)
```python
# 파일 경로를 사용하는 경우에도 speclint_lint를 그대로 사용
import aiofiles

async def lint_file(markdown_file_path: str, check_type: str = "full"):
    async with aiofiles.open(markdown_file_path, 'r', encoding='utf-8') as f:
        content = await f.read()
    return await speclint_lint(content=content, check_type=check_type)
```

### 4.3 사용 예시
```python
# 방법 1: 문서 내용 직접 검사
result1 = await speclint_lint("""
# [SpecGate] API 설계서
## 2. 설계 규칙
- **RULE-API-001** (MUST): 모든 API는 RESTful 원칙을 따라야 한다
""")

# 방법 2: 저장된 파일 검사 (새로운 워크플로우)
result2 = await check_document_quality("markdown_files/converted_20241219_143025.md")
```

## 5. 품질 등급별 처리

### 4.1 자동 승인 (90점 이상)
```python
def process_high_quality_document(document, score):
    """고품질 문서 처리"""
    return {
        'status': 'auto_approve',
        'message': '✅ 문서가 표준을 준수합니다. Phase 2 진행 가능합니다.',
        'next_action': 'proceed_to_phase2',
        'score': score
    }
```

### 4.2 HITL 검토 (70-89점)
```python
def process_medium_quality_document(document, score, issues):
    """중품질 문서 처리 - HITL 검토 필요"""
    return {
        'status': 'hitl_review_required',
        'message': f'⚠️ HITL 검토가 필요합니다. 품질 점수: {score}점',
        'next_action': 'create_hitl_issue',
        'score': score,
        'issues': issues
    }
```

### 4.3 필수 수정 (70점 미만)
```python
def process_low_quality_document(document, score, issues):
    """저품질 문서 처리 - 필수 수정"""
    return {
        'status': 'mandatory_fix_required',
        'message': f'❌ 문서 수정이 필수입니다. 품질 점수: {score}점',
        'next_action': 'create_mandatory_fix_issue',
        'score': score,
        'issues': issues
    }
```

## 5. 배치 처리

### 5.1 다중 문서 처리
```python
def process_batch_documents(documents):
    """여러 문서를 배치로 처리한다."""
    results = []
    total_score = 0
    
    for doc in documents:
        result = analyze_document_structure(doc['content'])
        results.append({
            'document_id': doc['id'],
            'title': doc['title'],
            'score': result['score'],
            'quality_level': result['quality_level'],
            'issues': result['issues']
        })
        total_score += result['score']
    
    return {
        'results': results,
        'average_score': total_score / len(documents),
        'total_documents': len(documents)
    }
```

## 6. 개선 사항 제안

### 6.1 자동 수정 제안
```python
IMPROVEMENT_SUGGESTIONS = {
    'title_format': {
        'pattern': r'^#\s*(.+?)\s*$',
        'suggestion': '제목을 "[프로젝트명] [문서유형] 설계서" 형식으로 수정하세요'
    },
    'rule_format': {
        'pattern': r'-\s*([^:]+):\s*(.+)',
        'suggestion': '규칙을 "**RULE-[영역]-[번호]** (유형): [규칙]" 형식으로 수정하세요'
    },
    'missing_section': {
        'suggestion': '누락된 섹션에 대한 템플릿을 제공합니다'
    }
}
```

## 7. 에러 처리 시나리오

### 7.1 문서 파싱 에러
```python
def handle_parsing_error(error: Exception, document_id: str) -> dict:
    """문서 파싱 실패 시 처리"""
    logging.error(f"문서 파싱 실패 - ID: {document_id}, 에러: {str(error)}")
    return {
        'status': 'error',
        'score': 0,
        'message': '문서 파싱에 실패했습니다. 문서 형식을 확인해주세요.',
        'error_type': 'parsing_error',
        'document_id': document_id
    }
```

### 7.2 정규식 매칭 실패
```python
def handle_regex_mismatch(rule_id: str, content: str) -> dict:
    """정규식 매칭 실패 시 처리"""
    logging.warning(f"규칙 형식 불일치 - Rule: {rule_id}")
    return {
        'type': 'regex_mismatch',
        'rule_id': rule_id,
        'message': f'규칙 {rule_id}의 형식이 올바르지 않습니다',
        'penalty': 3
    }
```

### 7.3 GitHub API 실패
```python
def handle_github_api_error(error: Exception, document_info: dict) -> dict:
    """GitHub Issue 생성 실패 시 처리"""
    logging.error(f"GitHub API 실패 - 문서: {document_info['title']}, 에러: {str(error)}")
    return {
        'status': 'github_api_error',
        'message': 'GitHub Issue 생성에 실패했습니다. 수동으로 검토해주세요.',
        'document_info': document_info,
        'fallback_action': 'manual_review_required'
    }
```

### 7.4 배치 처리 중 부분 실패
```python
def handle_batch_partial_failure(successful_docs: list, failed_docs: list) -> dict:
    """배치 처리 중 일부 문서 실패 시 처리"""
    return {
        'status': 'partial_success',
        'successful_count': len(successful_docs),
        'failed_count': len(failed_docs),
        'successful_documents': successful_docs,
        'failed_documents': failed_docs,
        'message': f'{len(successful_docs)}개 문서 처리 완료, {len(failed_docs)}개 문서 실패'
    }
```

### 7.5 메모리 부족 에러
```python
def handle_memory_error(document_size: int) -> dict:
    """메모리 부족 시 처리"""
    logging.error(f"메모리 부족 - 문서 크기: {document_size} bytes")
    return {
        'status': 'memory_error',
        'score': 0,
        'message': '문서가 너무 큽니다. 문서를 분할하여 처리해주세요.',
        'max_size': 10 * 1024 * 1024,  # 10MB
        'document_size': document_size
    }
```

### 7.6 네트워크 타임아웃
```python
def handle_timeout_error(operation: str, timeout_seconds: int) -> dict:
    """네트워크 타임아웃 시 처리"""
    logging.error(f"타임아웃 발생 - 작업: {operation}, 제한시간: {timeout_seconds}초")
    return {
        'status': 'timeout_error',
        'operation': operation,
        'timeout_seconds': timeout_seconds,
        'message': f'{operation} 작업이 {timeout_seconds}초 내에 완료되지 않았습니다.',
        'retry_recommended': True
    }
```

### 7.7 에러 처리 우선순위
1. **치명적 에러**: 문서 파싱 실패, 메모리 부족 → 즉시 중단, 0점 반환
2. **경고 에러**: 정규식 매칭 실패 → 점수 차감, 계속 진행
3. **외부 의존성 에러**: GitHub API 실패 → 로그 기록, 대체 프로세스 실행
4. **성능 에러**: 타임아웃 → 재시도 제안, 부분 결과 반환

## 8. 성능 요구사항

### 8.1 응답 시간 요구사항
```python
PERFORMANCE_REQUIREMENTS = {
    'single_document': {
        'max_processing_time': 5.0,  # 5초 이내
        'target_time': 2.0,          # 목표 2초
        'timeout': 10.0              # 최대 10초
    },
    'batch_processing': {
        'max_processing_time': 30.0,  # 30초 이내 (10개 문서)
        'target_time': 15.0,          # 목표 15초
        'timeout': 60.0               # 최대 60초
    },
    'github_api': {
        'max_response_time': 3.0,     # 3초 이내
        'retry_attempts': 3,          # 최대 3회 재시도
        'retry_delay': 1.0            # 1초 간격
    }
}
```

### 8.2 메모리 사용량 제한
```python
MEMORY_REQUIREMENTS = {
    'per_document': {
        'max_size': 10 * 1024 * 1024,  # 10MB per document
        'warning_threshold': 8 * 1024 * 1024,  # 8MB 경고
        'rejection_threshold': 15 * 1024 * 1024  # 15MB 거부
    },
    'total_memory': {
        'max_usage': 100 * 1024 * 1024,  # 100MB 총 사용량
        'gc_threshold': 80 * 1024 * 1024   # 80MB에서 가비지 컬렉션
    }
}
```

### 8.3 동시 처리 제한
```python
CONCURRENCY_LIMITS = {
    'max_concurrent_documents': 5,     # 최대 5개 문서 동시 처리
    'max_concurrent_github_requests': 3,  # 최대 3개 GitHub API 동시 요청
    'rate_limit': {
        'github_api': 60,              # 분당 60회
        'confluence_api': 100          # 분당 100회
    }
}
```

### 8.4 성능 모니터링
```python
def monitor_performance(operation: str, start_time: float, end_time: float) -> dict:
    """성능 모니터링 및 로깅"""
    processing_time = end_time - start_time
    
    # 성능 임계치 확인
    if operation == 'single_document' and processing_time > 5.0:
        logging.warning(f"단일 문서 처리 시간 초과: {processing_time:.2f}초")
    elif operation == 'batch_processing' and processing_time > 30.0:
        logging.warning(f"배치 처리 시간 초과: {processing_time:.2f}초")
    
    return {
        'operation': operation,
        'processing_time': processing_time,
        'timestamp': datetime.now().isoformat(),
        'performance_status': 'normal' if processing_time <= 5.0 else 'slow'
    }
```

### 8.5 성능 최적화 전략
1. **정규식 컴파일**: 자주 사용되는 정규식을 미리 컴파일
2. **메모리 관리**: 문서 처리 후 즉시 메모리 해제
3. **비동기 처리**: I/O 작업은 비동기로 처리
4. **캐싱**: 동일한 문서에 대한 중복 처리 방지
5. **배치 최적화**: 작은 문서들을 묶어서 처리

## 9. 테스트 시나리오

### 9.1 단위 테스트 시나리오
```python
# 테스트 데이터 준비
TEST_DOCUMENTS = {
    'perfect_document': '''
# [example_project] API 설계서

## 2. 설계 규칙
### 2.1 MUST 규칙 (필수)
- **RULE-API-001** (MUST): 모든 API 엔드포인트는 RESTful 원칙을 따라야 한다
  - 적용 범위: 모든 REST API
  - 근거: 일관된 API 설계를 통한 개발자 경험 향상
  - 참조: OpenAPI 3.0 스펙

## 3. 기술 스펙
### 3.1 API 설계 (OpenAPI)
```yaml
openapi: 3.0.0
info:
  title: Example API
  version: 1.0.0
```
''',
    'incomplete_document': '''
# API 설계서
## 설계 규칙
- 모든 API는 RESTful해야 함
''',
    'empty_document': '',
    'malformed_document': '''
# 잘못된 형식
## 설계 규칙
- RULE-API-001: API는 RESTful해야 함
'''
}

# 테스트 케이스 정의
TEST_CASES = [
    {
        'name': '완벽한 문서 테스트',
        'input': TEST_DOCUMENTS['perfect_document'],
        'expected_score': 95,
        'expected_violations': 0,
        'expected_status': 'auto_approve'
    },
    {
        'name': '불완전한 문서 테스트',
        'input': TEST_DOCUMENTS['incomplete_document'],
        'expected_score': 45,
        'expected_violations': 5,
        'expected_status': 'mandatory_fix_required'
    },
    {
        'name': '빈 문서 테스트',
        'input': TEST_DOCUMENTS['empty_document'],
        'expected_score': 0,
        'expected_violations': 1,
        'expected_status': 'error'
    },
    {
        'name': '잘못된 형식 문서 테스트',
        'input': TEST_DOCUMENTS['malformed_document'],
        'expected_score': 60,
        'expected_violations': 3,
        'expected_status': 'mandatory_fix_required'
    }
]
```

### 9.2 통합 테스트 시나리오
```python
# Confluence → SpecLint 통합 테스트
INTEGRATION_TEST_SCENARIOS = [
    {
        'name': '정상적인 문서 처리 플로우',
        'steps': [
            'confluence.fetch로 문서 수집',
            'HTML→MD 변환',
            'speclint.lint로 품질 검사',
            '결과에 따른 후속 처리'
        ],
        'expected_flow': 'confluence_fetch → html_to_md → speclint_lint → github_issue'
    },
    {
        'name': 'HITL 검토 플로우',
        'steps': [
            '70-89점 문서 검사',
            'GitHub Issue 생성',
            'HITL 검토 대기',
            '검토 결과 처리'
        ],
        'expected_flow': 'speclint_lint → github_issue_creation → hitl_review → approval'
    }
]
```

### 9.3 성능 테스트 시나리오
```python
PERFORMANCE_TEST_SCENARIOS = [
    {
        'name': '단일 문서 처리 성능',
        'test_data': '1MB 문서',
        'max_time': 5.0,
        'target_time': 2.0
    },
    {
        'name': '배치 처리 성능',
        'test_data': '10개 문서 (각 500KB)',
        'max_time': 30.0,
        'target_time': 15.0
    },
    {
        'name': '메모리 사용량 테스트',
        'test_data': '5MB 문서',
        'max_memory': 10 * 1024 * 1024,  # 10MB
        'expected_behavior': '정상 처리'
    },
    {
        'name': '대용량 문서 거부 테스트',
        'test_data': '20MB 문서',
        'max_memory': 15 * 1024 * 1024,  # 15MB
        'expected_behavior': '메모리 에러 반환'
    }
]
```

### 9.4 에러 처리 테스트 시나리오
```python
ERROR_HANDLING_TEST_SCENARIOS = [
    {
        'name': '문서 파싱 실패',
        'input': '잘못된 HTML 형식',
        'expected_error': 'parsing_error',
        'expected_score': 0,
        'expected_message': '문서 파싱에 실패했습니다'
    },
    {
        'name': 'GitHub API 실패',
        'input': '유효한 문서 (네트워크 오류 시뮬레이션)',
        'expected_error': 'github_api_error',
        'expected_fallback': 'manual_review_required'
    },
    {
        'name': '메모리 부족',
        'input': '15MB 문서',
        'expected_error': 'memory_error',
        'expected_message': '문서가 너무 큽니다'
    },
    {
        'name': '타임아웃',
        'input': '정상 문서 (느린 네트워크 시뮬레이션)',
        'expected_error': 'timeout_error',
        'expected_retry': True
    }
]
```

### 9.5 테스트 실행 계획
```python
TEST_EXECUTION_PLAN = {
    'unit_tests': {
        'priority': 'high',
        'coverage_target': 90,
        'execution_time': '5분'
    },
    'integration_tests': {
        'priority': 'high',
        'coverage_target': 80,
        'execution_time': '10분'
    },
    'performance_tests': {
        'priority': 'medium',
        'coverage_target': 70,
        'execution_time': '15분'
    },
    'error_handling_tests': {
        'priority': 'high',
        'coverage_target': 85,
        'execution_time': '10분'
    }
}
```
