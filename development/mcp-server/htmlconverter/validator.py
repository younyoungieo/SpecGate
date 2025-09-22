"""
변환 품질 검증기
HTML→MD 변환 품질을 검증하고 문제점을 식별하는 모듈
"""
import re
import logging
from typing import Dict, List, Any, Tuple
from bs4 import BeautifulSoup


class ConversionValidator:
    """변환 품질 검증기"""
    
    def __init__(self):
        self.logger = logging.getLogger("specgate.htmlconverter.validator")
    
    def validate_conversion(self, original_html: str, converted_markdown: str) -> Dict[str, Any]:
        """변환 품질을 검증한다."""
        try:
            issues = []
            quality_score = 100
            
            # 기본 검사
            basic_issues, basic_score = self._validate_basic_requirements(original_html, converted_markdown)
            issues.extend(basic_issues)
            quality_score = min(quality_score, basic_score)
            
            # 구조 검사
            structure_issues, structure_score = self._validate_structure_integrity(original_html, converted_markdown)
            issues.extend(structure_issues)
            quality_score = min(quality_score, structure_score)
            
            # 내용 검사
            content_issues, content_score = self._validate_content_preservation(original_html, converted_markdown)
            issues.extend(content_issues)
            quality_score = min(quality_score, content_score)
            
            return {
                'is_valid': len(issues) == 0,
                'quality_score': max(0, quality_score),
                'issues': issues,
                'summary': self._generate_validation_summary(issues, quality_score)
            }
            
        except Exception as e:
            self.logger.error(f"변환 검증 실패: {str(e)}")
            return {
                'is_valid': False,
                'quality_score': 0,
                'issues': [f"검증 중 오류 발생: {str(e)}"],
                'summary': "검증 실패"
            }
    
    def _validate_basic_requirements(self, html: str, markdown: str) -> Tuple[List[str], int]:
        """기본 요구사항을 검증한다."""
        issues = []
        score = 100
        
        # 빈 변환 결과 검사
        if not markdown.strip():
            issues.append("변환된 Markdown이 비어있습니다")
            score = 0
            return issues, score
        
        # HTML이 비어있는 경우
        if not html.strip():
            if not markdown.strip():
                score = 100  # 둘 다 비어있으면 정상
            else:
                issues.append("빈 HTML에서 비어있지 않은 Markdown이 생성되었습니다")
                score = 50
        
        return issues, score
    
    def _validate_structure_integrity(self, html: str, markdown: str) -> Tuple[List[str], int]:
        """구조 무결성을 검증한다."""
        issues = []
        score = 100
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 헤딩 수 검사
            html_headings = len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
            md_headings = len(re.findall(r'^#{1,6}\s+', markdown, re.MULTILINE))
            
            if html_headings != md_headings:
                issues.append(f"헤딩 수 불일치: HTML {html_headings}개, MD {md_headings}개")
                score -= 20
            
            # 표 수 검사
            html_tables = len(soup.find_all('table'))
            md_tables = len(re.findall(r'^\|.*\|$', markdown, re.MULTILINE)) // 2  # 헤더+구분선+데이터
            
            if html_tables > 0 and md_tables == 0:
                issues.append(f"표 변환 실패: HTML {html_tables}개 표가 변환되지 않음")
                score -= 30
            elif html_tables != md_tables:
                issues.append(f"표 수 불일치: HTML {html_tables}개, MD {md_tables}개")
                score -= 15
            
            # 리스트 수 검사
            html_lists = len(soup.find_all(['ul', 'ol']))
            md_lists = len(re.findall(r'^[-*+]\s+', markdown, re.MULTILINE)) + len(re.findall(r'^\d+\.\s+', markdown, re.MULTILINE))
            
            if html_lists > 0 and md_lists == 0:
                issues.append(f"리스트 변환 실패: HTML {html_lists}개 리스트가 변환되지 않음")
                score -= 20
            elif html_lists != md_lists:
                issues.append(f"리스트 수 불일치: HTML {html_lists}개, MD {md_lists}개")
                score -= 10
            
            # 코드 블록 검사
            html_code_blocks = len(soup.find_all('pre'))
            md_code_blocks = len(re.findall(r'^```', markdown, re.MULTILINE))
            
            if html_code_blocks > 0 and md_code_blocks == 0:
                issues.append(f"코드 블록 변환 실패: HTML {html_code_blocks}개 코드 블록이 변환되지 않음")
                score -= 25
            elif html_code_blocks != md_code_blocks:
                issues.append(f"코드 블록 수 불일치: HTML {html_code_blocks}개, MD {md_code_blocks}개")
                score -= 15
            
        except Exception as e:
            issues.append(f"구조 검증 중 오류: {str(e)}")
            score -= 30
        
        return issues, max(0, score)
    
    def _validate_content_preservation(self, html: str, markdown: str) -> Tuple[List[str], int]:
        """내용 보존을 검증한다."""
        issues = []
        score = 100
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 텍스트 내용 비교
            html_text = soup.get_text().strip()
            markdown_text = re.sub(r'[#*`|>\-\d\.\s]+', '', markdown).strip()
            
            # 텍스트 길이 비교 (50% 이상 보존되어야 함)
            if len(html_text) > 0:
                preservation_ratio = len(markdown_text) / len(html_text)
                if preservation_ratio < 0.5:
                    issues.append(f"텍스트 보존률 낮음: {preservation_ratio:.1%}")
                    score -= 40
                elif preservation_ratio < 0.8:
                    issues.append(f"텍스트 보존률 보통: {preservation_ratio:.1%}")
                    score -= 20
            
            # 링크 보존 검사
            html_links = len(soup.find_all('a'))
            md_links = len(re.findall(r'\[.*?\]\(.*?\)', markdown))
            
            if html_links > 0 and md_links == 0:
                issues.append(f"링크 변환 실패: HTML {html_links}개 링크가 변환되지 않음")
                score -= 15
            elif html_links != md_links:
                issues.append(f"링크 수 불일치: HTML {html_links}개, MD {md_links}개")
                score -= 10
            
            # 이미지 보존 검사
            html_images = len(soup.find_all('img'))
            md_images = len(re.findall(r'!\[.*?\]\(.*?\)', markdown))
            
            if html_images > 0 and md_images == 0:
                issues.append(f"이미지 변환 실패: HTML {html_images}개 이미지가 변환되지 않음")
                score -= 10
            elif html_images != md_images:
                issues.append(f"이미지 수 불일치: HTML {html_images}개, MD {md_images}개")
                score -= 5
            
        except Exception as e:
            issues.append(f"내용 검증 중 오류: {str(e)}")
            score -= 20
        
        return issues, max(0, score)
    
    def _generate_validation_summary(self, issues: List[str], score: int) -> str:
        """검증 요약을 생성한다."""
        if score >= 90:
            return "우수한 변환 품질"
        elif score >= 70:
            return "양호한 변환 품질"
        elif score >= 50:
            return "보통 변환 품질"
        else:
            return "개선이 필요한 변환 품질"
    
    def count_headings_in_html(self, html: str) -> int:
        """HTML의 헤딩 수를 계산한다."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
        except:
            return 0
    
    def count_headings_in_markdown(self, markdown: str) -> int:
        """Markdown의 헤딩 수를 계산한다."""
        return len(re.findall(r'^#{1,6}\s+', markdown, re.MULTILINE))
    
    def count_tables_in_html(self, html: str) -> int:
        """HTML의 표 수를 계산한다."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return len(soup.find_all('table'))
        except:
            return 0
    
    def count_tables_in_markdown(self, markdown: str) -> int:
        """Markdown의 표 수를 계산한다."""
        # 표는 헤더+구분선+데이터 행으로 구성되므로 3줄마다 1개 표
        table_lines = len(re.findall(r'^\|.*\|$', markdown, re.MULTILINE))
        return max(0, table_lines // 3)


