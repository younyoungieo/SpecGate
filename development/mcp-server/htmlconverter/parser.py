"""
HTML 파서
HTML 문서의 구조를 분석하고 요소를 추출하는 모듈
"""
import re
import logging
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup


class HTMLParser:
    """HTML 파서"""
    
    def __init__(self):
        self.logger = logging.getLogger("specgate.htmlconverter.parser")
    
    def parse_html_structure(self, html_content: str) -> Dict[str, Any]:
        """HTML 문서의 구조를 분석한다."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            structure = {
                'title': self._extract_title(soup),
                'headings': self._extract_headings(soup),
                'tables': self._extract_tables(soup),
                'code_blocks': self._extract_code_blocks(soup),
                'lists': self._extract_lists(soup),
                'links': self._extract_links(soup),
                'images': self._extract_images(soup),
                'paragraphs': self._extract_paragraphs(soup)
            }
            
            self.logger.info(f"HTML 구조 분석 완료: {len(structure['headings'])}개 헤딩, {len(structure['tables'])}개 표")
            return structure
            
        except Exception as e:
            self.logger.error(f"HTML 파싱 실패: {str(e)}")
            return self._create_empty_structure()
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """문서 제목을 추출한다."""
        # h1 태그 우선
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        # title 태그
        title = soup.find('title')
        if title:
            return title.get_text().strip()
        
        return ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """헤딩 요소를 추출한다."""
        headings = []
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                headings.append({
                    'level': i,
                    'text': heading.get_text().strip(),
                    'id': heading.get('id', ''),
                    'tag': f'h{i}'
                })
        return headings
    
    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """표 요소를 추출한다."""
        tables = []
        for table in soup.find_all('table'):
            table_data = {
                'headers': [],
                'rows': [],
                'element': table
            }
            
            # 헤더 추출
            thead = table.find('thead')
            if thead:
                for th in thead.find_all('th'):
                    table_data['headers'].append(th.get_text().strip())
            else:
                # thead가 없으면 첫 번째 행을 헤더로 간주
                first_row = table.find('tr')
                if first_row:
                    for th in first_row.find_all(['th', 'td']):
                        table_data['headers'].append(th.get_text().strip())
            
            # 데이터 행 추출
            tbody = table.find('tbody') or table
            for tr in tbody.find_all('tr'):
                if tr.find('th'):  # 헤더 행인 경우
                    continue
                row = []
                for td in tr.find_all('td'):
                    row.append(td.get_text().strip())
                if row:
                    table_data['rows'].append(row)
            
            tables.append(table_data)
        
        return tables
    
    def _extract_code_blocks(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """코드 블록을 추출한다."""
        code_blocks = []
        
        # pre 태그 (코드 블록)
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if code:
                language = self._detect_code_language(code)
                code_blocks.append({
                    'type': 'block',
                    'content': code.get_text(),
                    'language': language,
                    'element': pre
                })
            else:
                code_blocks.append({
                    'type': 'block',
                    'content': pre.get_text(),
                    'language': 'text',
                    'element': pre
                })
        
        # 인라인 코드
        for code in soup.find_all('code'):
            if not code.find_parent('pre'):  # pre 안에 있지 않은 경우만
                code_blocks.append({
                    'type': 'inline',
                    'content': code.get_text(),
                    'language': 'text',
                    'element': code
                })
        
        return code_blocks
    
    def _extract_lists(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """리스트를 추출한다."""
        lists = []
        
        # ul (순서 없는 리스트)
        for ul in soup.find_all('ul'):
            items = []
            for li in ul.find_all('li'):
                items.append(li.get_text().strip())
            lists.append({
                'type': 'ul',
                'items': items,
                'element': ul
            })
        
        # ol (순서 있는 리스트)
        for ol in soup.find_all('ol'):
            items = []
            for li in ol.find_all('li'):
                items.append(li.get_text().strip())
            lists.append({
                'type': 'ol',
                'items': items,
                'element': ol
            })
        
        return lists
    
    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """링크를 추출한다."""
        links = []
        for a in soup.find_all('a'):
            href = a.get('href', '')
            text = a.get_text().strip()
            if href and text:
                links.append({
                    'text': text,
                    'url': href,
                    'element': a
                })
        return links
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """이미지를 추출한다."""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            images.append({
                'src': src,
                'alt': alt,
                'element': img
            })
        return images
    
    def _extract_paragraphs(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """문단을 추출한다."""
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text:
                paragraphs.append({
                    'text': text,
                    'element': p
                })
        return paragraphs
    
    def _detect_code_language(self, code_element) -> str:
        """코드 언어를 감지한다."""
        # class에서 언어 추출
        class_name = code_element.get('class', [])
        for cls in class_name:
            if cls.startswith('language-'):
                return cls.replace('language-', '')
            if cls in ['python', 'javascript', 'json', 'yaml', 'xml', 'sql']:
                return cls
        
        # 부모 pre 태그의 class 확인
        pre = code_element.find_parent('pre')
        if pre:
            pre_class = pre.get('class', [])
            for cls in pre_class:
                if cls.startswith('language-'):
                    return cls.replace('language-', '')
                if cls in ['python', 'javascript', 'json', 'yaml', 'xml', 'sql']:
                    return cls
        
        return 'text'
    
    def _create_empty_structure(self) -> Dict[str, Any]:
        """빈 구조를 생성한다."""
        return {
            'title': '',
            'headings': [],
            'tables': [],
            'code_blocks': [],
            'lists': [],
            'links': [],
            'images': [],
            'paragraphs': []
        }


