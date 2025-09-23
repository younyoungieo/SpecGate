"""
SpecLint - 문서 품질 검사 시스템

Confluence에서 가져온 설계 문서의 표준화 여부를 검사하고
0-100점 점수로 품질을 평가하는 시스템입니다.

주요 기능:
- 문서 구조 분석 (제목, 섹션, 규칙 형식 등)
- 템플릿 준수 검사 (SpecGate 표준 템플릿)
- 품질 점수 계산 (0-100점)
- 개선 제안 생성
- 배치 처리 지원

사용 예시:
    from speclint_lint import SpecLint
    
    speclint = SpecLint()
    result = await speclint.lint(document_content, 'full')
    print(f"품질 점수: {result['score']}/100")
"""

from speclint_lint.analyzers import DocumentStructureAnalyzer
from speclint_lint.validators import TemplateValidator
from speclint_lint.scorers import QualityScorer
from speclint_lint.suggestors import ImprovementSuggester
from .speclint import SpecLint
from speclint_lint.utils import (
    QUALITY_SCORING, 
    PERFORMANCE_REQUIREMENTS, 
    MEMORY_REQUIREMENTS,
    STRUCTURE_CHECKS,
    IMPROVEMENT_SUGGESTIONS
)

__version__ = "1.0.0"
__author__ = "SpecGate Team"

__all__ = [
    'SpecLint',
    'DocumentStructureAnalyzer',
    'TemplateValidator', 
    'QualityScorer',
    'ImprovementSuggester',
    'QUALITY_SCORING',
    'PERFORMANCE_REQUIREMENTS',
    'MEMORY_REQUIREMENTS',
    'STRUCTURE_CHECKS',
    'IMPROVEMENT_SUGGESTIONS'
]
