"""
SpecLint 문서 구조 분석기

Confluence에서 가져온 설계 문서의 구조를 분석하고
SpecGate 표준 템플릿 준수 여부를 평가하는 모듈입니다.

주요 분석 항목:
- 제목 형식 검사 ([프로젝트명] [문서유형] 설계서)
- 설계 규칙 섹션 존재 여부
- 기술 스펙 섹션 존재 여부
- 규칙 형식 및 개수 분석
- 문서 기본 통계 (단어 수, 줄 수 등)
"""
import re
import logging
from typing import Dict, List, Any, Optional
from speclint_lint.utils.rules import STRUCTURE_CHECKS


class DocumentStructureAnalyzer:
    """문서 구조 분석기
    
    설계 문서의 구조적 요소들을 분석하여
    SpecGate 표준 템플릿 준수 여부를 평가합니다.
    """
    
    def __init__(self):
        self.checks = STRUCTURE_CHECKS
        self.logger = logging.getLogger("specgate.speclint.analyzer")
        
        # 정규식 패턴 미리 컴파일 (성능 최적화)
        self._compiled_patterns = {
            'title_format': re.compile(self.checks['title_format']['pattern'], re.MULTILINE),
            'design_rules_section': re.compile(self.checks['design_rules_section']['pattern'], re.IGNORECASE),
            'technical_spec_section': re.compile(self.checks['technical_spec_section']['pattern'], re.IGNORECASE),
            'rule_format': re.compile(self.checks['rule_format']['pattern'])
        }
    
    async def analyze(self, content: str) -> Dict[str, Any]:
        """문서 구조를 분석하고 점수를 계산한다.
        
        Args:
            content: 분석할 문서 내용
            
        Returns:
            Dict[str, Any]: 구조 분석 결과
        """
        if not content or not content.strip():
            self.logger.warning("빈 문서 분석 요청")
            return self._create_empty_result()
        
        try:
            # 제목 형식 검사
            title_result = self._check_title_format(content)
            
            # 설계 규칙 섹션 검사
            design_rules_result = self._check_design_rules_section(content)
            
            # 기술 스펙 섹션 검사
            technical_spec_result = self._check_technical_spec_section(content)
            
            # 규칙 개수 계산
            rule_count = self._count_rules(content)
            
            # 기본 통계
            word_count = len(content.split())
            line_count = len(content.split('\n'))
            
            # 구조 점수 계산
            structure_score = self._calculate_structure_score(
                title_result, design_rules_result, technical_spec_result, rule_count
            )
            
            result = {
                "has_title": title_result["valid"],
                "has_design_rules_section": design_rules_result["valid"],
                "has_technical_spec_section": technical_spec_result["valid"],
                "rule_count": rule_count,
                "title_format_valid": title_result["valid"],
                "word_count": word_count,
                "line_count": line_count,
                "structure_score": structure_score,
                "details": {
                    "title": title_result,
                    "design_rules": design_rules_result,
                    "technical_spec": technical_spec_result
                }
            }
            
            self.logger.info(f"문서 구조 분석 완료 - 점수: {structure_score}, 규칙: {rule_count}개")
            return result
            
        except Exception as e:
            self.logger.error(f"문서 구조 분석 중 오류: {e}")
            return self._create_error_result(str(e))
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """빈 문서에 대한 결과 생성"""
        return {
            "has_title": False,
            "has_design_rules_section": False,
            "has_technical_spec_section": False,
            "rule_count": 0,
            "title_format_valid": False,
            "word_count": 0,
            "line_count": 0,
            "structure_score": 0,
            "details": {},
            "error": "빈 문서"
        }
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """에러 발생 시 결과 생성"""
        return {
            "has_title": False,
            "has_design_rules_section": False,
            "has_technical_spec_section": False,
            "rule_count": 0,
            "title_format_valid": False,
            "word_count": 0,
            "line_count": 0,
            "structure_score": 0,
            "details": {},
            "error": error_message
        }
    
    def _check_title_format(self, content: str) -> Dict[str, Any]:
        """제목 형식 검사
        
        Args:
            content: 문서 내용
            
        Returns:
            Dict[str, Any]: 제목 형식 검사 결과
        """
        try:
            pattern = self._compiled_patterns['title_format']
            match = pattern.search(content)
            
            return {
                "valid": bool(match),
                "pattern": self.checks['title_format']['pattern'],
                "description": self.checks['title_format']['description'],
                "match": match.group() if match else None,
                "weight": self.checks['title_format']['weight']
            }
        except Exception as e:
            self.logger.error(f"제목 형식 검사 중 오류: {e}")
            return {
                "valid": False,
                "pattern": self.checks['title_format']['pattern'],
                "description": self.checks['title_format']['description'],
                "error": str(e),
                "weight": self.checks['title_format']['weight']
            }
    
    def _check_design_rules_section(self, content: str) -> Dict[str, Any]:
        """설계 규칙 섹션 검사
        
        Args:
            content: 문서 내용
            
        Returns:
            Dict[str, Any]: 설계 규칙 섹션 검사 결과
        """
        try:
            pattern = self._compiled_patterns['design_rules_section']
            match = pattern.search(content)
            
            return {
                "valid": bool(match),
                "pattern": self.checks['design_rules_section']['pattern'],
                "description": self.checks['design_rules_section']['description'],
                "match": match.group() if match else None,
                "weight": self.checks['design_rules_section']['weight']
            }
        except Exception as e:
            self.logger.error(f"설계 규칙 섹션 검사 중 오류: {e}")
            return {
                "valid": False,
                "pattern": self.checks['design_rules_section']['pattern'],
                "description": self.checks['design_rules_section']['description'],
                "error": str(e),
                "weight": self.checks['design_rules_section']['weight']
            }
    
    def _check_technical_spec_section(self, content: str) -> Dict[str, Any]:
        """기술 스펙 섹션 검사
        
        Args:
            content: 문서 내용
            
        Returns:
            Dict[str, Any]: 기술 스펙 섹션 검사 결과
        """
        try:
            pattern = self._compiled_patterns['technical_spec_section']
            match = pattern.search(content)
            
            return {
                "valid": bool(match),
                "pattern": self.checks['technical_spec_section']['pattern'],
                "description": self.checks['technical_spec_section']['description'],
                "match": match.group() if match else None,
                "weight": self.checks['technical_spec_section']['weight']
            }
        except Exception as e:
            self.logger.error(f"기술 스펙 섹션 검사 중 오류: {e}")
            return {
                "valid": False,
                "pattern": self.checks['technical_spec_section']['pattern'],
                "description": self.checks['technical_spec_section']['description'],
                "error": str(e),
                "weight": self.checks['technical_spec_section']['weight']
            }
    
    def _count_rules(self, content: str) -> int:
        """규칙 개수 계산
        
        Args:
            content: 문서 내용
            
        Returns:
            int: 발견된 규칙 개수
        """
        try:
            pattern = self._compiled_patterns['rule_format']
            matches = pattern.findall(content)
            count = len(matches)
            self.logger.debug(f"발견된 규칙 개수: {count}")
            return count
        except Exception as e:
            self.logger.error(f"규칙 개수 계산 중 오류: {e}")
            return 0
    
    def _calculate_structure_score(self, title_result: Dict[str, Any], 
                                 design_rules_result: Dict[str, Any],
                                 technical_spec_result: Dict[str, Any],
                                 rule_count: int) -> int:
        """구조 점수 계산
        
        Args:
            title_result: 제목 형식 검사 결과
            design_rules_result: 설계 규칙 섹션 검사 결과
            technical_spec_result: 기술 스펙 섹션 검사 결과
            rule_count: 규칙 개수
            
        Returns:
            int: 구조 점수 (0-100)
        """
        try:
            score = 0
            
            # 제목 형식 점수
            if title_result.get("valid", False):
                score += title_result.get("weight", 0)
            
            # 설계 규칙 섹션 점수
            if design_rules_result.get("valid", False):
                score += design_rules_result.get("weight", 0)
            
            # 기술 스펙 섹션 점수
            if technical_spec_result.get("valid", False):
                score += technical_spec_result.get("weight", 0)
            
            # 규칙 개수 점수 (규칙당 3점, 최대 30점)
            if rule_count > 0:
                rule_score = min(rule_count * self.checks['rule_format']['weight'], 30)
                score += rule_score
            
            final_score = min(score, 100)  # 최대 100점
            self.logger.debug(f"구조 점수 계산: {final_score} (기본: {score})")
            return final_score
            
        except Exception as e:
            self.logger.error(f"구조 점수 계산 중 오류: {e}")
            return 0


