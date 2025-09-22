#!/usr/bin/env python3
"""
US-002 파일 기반 품질 검사 테스트
"""
import asyncio
import os
from speclint import SpecLint

async def test_file_based_quality_check():
    print('🧪 US-002 파일 기반 품질 검사 테스트')
    
    # 테스트용 Markdown 파일 생성
    test_content = '''# [SpecGate] 데이터 모델 설계서

## 2. 설계 규칙
### 2.1 MUST 규칙 (필수)
- **RULE-DATA-001** (MUST): 모든 엔티티는 고유 식별자를 가져야 한다
  - 적용 범위: 모든 데이터베이스 테이블
  - 근거: 데이터 무결성 보장
  - 참조: 데이터베이스 설계 원칙

### 2.2 SHOULD 규칙 (권장)
- **RULE-DATA-002** (SHOULD): 모든 테이블은 생성일시와 수정일시를 가져야 한다
  - 적용 범위: 모든 데이터베이스 테이블
  - 근거: 데이터 변경 이력 추적
  - 참조: 감사 로그 요구사항

## 3. 기술 스펙
### 3.1 데이터베이스 스키마 (ERD)
```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER {
        int id PK
        string name
        string email
        datetime created_at
        datetime updated_at
    }
    ORDER {
        int id PK
        int user_id FK
        decimal total_amount
        datetime created_at
    }
```

## 4. 변경 이력
| 버전 | 날짜 | 변경내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2024-12-19 | 초기 버전 | 김개발 |
'''
    
    # 테스트 파일 저장
    test_file_path = '../data/markdown_files/test_document.md'
    os.makedirs('../data/markdown_files', exist_ok=True)
    
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f'📁 테스트 파일 생성: {test_file_path}')
    
    # SpecLint 인스턴스 생성
    speclint = SpecLint()
    
    print('\n1. 파일 기반 품질 검사 테스트')
    try:
        # 파일 읽기
        with open(test_file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 품질 검사 실행
        result = await speclint.lint(markdown_content, 'full')
        
        print(f'   - 점수: {result.get("score", "N/A")}/100')
        print(f'   - 위반 사항: {len(result.get("violations", []))}개')
        print(f'   - 제안 사항: {len(result.get("suggestions", []))}개')
        
        # 품질 등급 확인
        score = result.get('score', 0)
        if score >= 90:
            print(f'   - 상태: ✅ 자동승인 (표준 준수)')
        elif score >= 70:
            print(f'   - 상태: ⚠️ HITL검토 필요')
        else:
            print(f'   - 상태: ❌ 필수수정 필요')
            
        # 위반 사항 상세 출력
        violations = result.get('violations', [])
        if violations:
            print('   - 위반 사항:')
            for i, violation in enumerate(violations, 1):
                print(f'     {i}. {violation.get("message", "N/A")}')
        
        # 제안 사항 출력
        suggestions = result.get('suggestions', [])
        if suggestions:
            print('   - 개선 제안:')
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f'     {i}. {suggestion}')
            
    except Exception as e:
        print(f'   ❌ 오류: {e}')
        import traceback
        traceback.print_exc()
    
    print('\n2. 존재하지 않는 파일 테스트')
    try:
        non_existent_file = '../data/markdown_files/non_existent.md'
        
        with open(non_existent_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        result = await speclint.lint(markdown_content, 'full')
        print(f'   - 점수: {result.get("score", "N/A")}/100')
        print(f'   - 상태: {"❌ 파일 없음" if result.get("score", 0) == 0 else "⚠️ 처리됨"}')
        
    except FileNotFoundError:
        print('   - 상태: ❌ 파일을 찾을 수 없음 (예상된 동작)')
    except Exception as e:
        print(f'   ❌ 예상치 못한 오류: {e}')
    
    print('\n✅ US-002 파일 기반 품질 검사 테스트 완료!')
    return True

if __name__ == "__main__":
    asyncio.run(test_file_based_quality_check())
