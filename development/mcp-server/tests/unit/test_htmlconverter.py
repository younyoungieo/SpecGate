"""
HTML→MD 변환기 테스트
"""
import pytest
import asyncio
from htmlconverter import HTMLToMarkdownConverter, HTMLParser, ConversionValidator


class TestHTMLToMarkdownConverter:
    """HTML→MD 변환기 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.converter = HTMLToMarkdownConverter()
    
    @pytest.mark.asyncio
    async def test_basic_html_conversion(self):
        """기본 HTML 변환 테스트"""
        html = "<h1>제목</h1><p>문단입니다.</p>"
        result = await self.converter.convert(html)
        
        assert result['status'] == 'success'
        assert '# 제목' in result['markdown']
        assert '문단입니다.' in result['markdown']
    
    @pytest.mark.asyncio
    async def test_heading_conversion(self):
        """헤딩 변환 테스트"""
        html = """
        <h1>제목 1</h1>
        <h2>제목 2</h2>
        <h3>제목 3</h3>
        """
        result = await self.converter.convert(html)
        
        assert '# 제목 1' in result['markdown']
        assert '## 제목 2' in result['markdown']
        assert '### 제목 3' in result['markdown']
    
    @pytest.mark.asyncio
    async def test_list_conversion(self):
        """리스트 변환 테스트"""
        html = """
        <ul>
            <li>항목 1</li>
            <li>항목 2</li>
        </ul>
        <ol>
            <li>순서 1</li>
            <li>순서 2</li>
        </ol>
        """
        result = await self.converter.convert(html)
        
        assert '- 항목 1' in result['markdown']
        assert '- 항목 2' in result['markdown']
        assert '1. 순서 1' in result['markdown']
        assert '1. 순서 2' in result['markdown']
    
    @pytest.mark.asyncio
    async def test_code_block_conversion(self):
        """코드 블록 변환 테스트"""
        html = """
        <pre><code class="language-python">
def hello():
    print("Hello World")
        </code></pre>
        """
        result = await self.converter.convert(html)
        
        assert '```python' in result['markdown']
        assert 'def hello():' in result['markdown']
        assert 'print("Hello World")' in result['markdown']
    
    @pytest.mark.asyncio
    async def test_table_conversion(self):
        """표 변환 테스트"""
        html = """
        <table>
            <thead>
                <tr><th>이름</th><th>나이</th></tr>
            </thead>
            <tbody>
                <tr><td>김철수</td><td>30</td></tr>
                <tr><td>이영희</td><td>25</td></tr>
            </tbody>
        </table>
        """
        result = await self.converter.convert(html)
        
        assert '| 이름 | 나이 |' in result['markdown']
        assert '| --- | --- |' in result['markdown']
        assert '| 김철수 | 30 |' in result['markdown']
        assert '| 이영희 | 25 |' in result['markdown']
    
    @pytest.mark.asyncio
    async def test_inline_formatting(self):
        """인라인 서식 변환 테스트"""
        html = """
        <p>이것은 <strong>굵은 글씨</strong>와 <em>기울임</em>과 <code>코드</code>입니다.</p>
        """
        result = await self.converter.convert(html)
        
        assert '**굵은 글씨**' in result['markdown']
        assert '*기울임*' in result['markdown']
        assert '`코드`' in result['markdown']
    
    @pytest.mark.asyncio
    async def test_empty_html(self):
        """빈 HTML 테스트"""
        result = await self.converter.convert("")
        
        assert result['status'] == 'success'
        assert result['markdown'] == ""
    
    @pytest.mark.asyncio
    async def test_invalid_html(self):
        """잘못된 HTML 테스트"""
        html = "<h1>제목</h1><p>문단</p><invalid>잘못된 태그</invalid>"
        result = await self.converter.convert(html)
        
        # 잘못된 태그는 무시되고 나머지는 변환됨
        assert result['status'] == 'success'
        assert '# 제목' in result['markdown']
        assert '문단' in result['markdown']


class TestHTMLParser:
    """HTML 파서 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.parser = HTMLParser()
    
    def test_parse_html_structure(self):
        """HTML 구조 파싱 테스트"""
        html = """
        <h1>제목</h1>
        <p>문단입니다.</p>
        <ul><li>항목</li></ul>
        """
        structure = self.parser.parse_html_structure(html)
        
        assert len(structure['headings']) == 1
        assert structure['headings'][0]['level'] == 1
        assert structure['headings'][0]['text'] == '제목'
        assert len(structure['paragraphs']) == 1
        assert len(structure['lists']) == 1
    
    def test_extract_headings(self):
        """헤딩 추출 테스트"""
        html = """
        <h1>제목 1</h1>
        <h2>제목 2</h2>
        <h3>제목 3</h3>
        """
        structure = self.parser.parse_html_structure(html)
        
        assert len(structure['headings']) == 3
        assert structure['headings'][0]['level'] == 1
        assert structure['headings'][1]['level'] == 2
        assert structure['headings'][2]['level'] == 3
    
    def test_extract_tables(self):
        """표 추출 테스트"""
        html = """
        <table>
            <tr><th>헤더1</th><th>헤더2</th></tr>
            <tr><td>데이터1</td><td>데이터2</td></tr>
        </table>
        """
        structure = self.parser.parse_html_structure(html)
        
        assert len(structure['tables']) == 1
        table = structure['tables'][0]
        assert len(table['headers']) == 2
        assert table['headers'][0] == '헤더1'
        assert len(table['rows']) == 1
        assert table['rows'][0][0] == '데이터1'


class TestConversionValidator:
    """변환 검증기 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.validator = ConversionValidator()
    
    def test_validate_conversion_success(self):
        """성공적인 변환 검증 테스트"""
        html = "<h1>제목</h1><p>문단</p>"
        markdown = "# 제목\n\n문단"
        
        result = self.validator.validate_conversion(html, markdown)
        
        assert result['is_valid'] == True
        assert result['quality_score'] >= 90
        assert len(result['issues']) == 0
    
    def test_validate_conversion_failure(self):
        """실패한 변환 검증 테스트"""
        html = "<h1>제목</h1><p>문단</p>"
        markdown = ""  # 빈 변환 결과
        
        result = self.validator.validate_conversion(html, markdown)
        
        assert result['is_valid'] == False
        assert result['quality_score'] == 0
        assert len(result['issues']) > 0
    
    def test_validate_structure_integrity(self):
        """구조 무결성 검증 테스트"""
        html = "<h1>제목</h1><table><tr><td>데이터</td></tr></table>"
        markdown = "# 제목\n\n| 데이터 |\n| --- |"  # 표가 제대로 변환됨
        
        result = self.validator.validate_conversion(html, markdown)
        
        assert result['is_valid'] == True
        assert result['quality_score'] >= 70


if __name__ == "__main__":
    pytest.main([__file__])
