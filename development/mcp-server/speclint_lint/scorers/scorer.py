"""
SpecLint 품질 점수 계산기
문서의 품질을 0-100점으로 계산하는 모듈
"""
from typing import Dict, List, Any
from speclint_lint.utils.rules import QUALITY_SCORING


class QualityScorer:
    """품질 점수 계산기"""
    
    def __init__(self):
        self.scoring = QUALITY_SCORING
    
    async def calculate_score(self, structure: Dict[str, Any], violations: List[Dict[str, Any]]) -> int:
        """품질 점수 계산 (0-100)"""
        # 파싱 에러가 있으면 즉시 0점 반환
        for violation in violations:
            if violation.get("type") == "parsing_error":
                return 0
        
        # 구조 점수 기반 계산
        structure_score = structure.get("structure_score", 0)
        
        # 위반 사항에 따른 차감 점수 계산 (penalty는 음수이므로 절댓값 사용)
        total_penalty = sum(abs(violation.get("penalty", 0)) for violation in violations)
        
        # 최종 점수 계산 로직 개선
        if violations:
            # 위반사항이 있으면 구조 점수에서 차감 (구조 점수가 더 정확한 평가)
            if structure_score > 0:
                final_score = max(0, structure_score - total_penalty)
            else:
                # 구조 점수가 없으면 기본 점수에서 차감
                base_score = self.scoring['base_score']
                final_score = max(0, base_score - total_penalty)
        else:
            # 위반사항이 없으면 구조 점수 사용
            if structure_score > 0:
                final_score = structure_score
            else:
                # 구조 점수도 없으면 기본 점수
                final_score = self.scoring['base_score']
        
        # 0-100 범위 보장
        return max(0, min(100, final_score))
    
    def determine_quality_level(self, score: int) -> str:
        """품질 점수에 따른 등급 결정"""
        thresholds = self.scoring['thresholds']
        
        if score >= thresholds['high_quality']:
            return "high_quality"
        elif score >= thresholds['medium_quality']:
            return "medium_quality"
        else:
            return "low_quality"
    
    def create_processing_result(self, score: int, quality_level: str, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """품질 등급별 처리 결과 생성"""
        if quality_level == "high_quality":
            return {
                "status": "auto_approve",
                "message": "✅ 문서가 표준을 준수합니다. Phase 2 진행 가능합니다.",
                "next_action": "proceed_to_phase2",
                "score": score
            }
        elif quality_level == "medium_quality":
            return {
                "status": "hitl_review_required",
                "message": f"⚠️ HITL 검토가 필요합니다. 품질 점수: {score}점",
                "next_action": "create_hitl_issue",
                "score": score,
                "issues": violations
            }
        else:  # low_quality
            return {
                "status": "mandatory_fix_required",
                "message": f"❌ 문서 수정이 필수입니다. 품질 점수: {score}점",
                "next_action": "create_mandatory_fix_issue",
                "score": score,
                "issues": violations
            }
    
    def create_error_result(self, error_message: str, check_type: str) -> Dict[str, Any]:
        """에러 결과 생성"""
        return {
            "score": 0,
            "violations": [{
                "type": "error",
                "message": error_message,
                "penalty": 100
            }],
            "suggestions": ["문서를 확인하고 다시 시도하세요."],
            "metadata": {
                "check_type": check_type,
                "content_length": 0,
                "quality_level": "error",
                "processing_result": {
                    "status": "error",
                    "message": error_message,
                    "next_action": "manual_review_required"
                }
            }
        }


