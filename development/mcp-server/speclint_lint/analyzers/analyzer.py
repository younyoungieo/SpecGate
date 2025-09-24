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
        # 제목 패턴을 더 유연하게 허용
        self.title_patterns = [
            r'^#\s*\[[^\]]+\]\s*(\[[^\]]+\]|\w+)\s*설계서\s*$',  # [프로젝트] [유형] 설계서
            r'^#\s*\[[^\]]+\]\s*[A-Za-z가-힣\s]+\s*설계서\s*$',  # [프로젝트] API 설계서
            r'^#\s*[A-Za-z가-힣\s]+\s*설계서\s*$'  # SpecGate API 설계서
        ]
        
        self._compiled_patterns = {
            'title_format': [re.compile(pattern, re.MULTILINE) for pattern in self.title_patterns],
            'design_rules_section': re.compile(self.checks['design_rules_section']['pattern'], re.IGNORECASE),
            'technical_spec_section': re.compile(self.checks['technical_spec_section']['pattern'], re.IGNORECASE),
            'rule_format': re.compile(self.checks['rule_format']['pattern'])
        }
    
    async def analyze(self, content: str, document_title: Optional[str] = None) -> Dict[str, Any]:
        """문서 구조를 분석하고 점수를 계산한다.
        
        Args:
            content: 분석할 문서 내용
            document_title: Confluence 문서의 실제 제목 (선택사항)
            
        Returns:
            Dict[str, Any]: 구조 분석 결과
        """
        if not content or not content.strip():
            self.logger.warning("빈 문서 분석 요청")
            return self._create_empty_result()
        
        try:
            # 제목 형식 검사 (Confluence 제목 우선 사용)
            title_result = self._check_title_format(content, document_title)
            
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
                title_result, design_rules_result, technical_spec_result, rule_count, content
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
    
    def _check_title_format(self, content: str, document_title: Optional[str] = None) -> Dict[str, Any]:
        """제목 형식 검사
        
        Args:
            content: 문서 내용
            document_title: Confluence 문서의 실제 제목 (선택사항)
            
        Returns:
            Dict[str, Any]: 제목 형식 검사 결과
        """
        try:
            # Confluence 문서 제목이 있으면 우선 사용
            if document_title:
                self.logger.info(f"Confluence 문서 제목으로 검사: {document_title}")
                # Confluence 제목을 Markdown 형식으로 변환하여 검사
                confluence_title = f"# {document_title}"
                
                patterns = self._compiled_patterns['title_format']
                match = None
                matched_pattern = None
                
                for i, pattern in enumerate(patterns):
                    match = pattern.search(confluence_title)
                    if match:
                        matched_pattern = self.title_patterns[i]
                        break
                
                return {
                    "valid": bool(match),
                    "pattern": matched_pattern or self.checks['title_format']['pattern'],
                    "description": self.checks['title_format']['description'],
                    "match": match.group() if match else confluence_title,
                    "weight": self.checks['title_format']['weight'],
                    "source": "confluence_title"
                }
            else:
                # 기존 방식: Markdown 내용에서 제목 검색
                patterns = self._compiled_patterns['title_format']
                match = None
                matched_pattern = None
                
                for i, pattern in enumerate(patterns):
                    match = pattern.search(content)
                    if match:
                        matched_pattern = self.title_patterns[i]
                        break
                
                return {
                    "valid": bool(match),
                    "pattern": matched_pattern or self.checks['title_format']['pattern'],
                    "description": self.checks['title_format']['description'],
                    "match": match.group() if match else None,
                    "weight": self.checks['title_format']['weight'],
                    "source": "markdown_content"
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
                                 rule_count: int, content: str) -> int:
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
            
            # 규칙 개수 점수 (10점)
            if rule_count >= 5:  # 최소 5개 규칙 이상
                rule_score = 10  # 고정 점수
            elif rule_count > 0:
                rule_score = rule_count * 2  # 부족하면 개수에 비례 (최대 8점)
            else:
                rule_score = 0  # 규칙이 없으면 0점
            
            score += rule_score
            
            # 코드 블록 존재 점수 (10점)
            code_blocks = self._count_code_blocks(content)
            if code_blocks > 0:
                score += 10
            
            # 변경 이력 존재 점수 (5점)
            if self._has_change_history(content):
                score += 5
            
            final_score = min(score, 100)  # 최대 100점
            self.logger.debug(f"구조 점수 계산: {final_score} (기본: {score})")
            return final_score
            
        except Exception as e:
            self.logger.error(f"구조 점수 계산 중 오류: {e}")
            return 0
    
    def _count_code_blocks(self, content: str) -> int:
        """코드 블록 개수 계산"""
        try:
            # 다양한 코드 블록 패턴 검사
            code_patterns = [
                r'```[\s\S]*?```',  # 기본 코드 블록
                r'```python[\s\S]*?```',  # Python 코드 블록
                r'```javascript[\s\S]*?```',  # JavaScript 코드 블록
                r'```json[\s\S]*?```',  # JSON 코드 블록
                r'```yaml[\s\S]*?```',  # YAML 코드 블록
                r'```xml[\s\S]*?```',  # XML 코드 블록
                r'```sql[\s\S]*?```',  # SQL 코드 블록
                r'```bash[\s\S]*?```',  # Bash 코드 블록
                r'```shell[\s\S]*?```',  # Shell 코드 블록
            ]
            
            total_blocks = 0
            for pattern in code_patterns:
                matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                total_blocks += len(matches)
            
            self.logger.debug(f"발견된 코드 블록 개수: {total_blocks}")
            return total_blocks
            
        except Exception as e:
            self.logger.error(f"코드 블록 계산 중 오류: {e}")
            return 0
    
    def _has_change_history(self, content: str) -> bool:
        """변경 이력 섹션 존재 여부 확인"""
        try:
            # 변경 이력 섹션 패턴들
            change_history_patterns = [
                r'##\s*[0-9]+\.\s*변경\s*이력',
                r'##\s*[0-9]+\.\s*changelog',
                r'##\s*[0-9]+\.\s*version',
                r'##\s*[0-9]+\.\s*history',
                r'##\s*[0-9]+\.\s*revision'
            ]
            
            for pattern in change_history_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    self.logger.debug("변경 이력 섹션 발견")
                    return True
            
            self.logger.debug("변경 이력 섹션 없음")
            return False
            
        except Exception as e:
            self.logger.error(f"변경 이력 검사 중 오류: {e}")
            return False


