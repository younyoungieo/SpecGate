"""
SpecLint 템플릿 준수 검사기
문서가 표준 템플릿을 준수하는지 검사하는 모듈
"""
import re
from typing import Dict, List, Any
from speclint_lint.utils.rules import QUALITY_SCORING


class TemplateValidator:
    """템플릿 준수 검사기"""
    
    def __init__(self):
        self.scoring = QUALITY_SCORING
    
    async def validate(self, content: str, check_type: str = "full") -> List[Dict[str, Any]]:
        """템플릿 준수 검사"""
        violations = []
        
        # 빈 문서 검사
        if not content or not content.strip():
            violations.append(self._create_violation(
                "parsing_error", 
                "문서 파싱에 실패했습니다",
                self.scoring['deductions']['parsing_error']
            ))
            return violations
        
        # 기본 검사 (모든 check_type에 적용)
        if check_type in ["basic", "structure", "full"]:
            violations.extend(self._check_basic_requirements(content))
        
        # 구조 검사 (structure, full)
        if check_type in ["structure", "full"]:
            violations.extend(self._check_structure_requirements(content))
        
        # 전체 검사 (full)
        if check_type == "full":
            violations.extend(self._check_full_requirements(content))
        
        return violations
    
    def _check_basic_requirements(self, content: str) -> List[Dict[str, Any]]:
        """기본 요구사항 검사"""
        violations = []
        
        # 제목 형식 검사 - 더 유연한 패턴 허용
        title_patterns = [
            r'^#\s*\[[^\]]+\]\s*(\[[^\]]+\]|\w+)\s*설계서\s*$',  # [프로젝트] [유형] 설계서
            r'^#\s*\[[^\]]+\]\s*[A-Za-z가-힣\s]+\s*설계서\s*$',  # [프로젝트] API 설계서
            r'^#\s*[A-Za-z가-힣\s]+\s*설계서\s*$'  # SpecGate API 설계서
        ]
        
        title_match = False
        for pattern in title_patterns:
            if re.search(pattern, content, re.MULTILINE):
                title_match = True
                break
        
        if not title_match:
            violations.append(self._create_violation(
                "title_format_mismatch",
                "제목 형식이 표준을 준수하지 않습니다. '프로젝트명 문서유형 설계서' 또는 '[프로젝트명] [문서유형] 설계서' 형식을 사용하세요.",
                self.scoring['deductions']['title_format_mismatch']
            ))
        
        # 설계 규칙 섹션 검사
        design_rules_pattern = r'##\s*2\.\s*설계\s*규칙'
        if not re.search(design_rules_pattern, content, re.IGNORECASE):
            violations.append(self._create_violation(
                "design_rules_missing",
                "설계 규칙 섹션이 누락되었습니다.",
                self.scoring['deductions']['design_rules_missing']
            ))
        
        return violations
    
    def _check_structure_requirements(self, content: str) -> List[Dict[str, Any]]:
        """구조 요구사항 검사"""
        violations = []
        
        # 기술 스펙 섹션 검사
        technical_spec_pattern = r'##\s*3\.\s*기술\s*스펙'
        if not re.search(technical_spec_pattern, content, re.IGNORECASE):
            violations.append(self._create_violation(
                "technical_spec_missing",
                "기술 스펙 섹션이 누락되었습니다.",
                self.scoring['deductions']['technical_spec_missing']
            ))
        
        # 설계 규칙 내용 검사 (US-002 목적에 맞게)
        design_rules_section = self._extract_section(content, r'##\s*2\.\s*설계\s*규칙')
        if design_rules_section:
            violations.extend(self._check_design_rules_content(design_rules_section))
        
        return violations
    
    def _check_full_requirements(self, content: str) -> List[Dict[str, Any]]:
        """전체 요구사항 검사"""
        violations = []
        
        # 설계 규칙 내용 검사
        design_rules_section = self._extract_section(content, r'##\s*2\.\s*설계\s*규칙')
        if design_rules_section:
            violations.extend(self._check_design_rules_content(design_rules_section))
        
        # 코드 예제 검사 - 더 정확한 패턴 사용
        code_patterns = [
            r'```[\s\S]*?```',  # 기본 코드 블록
            r'```python[\s\S]*?```',  # Python 코드 블록
            r'```javascript[\s\S]*?```',  # JavaScript 코드 블록
            r'```json[\s\S]*?```',  # JSON 코드 블록
            r'```yaml[\s\S]*?```',  # YAML 코드 블록
            r'```xml[\s\S]*?```',  # XML 코드 블록
            r'```sql[\s\S]*?```',  # SQL 코드 블록
        ]
        
        code_found = False
        for pattern in code_patterns:
            if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                code_found = True
                break
        
        if not code_found:
            violations.append(self._create_violation(
                "code_example_missing",
                "코드 예제가 누락되었습니다.",
                self.scoring['deductions']['code_example_missing']
            ))
        
        # 변경 이력 검사
        change_history_pattern = r'##\s*[0-9]+\.\s*변경\s*이력|##\s*[0-9]+\.\s*changelog|##\s*[0-9]+\.\s*version'
        if not re.search(change_history_pattern, content, re.IGNORECASE):
            violations.append(self._create_violation(
                "change_history_missing",
                "변경 이력 섹션이 누락되었습니다.",
                self.scoring['deductions']['change_history_missing']
            ))
        
        return violations
    
    def _extract_section(self, content: str, pattern: str) -> str:
        """섹션 내용 추출"""
        match = re.search(pattern, content, re.IGNORECASE)
        if not match:
            return ""
        
        start_pos = match.end()
        # 다음 섹션 찾기
        next_section_match = re.search(r'^##\s*[0-9]+\.', content[start_pos:], re.MULTILINE)
        if next_section_match:
            end_pos = start_pos + next_section_match.start()
        else:
            end_pos = len(content)
        
        return content[start_pos:end_pos].strip()
    
    def _check_design_rules_content(self, section_content: str) -> List[Dict[str, Any]]:
        """설계 규칙 섹션 내용 검사"""
        violations = []
        
        # MUST, SHOULD, MUST NOT 키워드 검사
        must_pattern = r'(MUST|SHOULD|MUST NOT|MUSTNOT)'
        if not re.search(must_pattern, section_content, re.IGNORECASE):
            violations.append(self._create_violation(
                "design_rules_keywords_missing",
                "설계 규칙에 MUST, SHOULD, MUST NOT 키워드가 누락되었습니다.",
                self.scoring['deductions']['design_rules_keywords_missing']
            ))
        
        # 규칙 개수 검사 (최소 3개)
        rule_pattern = r'^\s*[-*]\s*'
        rules = re.findall(rule_pattern, section_content, re.MULTILINE)
        if len(rules) < 3:
            violations.append(self._create_violation(
                "design_rules_insufficient",
                "설계 규칙이 충분하지 않습니다. 최소 3개 이상의 규칙을 작성하세요.",
                self.scoring['deductions']['design_rules_insufficient']
            ))
        
        # 규칙 내용 길이 검사
        rule_lines = re.findall(r'^\s*[-*]\s*(.+)$', section_content, re.MULTILINE)
        for i, rule in enumerate(rule_lines):
            if len(rule.strip()) < 10:
                violations.append(self._create_violation(
                    "rule_content_too_short",
                    f"규칙 {i+1}의 내용이 너무 짧습니다.",
                    self.scoring['deductions']['rule_content_too_short']
                ))
        
        return violations
    
    def _create_violation(self, violation_type: str, message: str, penalty: int) -> Dict[str, Any]:
        """위반사항 생성"""
        return {
            "type": violation_type,
            "message": message,
            "penalty": penalty
        }
