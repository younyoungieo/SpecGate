"""
SpecLint 메인 클래스

Confluence에서 가져온 설계 문서의 품질을 검사하는
통합 워크플로우를 관리하는 메인 클래스입니다.

US-002의 요구사항에 따라 다음 단계를 수행합니다:
1. 문서 구조 분석 (DocumentStructureAnalyzer)
2. 템플릿 준수 검사 (TemplateValidator)
3. 품질 점수 계산 (QualityScorer)
4. 개선 제안 생성 (ImprovementSuggester)
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from speclint_lint.analyzers import DocumentStructureAnalyzer
from speclint_lint.validators import TemplateValidator
from speclint_lint.scorers import QualityScorer
from speclint_lint.suggestors import ImprovementSuggester


class SpecLint:
    """SpecLint 메인 클래스
    
    설계 문서의 품질을 종합적으로 검사하고 평가하는
    통합 워크플로우를 제공합니다.
    """
    
    def __init__(self):
        """SpecLint 인스턴스 초기화"""
        self.analyzer = DocumentStructureAnalyzer()
        self.validator = TemplateValidator()
        self.scorer = QualityScorer()
        self.suggester = ImprovementSuggester()
        self.logger = logging.getLogger("specgate.speclint")
        
        self.logger.info("SpecLint 인스턴스 초기화 완료")
    
    async def lint(self, content: str, check_type: str = "full", document_title: Optional[str] = None) -> Dict[str, Any]:
        """문서 품질 검사 실행
        
        Args:
            content: 검사할 문서 내용
            check_type: 검사 유형 ("full", "basic", "structure")
            document_title: Confluence 문서의 실제 제목 (선택사항)
            
        Returns:
            Dict[str, Any]: 품질 검사 결과
                - score: 품질 점수 (0-100)
                - violations: 위반 사항 목록
                - suggestions: 개선 제안 목록
                - metadata: 메타데이터
        """
        start_time = datetime.now()
        self.logger.info(f"문서 품질 검사 시작 - 검사 유형: {check_type}")
        
        try:
            # 입력 검증
            if content is None:
                self.logger.error("문서 내용이 None입니다.")
                return self.scorer.create_error_result("문서 내용이 None입니다.", check_type)
            
            if not content.strip():
                self.logger.warning("빈 문서 검사 요청")
                return self.scorer.create_error_result("문서 파싱에 실패했습니다.", check_type)
            
            # 1단계: 문서 구조 분석
            self.logger.info("1단계: 문서 구조 분석 중...")
            structure_analysis = await self.analyzer.analyze(content, document_title)
            
            # 2단계: 템플릿 준수 검사
            self.logger.info("2단계: 템플릿 준수 검사 중...")
            template_violations = await self.validator.validate(content, check_type)
            
            # 3단계: 품질 점수 계산
            self.logger.info("3단계: 품질 점수 계산 중...")
            quality_score = await self.scorer.calculate_score(structure_analysis, template_violations)
            
            # 4단계: 개선 제안 생성
            self.logger.info("4단계: 개선 제안 생성 중...")
            suggestions = await self.suggester.generate_suggestions(template_violations)
            
            # 5단계: 품질 등급별 처리 결과 생성
            quality_level = self.scorer.determine_quality_level(quality_score)
            processing_result = self.scorer.create_processing_result(quality_score, quality_level, template_violations)
            
            # 처리 시간 계산
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "score": quality_score,
                "violations": template_violations,
                "suggestions": suggestions,
                "metadata": {
                    "check_type": check_type,
                    "content_length": len(content) if content else 0,
                    "timestamp": datetime.now().isoformat(),
                    "quality_level": quality_level,
                    "processing_result": processing_result,
                    "processing_time_seconds": processing_time,
                    "structure_analysis": structure_analysis
                }
            }
            
            self.logger.info(f"품질 검사 완료 - 점수: {quality_score}/100, 등급: {quality_level}, 처리시간: {processing_time:.2f}초")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"품질 검사 실패: {str(e)} (처리시간: {processing_time:.2f}초)")
            return self.scorer.create_error_result(f"품질 검사 중 오류 발생: {str(e)}", check_type)
    
    async def batch_lint(self, documents: List[Dict[str, Any]], check_type: str = "full") -> Dict[str, Any]:
        """배치 문서 품질 검사
        
        Args:
            documents: 검사할 문서 목록 (각 문서는 'content', 'id', 'title' 키 포함)
            check_type: 검사 유형 ("full", "basic", "structure")
            
        Returns:
            Dict[str, Any]: 배치 검사 결과
                - results: 각 문서별 검사 결과
                - summary: 전체 요약 통계
                - metadata: 메타데이터
        """
        start_time = datetime.now()
        self.logger.info(f"배치 문서 품질 검사 시작 - 문서 수: {len(documents)}")
        
        if not documents:
            self.logger.warning("빈 문서 목록으로 배치 검사 요청")
            return {
                'results': [],
                'summary': {
                    'total_documents': 0,
                    'successful_count': 0,
                    'failed_count': 0,
                    'average_score': 0
                },
                'metadata': {
                    'check_type': check_type,
                    'timestamp': datetime.now().isoformat(),
                    'processing_time_seconds': 0
                }
            }
        
        results = []
        total_score = 0
        successful_count = 0
        failed_count = 0
        
        for i, doc in enumerate(documents, 1):
            try:
                content = doc.get('content', '')
                doc_id = doc.get('id', f'doc_{i}')
                doc_title = doc.get('title', 'Unknown')
                
                self.logger.info(f"문서 {i}/{len(documents)} 처리 중: {doc_title}")
                
                result = await self.lint(content, check_type, doc_title)
                result['document_id'] = doc_id
                result['title'] = doc_title
                
                results.append(result)
                total_score += result['score']
                
                if result['score'] > 0:
                    successful_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                self.logger.error(f"문서 {doc.get('id', f'doc_{i}')} 처리 실패: {str(e)}")
                failed_count += 1
                results.append({
                    'document_id': doc.get('id', f'doc_{i}'),
                    'title': doc.get('title', 'Unknown'),
                    'score': 0,
                    'violations': [{'type': 'processing_error', 'message': str(e)}],
                    'suggestions': ['문서를 확인하고 다시 시도하세요.'],
                    'metadata': {'error': str(e)}
                })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        average_score = total_score / len(documents) if documents else 0
        
        self.logger.info(f"배치 검사 완료 - 성공: {successful_count}, 실패: {failed_count}, 평균점수: {average_score:.1f}, 처리시간: {processing_time:.2f}초")
        
        return {
            'results': results,
            'summary': {
                'total_documents': len(documents),
                'successful_count': successful_count,
                'failed_count': failed_count,
                'average_score': average_score
            },
            'metadata': {
                'check_type': check_type,
                'timestamp': datetime.now().isoformat(),
                'processing_time_seconds': processing_time
            }
        }
