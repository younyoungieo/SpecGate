#!/usr/bin/env python3
"""
Confluence HTML 파일을 사용한 US-003 테스트
"""
import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from htmlconverter import HTMLToMarkdownConverter

async def test_confluence_html_conversion():
    """Confluence HTML 파일 변환 테스트"""
    print("🌐 Confluence HTML 파일 변환 테스트")
    print("=" * 60)
    
    # HTML 파일 경로
    html_file_path = "../data/html_files/design_20250922_132913/SpecGate_데이터_모델_설계서_1.html"
    
    if not os.path.exists(html_file_path):
        print(f"❌ HTML 파일을 찾을 수 없습니다: {html_file_path}")
        return False
    
    try:
        # HTML 파일 읽기
        import aiofiles
        async with aiofiles.open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = await f.read()
        
        print(f"📁 HTML 파일: {html_file_path}")
        print(f"📏 파일 크기: {len(html_content):,} bytes")
        
        # 변환기 초기화
        converter = HTMLToMarkdownConverter()
        
        # HTML→MD 변환
        print("\n🔄 HTML→MD 변환 중...")
        result = await converter.convert(
            html_content, 
            preserve_structure=True, 
            save_to_file=True,
            output_path="../data/markdown_files/confluence_converted.md"
        )
        
        print(f"✅ 변환 상태: {result['status']}")
        
        if result['status'] == 'success':
            print(f"📄 변환된 Markdown (처음 500자):")
            print("-" * 50)
            print(result['markdown'][:500] + "..." if len(result['markdown']) > 500 else result['markdown'])
            print("-" * 50)
            
            print(f"\n📊 변환 정보:")
            print(f"  - 변환된 요소 수: {result['conversion_info']['elements_converted']}")
            print(f"  - 파일 저장: {result['conversion_info']['saved_to_file']}")
            print(f"  - 저장 경로: {result['conversion_info']['file_path']}")
            
            print(f"\n📋 메타데이터:")
            for key, value in result['metadata'].items():
                print(f"  - {key}: {value}")
            
            # 변환 품질 검증
            print(f"\n🔍 변환 품질 검증:")
            markdown = result['markdown']
            
            # 헤딩 검사
            heading_count = markdown.count('#')
            print(f"  - 헤딩 수: {heading_count}")
            
            # 리스트 검사
            list_count = markdown.count('- ') + markdown.count('1. ')
            print(f"  - 리스트 항목 수: {list_count}")
            
            # 코드 블록 검사
            code_block_count = markdown.count('```')
            print(f"  - 코드 블록 수: {code_block_count // 2}")
            
            # 표 검사
            table_count = markdown.count('| --- |')
            print(f"  - 표 수: {table_count}")
            
            # 링크 검사
            link_count = markdown.count('](')
            print(f"  - 링크 수: {link_count}")
            
            print(f"\n✅ Confluence HTML 변환 성공!")
            return True
            
        else:
            print(f"❌ 변환 실패: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        return False

async def test_design_document_structure():
    """설계 문서 구조 분석 테스트"""
    print("\n📋 설계 문서 구조 분석")
    print("=" * 60)
    
    html_file_path = "../data/html_files/design_20250922_132913/SpecGate_데이터_모델_설계서_1.html"
    
    try:
        import aiofiles
        async with aiofiles.open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = await f.read()
        
        converter = HTMLToMarkdownConverter()
        result = await converter.convert(html_content)
        
        if result['status'] == 'success':
            markdown = result['markdown']
            
            # 설계 문서 특화 검사
            print("🔍 설계 문서 특화 요소 검사:")
            
            # RULE 패턴 검사
            rule_patterns = ['RULE-', 'MUST', 'SHOULD', 'MAY', 'MUST NOT']
            rule_found = any(pattern in markdown for pattern in rule_patterns)
            print(f"  - 설계 규칙 패턴: {'✅ 발견' if rule_found else '❌ 없음'}")
            
            # 기술적 내용 검사
            tech_keywords = ['API', '데이터', '모델', '설계', '구조', '클래스', '메서드']
            tech_found = any(keyword in markdown for keyword in tech_keywords)
            print(f"  - 기술적 키워드: {'✅ 발견' if tech_found else '❌ 없음'}")
            
            # 표 구조 검사
            has_tables = '| --- |' in markdown
            print(f"  - 표 구조: {'✅ 발견' if has_tables else '❌ 없음'}")
            
            # 코드 예시 검사
            has_code = '```' in markdown
            print(f"  - 코드 예시: {'✅ 발견' if has_code else '❌ 없음'}")
            
            # 전체적인 구조 품질 평가
            structure_score = 0
            if rule_found: structure_score += 25
            if tech_found: structure_score += 25
            if has_tables: structure_score += 25
            if has_code: structure_score += 25
            
            print(f"\n📊 설계 문서 구조 점수: {structure_score}/100")
            
            if structure_score >= 75:
                print("✅ 설계 문서 구조가 잘 보존되었습니다!")
            elif structure_score >= 50:
                print("⚠️ 설계 문서 구조가 부분적으로 보존되었습니다.")
            else:
                print("❌ 설계 문서 구조가 제대로 보존되지 않았습니다.")
            
            return structure_score >= 50
            
        else:
            print(f"❌ 구조 분석 실패: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ 구조 분석 중 오류: {e}")
        return False

async def main():
    """메인 테스트 함수"""
    print("🚀 Confluence HTML 파일을 사용한 US-003 테스트")
    print("=" * 70)
    
    try:
        # 1. Confluence HTML 변환 테스트
        success1 = await test_confluence_html_conversion()
        
        # 2. 설계 문서 구조 분석 테스트
        success2 = await test_design_document_structure()
        
        print("\n" + "=" * 70)
        print("📋 Confluence HTML 테스트 결과 요약")
        print("=" * 70)
        print(f"🌐 Confluence HTML 변환: {'✅ 성공' if success1 else '❌ 실패'}")
        print(f"📋 설계 문서 구조 분석: {'✅ 성공' if success2 else '❌ 실패'}")
        
        overall_success = success1 and success2
        print(f"\n🎯 전체 결과: {'✅ 모든 테스트 통과!' if overall_success else '❌ 일부 테스트 실패'}")
        
        if overall_success:
            print("\n🎉 US-003 HTML→MD 변환 기능이 실제 Confluence 문서에서도 정상 작동합니다!")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
