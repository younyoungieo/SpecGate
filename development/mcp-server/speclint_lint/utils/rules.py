"""
SpecLint 품질 검사 규칙 정의

Confluence에서 가져온 설계 문서의 품질을 검사하기 위한
규칙과 점수 산정 기준을 정의합니다.

US-002의 요구사항에 따라 설계 문서의 표준화 여부를
0-100점으로 평가하는 규칙들을 포함합니다.

주요 규칙:
- 문서 구조 검사 (제목, 섹션, 규칙 형식)
- 품질 점수 산정 (차감 방식)
- 성능 및 메모리 요구사항
- 개선 제안 템플릿
"""

# 필수 구조 검사 규칙
STRUCTURE_CHECKS = {
    'title_format': {
        'pattern': r'^#\s*\[[^\]]+\]\s*(\[[^\]]+\]|\w+)\s*설계서\s*$',
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

# 품질 점수 산정 규칙
# 
# 점수 생성 기준:
# - 기본 점수: 100점에서 시작
# - 각 위반사항별로 차감점수 적용
# - 최종 점수 = 100 - 총 차감점수 (최소 0점)
#
# 임계값 기준:
# - 80점 이상: 자동 승인 (표준 완전 준수)
# - 60-79점: HITL 검토 필요 (부분적 개선 필요)
# - 60점 미만: 필수 수정 (표준 미준수)
#
# 기준 완화 이유:
# - 초기 도입 단계에서 너무 엄격한 기준은 도구 사용을 저해
# - 점진적 품질 향상을 통한 조직 문화 개선 목표
QUALITY_SCORING = {
    'base_score': 100,
    'deductions': {
        # 구조적 문제 (큰 차감)
        'title_format_mismatch': -20,    # 제목 형식 불일치
        'design_rules_missing': -30,     # 설계 규칙 섹션 누락
        'technical_spec_missing': -25,   # 기술 스펙 섹션 누락
        'parsing_error': -100,           # 치명적 파싱 에러
        
        # 규칙 관련 문제 (중간 차감)
        'rule_spec_relation_missing': -10,  # 규칙-스펙 연관성 누락
        'design_rules_keywords_missing': -10,  # 설계 규칙 키워드 누락
        'design_rules_insufficient': -15,     # 설계 규칙 부족
        'no_rules_found': -15,               # 규칙 전혀 없음
        
        # 개별 규칙 문제 (규칙당 차감)
        'rule_id_format_mismatch': -3,   # 규칙 ID 형식 불일치 (규칙당)
        'rule_type_mismatch': -2,        # 규칙 타입 불일치 (규칙당)
        'scope_missing': -2,             # 적용 범위 누락 (규칙당)
        'reason_missing': -2,            # 근거 누락 (규칙당)
        'rule_content_too_short': -1,    # 규칙 내용 너무 짧음 (규칙당)
        
        # 기타 문제 (소액 차감)
        'reference_missing': -1,         # 참조 정보 누락 (규칙당)
        'code_example_missing': -5,      # 코드 예시 누락
        'change_history_missing': -5     # 변경 이력 누락
    },
    'thresholds': {
        'high_quality': 80,      # 자동 승인 (기준 완화)
        'medium_quality': 60,    # HITL 검토 (기준 완화)
        'low_quality': 0         # 필수 수정
    }
}

# 개선 제안 매핑
IMPROVEMENT_SUGGESTIONS = {
    'parsing_error': "문서 내용을 확인하고 올바른 형식으로 작성하세요.",
    'title_format_mismatch': "제목을 '[프로젝트명] [문서유형] 설계서' 형식으로 수정하세요. 예: '[SpecGate] API 설계서'",
    'design_rules_missing': "## 2. 설계 규칙 섹션을 추가하고 설계 원칙을 명시하세요.",
    'technical_spec_missing': "## 3. 기술 스펙 섹션을 추가하고 기술적 세부사항을 설명하세요.",
    'no_rules_found': "설계 규칙을 **RULE-[영역]-[번호]** (유형): [규칙] 형식으로 추가하세요.",
    'rule_type_mismatch': "규칙 유형을 MUST, SHOULD, MUST NOT, MAY, SHOULD NOT 중 하나로 수정하세요.",
    'rule_content_too_short': "규칙 내용을 더 구체적이고 명확하게 작성하세요.",
    'code_example_missing': "코드 예제를 ```코드블록``` 형식으로 추가하세요.",
    'change_history_missing': "## 4. 변경 이력 섹션을 추가하여 문서 변경 사항을 추적하세요."
}

# 성능 요구사항
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
    }
}

# 메모리 사용량 제한
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


