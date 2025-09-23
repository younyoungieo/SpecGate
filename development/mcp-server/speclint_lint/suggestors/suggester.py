"""
SpecLint 개선 제안 생성기

문서 품질 검사 결과를 바탕으로 구체적인 개선 제안을 생성하는 모듈입니다.
US-002의 품질 검사 결과에 따라 사용자에게 실용적인 수정 방향을 제시합니다.
"""
import logging
from typing import List, Dict, Any, Set
from speclint_lint.utils.rules import IMPROVEMENT_SUGGESTIONS


class ImprovementSuggester:
    """개선 제안 생성기
    
    문서 품질 검사에서 발견된 위반 사항들을 분석하여
    구체적이고 실행 가능한 개선 제안을 생성합니다.
    """
    
    def __init__(self):
        self.suggestions = IMPROVEMENT_SUGGESTIONS
        self.logger = logging.getLogger("specgate.speclint.suggester")
    
    async def generate_suggestions(self, violations: List[Dict[str, Any]]) -> List[str]:
        """위반 사항에 따른 개선 제안 생성
        
        Args:
            violations: 위반 사항 목록
            
        Returns:
            List[str]: 개선 제안 목록
        """
        if not violations:
            return ["문서가 표준을 잘 준수하고 있습니다."]
        
        suggestions = []
        processed_types: Set[str] = set()
        
        # 위반 사항에 따른 제안 생성
        for violation in violations:
            violation_type = violation.get("type")
            if violation_type and violation_type not in processed_types:
                suggestion = self._get_suggestion_for_violation(violation_type)
                if suggestion:
                    suggestions.append(suggestion)
                    processed_types.add(violation_type)
        
        # 중복 제거 및 정렬
        suggestions = list(dict.fromkeys(suggestions))  # 순서 유지하면서 중복 제거
        
        # 일반적인 개선 제안 추가
        if suggestions:
            suggestions.append("위의 제안사항을 적용하여 문서 품질을 향상시키세요.")
        
        self.logger.info(f"생성된 개선 제안: {len(suggestions)}개")
        return suggestions
    
    def _get_suggestion_for_violation(self, violation_type: str) -> str:
        """특정 위반 사항에 대한 제안 반환
        
        Args:
            violation_type: 위반 사항 유형
            
        Returns:
            str: 개선 제안 메시지
        """
        suggestion = self.suggestions.get(violation_type)
        if not suggestion:
            self.logger.warning(f"알 수 없는 위반 사항 유형: {violation_type}")
            return f"'{violation_type}' 유형의 위반 사항을 수정하세요."
        
        return suggestion
    
    def get_suggestion_for_violation(self, violation_type: str) -> str:
        """특정 위반 사항에 대한 제안 반환 (공개 메서드)
        
        Args:
            violation_type: 위반 사항 유형
            
        Returns:
            str: 개선 제안 메시지
        """
        return self._get_suggestion_for_violation(violation_type)
    
    def get_all_suggestions(self) -> Dict[str, str]:
        """모든 제안 반환
        
        Returns:
            Dict[str, str]: 위반 사항 유형별 제안 사항
        """
        return self.suggestions.copy()
    
    def add_custom_suggestion(self, violation_type: str, suggestion: str) -> None:
        """사용자 정의 제안 추가
        
        Args:
            violation_type: 위반 사항 유형
            suggestion: 제안 메시지
        """
        self.suggestions[violation_type] = suggestion
        self.logger.info(f"사용자 정의 제안 추가: {violation_type}")
    
    def get_suggestion_count(self) -> int:
        """제안 사항 개수 반환
        
        Returns:
            int: 제안 사항 개수
        """
        return len(self.suggestions)
