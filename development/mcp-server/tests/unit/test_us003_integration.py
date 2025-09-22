#!/usr/bin/env python3
"""
US-003 HTML→MD 변환 기능 통합 테스트
"""
import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from htmlconverter import HTMLToMarkdownConverter

async def test_html_to_md_converter():
    """HTML→MD 변환기 직접 테스트"""
    print("🔧 HTML→MD 변환기 직접 테스트")
    print("=" * 50)
    
    converter = HTMLToMarkdownConverter()
    
    # 테스트 케이스 1: 기본 HTML 변환
    print("\n📝 테스트 1: 기본 HTML 변환")
    html1 = """
    <h1>API 설계서</h1>
    <h2>설계 규칙</h2>
    <p><strong>RULE-API-001</strong> (MUST): 모든 API는 RESTful 원칙을 따라야 한다</p>
    <ul>
        <li>리소스는 명사로 표현</li>
        <li>HTTP 메서드는 동사로 표현</li>
    </ul>
    """
    
    result1 = await converter.convert(html1)
    print(f"✅ 상태: {result1['status']}")
    print(f"📄 변환된 Markdown:")
    print(result1['markdown'])
    print(f"📊 메타데이터: {result1['metadata']}")
    print(f"🔧 변환 정보: {result1['conversion_info']}")
    
    # 테스트 케이스 2: 복잡한 HTML 구조
    print("\n📝 테스트 2: 복잡한 HTML 구조")
    html2 = """
    <h1>데이터 모델 설계</h1>
    <h2>엔티티 정의</h2>
    <table>
        <thead>
            <tr><th>엔티티명</th><th>설명</th><th>속성 수</th></tr>
        </thead>
        <tbody>
            <tr><td>User</td><td>사용자 정보</td><td>5</td></tr>
            <tr><td>Project</td><td>프로젝트 정보</td><td>8</td></tr>
        </tbody>
    </table>
    <h3>코드 예시</h3>
    <pre><code class="language-python">
class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
    </code></pre>
    <blockquote>
        <p>참고: 모든 엔티티는 BaseModel을 상속받아야 합니다.</p>
    </blockquote>
    """
    
    result2 = await converter.convert(html2, save_to_file=True)
    print(f"✅ 상태: {result2['status']}")
    print(f"📄 변환된 Markdown:")
    print(result2['markdown'])
    print(f"💾 저장된 파일: {result2['conversion_info']['file_path']}")
    
    # 테스트 케이스 3: 에러 처리
    print("\n📝 테스트 3: 에러 처리")
    try:
        result3 = await converter.convert(None)
        print(f"❌ 상태: {result3['status']}")
        print(f"⚠️ 메시지: {result3['message']}")
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
    
    # 테스트 케이스 4: 빈 HTML
    print("\n📝 테스트 4: 빈 HTML")
    result4 = await converter.convert("")
    print(f"✅ 상태: {result4['status']}")
    print(f"📄 변환된 Markdown: '{result4['markdown']}'")
    
    return True

async def test_mcp_tools():
    """MCP 도구들 테스트"""
    print("\n🔧 MCP 도구들 테스트")
    print("=" * 50)
    
    try:
        # server.py에서 변환기 인스턴스 직접 사용
        from server import html_converter
        
        # 테스트 1: html_to_md 도구 (변환기 직접 사용)
        print("\n📝 MCP 도구 테스트 1: html_to_md (변환기 직접 사용)")
        test_html = """
        <h1>테스트 문서</h1>
        <p>이것은 <strong>테스트</strong> 문서입니다.</p>
        <ul>
            <li>항목 1</li>
            <li>항목 2</li>
        </ul>
        """
        
        result = await html_converter.convert(test_html, save_to_file=True)
        print(f"✅ 결과: {result['status']}")
        print(f"📄 Markdown:")
        print(result['markdown'])
        print(f"💾 파일 저장: {result['conversion_info']['saved_to_file']}")
        
        # 테스트 2: convert_saved_html 도구 (파일 기반 변환)
        print("\n📝 MCP 도구 테스트 2: convert_saved_html (파일 기반 변환)")
        
        # HTML 파일을 생성
        import aiofiles
        html_file_path = "test_input.html"
        async with aiofiles.open(html_file_path, 'w', encoding='utf-8') as f:
            await f.write(test_html)
        
        # convert_saved_html 로직 직접 구현
        try:
            # HTML 파일 읽기
            async with aiofiles.open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = await f.read()
            
            # Markdown으로 변환
            convert_result = await html_converter.convert(
                html_content, 
                preserve_structure=True, 
                save_to_file=True,
                output_path="test_output.md"
            )
            
            # HTML 파일 경로 정보 추가
            convert_result["metadata"]["source_html_file"] = html_file_path
            
            print(f"✅ 결과: {convert_result['status']}")
            print(f"📄 Markdown:")
            print(convert_result['markdown'])
            print(f"📁 소스 파일: {convert_result['metadata']['source_html_file']}")
            
            # 정리
            if os.path.exists(html_file_path):
                os.remove(html_file_path)
            if os.path.exists("test_output.md"):
                os.remove("test_output.md")
            
        except Exception as e:
            print(f"❌ 파일 기반 변환 실패: {e}")
            if os.path.exists(html_file_path):
                os.remove(html_file_path)
        
        return True
        
    except Exception as e:
        print(f"❌ MCP 도구 테스트 실패: {e}")
        return False

