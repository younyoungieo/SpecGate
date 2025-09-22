"""
HTML to Markdown 변환기
HTML 요소를 Markdown 형식으로 변환하는 핵심 모듈
"""
import re
import logging
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup, Tag


class HTMLToMarkdownConverter:
    """HTML to Markdown 변환기"""
    
    def __init__(self):
        self.logger = logging.getLogger("specgate.htmlconverter.converter")
        self.conversion_mapping = self._init_conversion_mapping()
    
    async def convert(self, html_content: str, preserve_structure: bool = True, save_to_file: bool = False, output_path: str = None) -> Dict[str, Any]:
        """HTML을 Markdown으로 변환한다."""
        try:
            import time
            t0 = time.perf_counter()

            # 파서 선택(가능 시 lxml 사용)
            parser = 'lxml'
            try:
                import lxml  # noqa: F401
            except Exception:
                parser = 'html.parser'

            soup = BeautifulSoup(html_content, parser)
            t1 = time.perf_counter()
            self.logger.info(
                "HTML→MD | step=parse | parser=%s | length=%s | elapsed=%.3fs",
                parser,
                len(html_content) if html_content else 0,
                (t1 - t0)
            )

            markdown_parts = []
            
            # 주요 요소들을 순서대로 변환
            for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                                         'p', 'ul', 'ol', 'table', 'pre', 'blockquote']):
                converted = self._convert_element(element, preserve_structure)
                if converted:
                    markdown_parts.append(converted)
            
            # 빈 줄로 구분하여 결합
            markdown_content = '\n\n'.join(markdown_parts)
            t2 = time.perf_counter()
            self.logger.info(
                "HTML→MD | step=convert_elements | elements=%d | elapsed=%.3fs",
                len(markdown_parts),
                (t2 - t1)
            )
            
            # 정리 작업
            markdown_content = self._cleanup_markdown(markdown_content)
            t3 = time.perf_counter()
            self.logger.info(
                "HTML→MD | step=cleanup | elapsed=%.3fs",
                (t3 - t2)
            )
            
            # 파일 저장 처리
            saved_file_path = None
            if save_to_file:
                saved_file_path = await self._save_to_file(markdown_content, output_path)
            t4 = time.perf_counter()
            self.logger.info(
                "HTML→MD | step=save | saved=%s | path=%s | elapsed=%.3fs | total=%.3fs",
                bool(saved_file_path),
                saved_file_path or "<not saved>",
                (t4 - t3),
                (t4 - t0)
            )
            
            return {
                'status': 'success',
                'markdown': markdown_content,
                'metadata': self._extract_metadata(soup),
                'conversion_info': {
                    'preserve_structure': preserve_structure,
                    'elements_converted': len(markdown_parts),
                    'saved_to_file': save_to_file,
                    'file_path': saved_file_path
                }
            }
            
        except Exception as e:
            self.logger.error(f"HTML→MD 변환 실패: {str(e)}")
            return {
                'status': 'error',
                'message': f'HTML→MD 변환 중 오류가 발생했습니다: {str(e)}',
                'fallback_content': html_content,
                'requires_manual_review': True
            }
    
    def _convert_element(self, element: Tag, preserve_structure: bool) -> str:
        """개별 HTML 요소를 Markdown으로 변환한다."""
        tag = element.name
        
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return self._convert_heading(element)
        
        elif tag == 'p':
            return self._convert_paragraph(element)
        
        elif tag in ['ul', 'ol']:
            return self._convert_list(element)
        
        elif tag == 'table':
            return self._convert_table(element)
        
        elif tag == 'pre':
            return self._convert_code_block(element)
        
        elif tag == 'blockquote':
            return self._convert_blockquote(element)
        
        else:
            return element.get_text().strip()
    
    def _convert_heading(self, heading: Tag) -> str:
        """헤딩을 변환한다."""
        level = int(heading.name[1])
        text = heading.get_text().strip()
        return f"{'#' * level} {text}"
    
    def _convert_paragraph(self, paragraph: Tag) -> str:
        """문단을 변환하고 인라인 요소를 처리한다."""
        text = paragraph.get_text()
        
        # 인라인 요소 처리
        text = self._process_inline_elements(paragraph, text)
        
        return text.strip()
    
    def _convert_list(self, list_element: Tag) -> str:
        """리스트를 변환한다."""
        items = []
        list_type = list_element.name
        
        for li in list_element.find_all('li', recursive=False):
            item_text = self._process_inline_elements(li, li.get_text())
            
            if list_type == 'ul':
                items.append(f"- {item_text}")
            else:  # ol
                items.append(f"1. {item_text}")
        
        return '\n'.join(items)
    
    def _convert_table(self, table: Tag) -> str:
        """표를 Markdown 형식으로 변환한다."""
        rows = []
        
        # 헤더 행 처리
        thead = table.find('thead')
        if thead:
            header_row = []
            for th in thead.find_all('th'):
                header_row.append(th.get_text().strip())
            if header_row:
                rows.append('| ' + ' | '.join(header_row) + ' |')
                rows.append('| ' + ' | '.join(['---'] * len(header_row)) + ' |')
        else:
            # thead가 없으면 첫 번째 행을 헤더로 간주
            first_row = table.find('tr')
            if first_row:
                header_row = []
                for th in first_row.find_all(['th', 'td']):
                    header_row.append(th.get_text().strip())
                if header_row:
                    rows.append('| ' + ' | '.join(header_row) + ' |')
                    rows.append('| ' + ' | '.join(['---'] * len(header_row)) + ' |')
        
        # 데이터 행 처리
        tbody = table.find('tbody') or table
        for tr in tbody.find_all('tr'):
            if tr.find('th'):  # 헤더 행인 경우
                continue
            row = []
            for td in tr.find_all('td'):
                cell_text = td.get_text().strip()
                # 파이프 문자 이스케이프
                cell_text = cell_text.replace('|', '\\|')
                row.append(cell_text)
            if row:
                rows.append('| ' + ' | '.join(row) + ' |')
        
        return '\n'.join(rows)
    
    def _convert_code_block(self, pre: Tag) -> str:
        """코드 블록을 변환한다."""
        code = pre.find('code')
        if code:
            language = self._detect_code_language(code)
            content = code.get_text()
            return f"```{language}\n{content}\n```"
        else:
            content = pre.get_text()
            return f"```\n{content}\n```"
    
    def _convert_blockquote(self, blockquote: Tag) -> str:
        """인용문을 변환한다."""
        text = blockquote.get_text().strip()
        lines = text.split('\n')
        quoted_lines = [f"> {line}" for line in lines]
        return '\n'.join(quoted_lines)
    
    def _process_inline_elements(self, element: Tag, text: str) -> str:
        """인라인 요소를 처리한다."""
        # strong/b 태그
        for strong in element.find_all(['strong', 'b']):
            original = strong.get_text()
            replacement = f"**{original}**"
            text = text.replace(original, replacement)
        
        # em/i 태그
        for em in element.find_all(['em', 'i']):
            original = em.get_text()
            replacement = f"*{original}*"
            text = text.replace(original, replacement)
        
        # code 태그 (인라인)
        for code in element.find_all('code'):
            if not code.find_parent('pre'):  # pre 안에 있지 않은 경우만
                original = code.get_text()
                replacement = f"`{original}`"
                text = text.replace(original, replacement)
        
        # del/s 태그
        for del_tag in element.find_all(['del', 's']):
            original = del_tag.get_text()
            replacement = f"~~{original}~~"
            text = text.replace(original, replacement)
        
        # 링크 처리
        for a in element.find_all('a'):
            href = a.get('href', '')
            link_text = a.get_text()
            if href and link_text:
                replacement = f"[{link_text}]({href})"
                text = text.replace(link_text, replacement)
        
        return text
    
    def _detect_code_language(self, code_element: Tag) -> str:
        """코드 언어를 감지한다."""
        # class에서 언어 추출
        class_name = code_element.get('class', [])
        for cls in class_name:
            if cls.startswith('language-'):
                return cls.replace('language-', '')
            if cls in ['python', 'javascript', 'json', 'yaml', 'xml', 'sql', 'bash', 'shell']:
                return cls
        
        # 부모 pre 태그의 class 확인
        pre = code_element.find_parent('pre')
        if pre:
            pre_class = pre.get('class', [])
            for cls in pre_class:
                if cls.startswith('language-'):
                    return cls.replace('language-', '')
                if cls in ['python', 'javascript', 'json', 'yaml', 'xml', 'sql', 'bash', 'shell']:
                    return cls
        
        return 'text'
    
    def _cleanup_markdown(self, markdown: str) -> str:
        """Markdown을 정리한다."""
        # 연속된 빈 줄을 2개로 제한
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # 앞뒤 공백 제거
        markdown = markdown.strip()
        
        return markdown
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """메타데이터를 추출한다."""
        metadata = {
            'title': '',
            'has_tables': len(soup.find_all('table')) > 0,
            'has_code_blocks': len(soup.find_all('pre')) > 0,
            'has_lists': len(soup.find_all(['ul', 'ol'])) > 0,
            'has_links': len(soup.find_all('a')) > 0,
            'has_images': len(soup.find_all('img')) > 0
        }
        
        # 제목 추출
        h1 = soup.find('h1')
        if h1:
            metadata['title'] = h1.get_text().strip()
        else:
            title = soup.find('title')
            if title:
                metadata['title'] = title.get_text().strip()
        
        return metadata
    
    async def _save_to_file(self, markdown_content: str, output_path: str = None) -> str:
        """Markdown을 파일로 저장한다."""
        import os
        import aiofiles
        from datetime import datetime
        
        try:
            # 출력 경로 생성
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"converted_{timestamp}.md"
            
            # 디렉토리 생성
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            
            # 파일 저장
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                await f.write(markdown_content)
            
            self.logger.info(f"Markdown 파일 저장 완료: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"파일 저장 실패: {str(e)}")
            raise Exception(f"파일 저장 중 오류 발생: {str(e)}")
    
    def _init_conversion_mapping(self) -> Dict[str, Any]:
        """변환 매핑을 초기화한다."""
        return {
            'headings': {
                'h1': '# ',
                'h2': '## ',
                'h3': '### ',
                'h4': '#### ',
                'h5': '##### ',
                'h6': '###### '
            },
            'text_formatting': {
                'strong': '**{}**',
                'em': '*{}*',
                'code': '`{}`',
                'del': '~~{}~~'
            },
            'lists': {
                'ul': '- ',
                'ol': '1. ',
                'li': '  '
            }
        }