async def test_us003_requirements():
    """US-003 요구사항 검증"""
    print("\n📋 US-003 요구사항 검증")
    print("=" * 50)
    
    converter = HTMLToMarkdownConverter()
    requirements_met = []
    
    # AC1: HTML 문서를 Markdown 형식으로 변환할 수 있다
    print("\n✅ AC1: HTML→MD 변환")
    test_html = "<h1>제목</h1><p>내용</p>"
    result = await converter.convert(test_html)
    if result['status'] == 'success' and result['markdown']:
        requirements_met.append("AC1")
        print("✅ 통과: HTML을 Markdown으로 변환 가능")
    else:
        print("❌ 실패: HTML→MD 변환 불가")
    
    # AC2: 헤딩 태그(h1, h2, h3)를 Markdown 헤딩으로 변환할 수 있다
    print("\n✅ AC2: 헤딩 변환")
    heading_html = "<h1>제목1</h1><h2>제목2</h2><h3>제목3</h3>"
    result = await converter.convert(heading_html)
    if ('# 제목1' in result['markdown'] and 
        '## 제목2' in result['markdown'] and 
        '### 제목3' in result['markdown']):
        requirements_met.append("AC2")
        print("✅ 통과: h1, h2, h3 헤딩 변환 가능")
    else:
        print("❌ 실패: 헤딩 변환 불가")
    
    # AC3: 리스트 태그(ul, ol)를 Markdown 리스트로 변환할 수 있다
    print("\n✅ AC3: 리스트 변환")
    list_html = "<ul><li>항목1</li><li>항목2</li></ul><ol><li>순서1</li><li>순서2</li></ol>"
    result = await converter.convert(list_html)
    if ('- 항목1' in result['markdown'] and 
        '1. 순서1' in result['markdown']):
        requirements_met.append("AC3")
        print("✅ 통과: ul, ol 리스트 변환 가능")
    else:
        print("❌ 실패: 리스트 변환 불가")
    
    # AC4: 코드 블록을 Markdown 코드 블록으로 변환할 수 있다
    print("\n✅ AC4: 코드 블록 변환")
    code_html = "<pre><code>print('Hello World')</code></pre>"
    result = await converter.convert(code_html)
    if '```' in result['markdown'] and 'print' in result['markdown']:
        requirements_met.append("AC4")
        print("✅ 통과: 코드 블록 변환 가능")
    else:
        print("❌ 실패: 코드 블록 변환 불가")
    
    # AC5: 변환된 Markdown을 파일로 저장할 수 있다
    print("\n✅ AC5: 파일 저장")
    result = await converter.convert(test_html, save_to_file=True)
    if result['conversion_info']['saved_to_file'] and result['conversion_info']['file_path']:
        requirements_met.append("AC5")
        print("✅ 통과: Markdown 파일 저장 가능")
        # 정리
        if os.path.exists(result['conversion_info']['file_path']):
            os.remove(result['conversion_info']['file_path'])
    else:
        print("❌ 실패: 파일 저장 불가")
    
    # AC6: 변환 실패 시 적절한 에러 메시지를 출력한다
    print("\n✅ AC6: 에러 처리")
    try:
        result = await converter.convert(None)
        if result['status'] == 'error' and '오류가 발생했습니다' in result['message']:
            requirements_met.append("AC6")
            print("✅ 통과: 에러 메시지 출력 가능")
        else:
            print("❌ 실패: 에러 처리 불가")
    except Exception as e:
        print(f"❌ 실패: 예외 발생 - {e}")
    
    print(f"\n📊 요구사항 달성률: {len(requirements_met)}/6 ({len(requirements_met)/6*100:.1f}%)")
    print(f"✅ 달성된 요구사항: {', '.join(requirements_met)}")
    
    return len(requirements_met) == 6

async def main():
    """메인 테스트 함수"""
    print("🚀 US-003 HTML→MD 변환 기능 테스트 시작")
    print("=" * 60)
    
    try:
        # 1. 변환기 직접 테스트
        success1 = await test_html_to_md_converter()
        
        # 2. MCP 도구 테스트
        success2 = await test_mcp_tools()
        
        # 3. 요구사항 검증
        success3 = await test_us003_requirements()
        
        print("\n" + "=" * 60)
        print("📋 테스트 결과 요약")
        print("=" * 60)
        print(f"🔧 변환기 직접 테스트: {'✅ 성공' if success1 else '❌ 실패'}")
        print(f"🔧 MCP 도구 테스트: {'✅ 성공' if success2 else '❌ 실패'}")
        print(f"📋 요구사항 검증: {'✅ 성공' if success3 else '❌ 실패'}")
        
        overall_success = success1 and success2 and success3
        print(f"\n🎯 전체 결과: {'✅ 모든 테스트 통과!' if overall_success else '❌ 일부 테스트 실패'}")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
