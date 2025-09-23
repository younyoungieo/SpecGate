#!/usr/bin/env python3
"""
SpecGate 입력 표준 검증 스크립트

Phase 1 표준 준수 여부를 검증하는 스크립트입니다.
개발자와 CI/CD 파이프라인에서 사용할 수 있습니다.

사용법:
    python scripts/validate-input-standards.py --help
    python scripts/validate-input-standards.py --check-confluence
    python scripts/validate-input-standards.py --check-speclint  
    python scripts/validate-input-standards.py --check-all

요구사항:
    - Python 3.8+
    - SpecGate MCP Server 환경
    - Confluence 접근 권한 (선택)
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# SpecGate 모듈 경로 추가
sys.path.append(str(Path(__file__).parent.parent / "development" / "mcp-server"))

try:
    from confluence_fetch import ConfluenceService
    from speclint_lint import SpecLint
    from html_to_md import HTMLToMarkdownConverter
except ImportError as e:
    print(f"❌ SpecGate 모듈을 가져올 수 없습니다: {e}")
    print("💡 development/mcp-server 디렉토리에서 실행하거나 PYTHONPATH를 설정하세요.")
    sys.exit(1)


class ValidationResult:
    """검증 결과를 담는 클래스"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.details = []
        self.start_time = datetime.now()
        self.end_time = None
    
    def add_pass(self, test_name: str, message: str = ""):
        self.passed += 1
        self.details.append({
            "status": "PASS",
            "test": test_name,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_fail(self, test_name: str, message: str, error: str = ""):
        self.failed += 1
        self.details.append({
            "status": "FAIL", 
            "test": test_name,
            "message": message,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_warning(self, test_name: str, message: str):
        self.warnings += 1
        self.details.append({
            "status": "WARN",
            "test": test_name, 
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def finish(self):
        self.end_time = datetime.now()
    
    def get_summary(self) -> Dict[str, Any]:
        duration = None
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            "summary": {
                "passed": self.passed,
                "failed": self.failed,
                "warnings": self.warnings,
                "total": self.passed + self.failed,
                "success_rate": f"{(self.passed / max(1, self.passed + self.failed) * 100):.1f}%",
                "duration_seconds": duration
            },
            "details": self.details,
            "metadata": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "validator_version": "1.0.0"
            }
        }


class SpecGateValidator:
    """SpecGate 표준 검증기"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.result = ValidationResult()
    
    def _setup_logging(self) -> logging.Logger:
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger("specgate.validator")
    
    async def validate_confluence_integration(self) -> bool:
        """Confluence 연동 검증"""
        self.logger.info("🔍 Confluence 연동 검증 시작")
        
        # 환경변수 검사
        required_vars = ["CONFLUENCE_DOMAIN", "CONFLUENCE_EMAIL", "CONFLUENCE_API_TOKEN"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.result.add_fail(
                "confluence_env_vars",
                f"필수 환경변수 누락: {', '.join(missing_vars)}",
                "Confluence API 연동을 위해 환경변수를 설정하세요"
            )
            return False
        
        self.result.add_pass("confluence_env_vars", "모든 필수 환경변수가 설정됨")
        
        # Confluence 서비스 초기화 테스트
        try:
            confluence_service = ConfluenceService()
            self.result.add_pass("confluence_service_init", "Confluence 서비스 초기화 성공")
        except Exception as e:
            self.result.add_fail(
                "confluence_service_init",
                "Confluence 서비스 초기화 실패",
                str(e)
            )
            return False
        
        # 실제 API 연결 테스트 (선택적)
        try:
            # 간단한 CQL 검색으로 연결 테스트
            test_result = await confluence_service.search_by_cql('type=page', 1)
            
            if test_result.get("status") == "success":
                self.result.add_pass("confluence_api_connection", "Confluence API 연결 성공")
            else:
                error_msg = test_result.get("metadata", {}).get("error", "Unknown error")
                self.result.add_fail(
                    "confluence_api_connection",
                    "Confluence API 연결 실패",
                    error_msg
                )
                return False
                
        except Exception as e:
            self.result.add_warning(
                "confluence_api_connection",
                f"Confluence API 테스트 중 오류: {str(e)} (네트워크 문제일 수 있음)"
            )
        
        return True
    
    async def validate_speclint_engine(self) -> bool:
        """SpecLint 엔진 검증"""
        self.logger.info("🔍 SpecLint 엔진 검증 시작")
        
        # SpecLint 초기화 테스트
        try:
            speclint = SpecLint()
            self.result.add_pass("speclint_init", "SpecLint 엔진 초기화 성공")
        except Exception as e:
            self.result.add_fail(
                "speclint_init",
                "SpecLint 엔진 초기화 실패",
                str(e)
            )
            return False
        
        # 테스트 문서로 품질 검사 테스트
        test_documents = [
            {
                "name": "valid_document",
                "content": """# [TestProject] API 설계서

## 1. 개요
- **목적**: 테스트용 API 설계서
- **배경**: 검증 목적
- **참고사항**: 없음

## 2. 설계 규칙
### 2.1 MUST 규칙 (필수)
- **RULE-API-001** (MUST): 모든 API는 JSON 형식으로 응답해야 한다
  - 적용 범위: 모든 REST API
  - 근거: 표준화
  - 참조: API 가이드

## 3. 기술 스펙
### 3.1 API 설계
테스트 스펙입니다.
""",
                "expected_score_min": 80
            },
            {
                "name": "invalid_document", 
                "content": "Invalid document without proper structure",
                "expected_score_max": 50
            }
        ]
        
        for test_doc in test_documents:
            try:
                result = await speclint.lint(test_doc["content"], "full")
                score = result.get("score", 0)
                
                if "expected_score_min" in test_doc:
                    if score >= test_doc["expected_score_min"]:
                        self.result.add_pass(
                            f"speclint_test_{test_doc['name']}",
                            f"품질 점수 {score}점 (기대값: {test_doc['expected_score_min']}점 이상)"
                        )
                    else:
                        self.result.add_fail(
                            f"speclint_test_{test_doc['name']}",
                            f"품질 점수 {score}점이 기대값 {test_doc['expected_score_min']}점보다 낮음",
                            f"SpecLint 규칙이 올바르게 작동하지 않을 수 있습니다"
                        )
                
                elif "expected_score_max" in test_doc:
                    if score <= test_doc["expected_score_max"]:
                        self.result.add_pass(
                            f"speclint_test_{test_doc['name']}",
                            f"품질 점수 {score}점 (기대값: {test_doc['expected_score_max']}점 이하)"
                        )
                    else:
                        self.result.add_fail(
                            f"speclint_test_{test_doc['name']}",
                            f"품질 점수 {score}점이 기대값 {test_doc['expected_score_max']}점보다 높음",
                            f"SpecLint 규칙이 너무 관대할 수 있습니다"
                        )
                        
            except Exception as e:
                self.result.add_fail(
                    f"speclint_test_{test_doc['name']}",
                    "SpecLint 검사 중 오류 발생",
                    str(e)
                )
                return False
        
        return True
    
    async def validate_html_converter(self) -> bool:
        """HTML→MD 변환기 검증"""
        self.logger.info("🔍 HTML→MD 변환기 검증 시작")
        
        # HTML 변환기 초기화 테스트
        try:
            converter = HTMLToMarkdownConverter()
            self.result.add_pass("html_converter_init", "HTML 변환기 초기화 성공")
        except Exception as e:
            self.result.add_fail(
                "html_converter_init",
                "HTML 변환기 초기화 실패",
                str(e)
            )
            return False
        
        # 테스트 HTML로 변환 테스트
        test_html = """
        <h1>Test Document</h1>
        <h2>Section 1</h2>
        <p>This is a test paragraph with <strong>bold</strong> text.</p>
        <ul>
            <li>List item 1</li>
            <li>List item 2</li>
        </ul>
        <pre><code>print("Hello World")</code></pre>
        """
        
        try:
            result = await converter.convert(
                html_content=test_html,
                preserve_structure=True,
                save_to_file=False
            )
            
            markdown = result.get("markdown", "")
            if markdown and "# Test Document" in markdown:
                self.result.add_pass(
                    "html_converter_test",
                    f"HTML→MD 변환 성공 (출력 길이: {len(markdown)}자)"
                )
            else:
                self.result.add_fail(
                    "html_converter_test",
                    "HTML→MD 변환 결과가 예상과 다름",
                    f"변환 결과: {markdown[:100]}..."
                )
                return False
                
        except Exception as e:
            self.result.add_fail(
                "html_converter_test",
                "HTML→MD 변환 중 오류 발생",
                str(e)
            )
            return False
        
        return True
    
    async def validate_file_structure(self) -> bool:
        """파일 구조 검증"""
        self.logger.info("🔍 파일 구조 검증 시작")
        
        # 프로젝트 루트 확인
        project_root = Path(__file__).parent.parent
        
        # 필수 디렉토리 확인
        required_dirs = [
            "development/mcp-server",
            "documentation",
            "docs",
            "rules", 
            "scripts"
        ]
        
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            if full_path.exists():
                self.result.add_pass(
                    f"dir_exists_{dir_path.replace('/', '_')}",
                    f"필수 디렉토리 존재: {dir_path}"
                )
            else:
                self.result.add_fail(
                    f"dir_exists_{dir_path.replace('/', '_')}",
                    f"필수 디렉토리 누락: {dir_path}",
                    "Phase 1 표준 디렉토리 구조를 확인하세요"
                )
        
        # 필수 파일 확인
        required_files = [
            "docs/authoring-guide.md",
            "docs/confluence-policy.md", 
            "rules/speclint-rules.yaml",
            "development/mcp-server/server.py",
            "development/mcp-server/README.md"
        ]
        
        for file_path in required_files:
            full_path = project_root / file_path
            if full_path.exists():
                self.result.add_pass(
                    f"file_exists_{file_path.replace('/', '_').replace('.', '_')}",
                    f"필수 파일 존재: {file_path}"
                )
            else:
                self.result.add_fail(
                    f"file_exists_{file_path.replace('/', '_').replace('.', '_')}",
                    f"필수 파일 누락: {file_path}",
                    "Phase 1 표준 산출물을 확인하세요"
                )
        
        return True
    
    async def validate_all(self) -> bool:
        """전체 검증 실행"""
        self.logger.info("🚀 SpecGate 전체 표준 검증 시작")
        
        validation_tasks = [
            ("파일 구조", self.validate_file_structure),
            ("HTML 변환기", self.validate_html_converter),
            ("SpecLint 엔진", self.validate_speclint_engine),
            ("Confluence 연동", self.validate_confluence_integration)
        ]
        
        all_passed = True
        
        for task_name, task_func in validation_tasks:
            self.logger.info(f"📋 {task_name} 검증 중...")
            try:
                task_result = await task_func()
                if not task_result:
                    all_passed = False
                    self.logger.warning(f"⚠️ {task_name} 검증에서 문제 발견")
                else:
                    self.logger.info(f"✅ {task_name} 검증 완료")
            except Exception as e:
                self.logger.error(f"❌ {task_name} 검증 중 오류: {e}")
                self.result.add_fail(
                    f"validation_{task_name.lower().replace(' ', '_')}",
                    f"{task_name} 검증 실행 실패",
                    str(e)
                )
                all_passed = False
        
        return all_passed
    
    def save_report(self, output_path: str):
        """검증 리포트 저장"""
        self.result.finish()
        report = self.result.get_summary()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"📄 검증 리포트 저장: {output_path}")
    
    def print_summary(self):
        """검증 결과 요약 출력"""
        self.result.finish()
        summary = self.result.get_summary()
        
        print("\n" + "="*80)
        print("🎯 SpecGate 표준 검증 결과")
        print("="*80)
        print(f"✅ 통과: {summary['summary']['passed']}")
        print(f"❌ 실패: {summary['summary']['failed']}")
        print(f"⚠️ 경고: {summary['summary']['warnings']}")
        print(f"📊 성공률: {summary['summary']['success_rate']}")
        print(f"⏱️ 소요시간: {summary['summary']['duration_seconds']:.2f}초")
        
        if summary['summary']['failed'] > 0:
            print("\n❌ 실패한 테스트:")
            for detail in summary['details']:
                if detail['status'] == 'FAIL':
                    print(f"   • {detail['test']}: {detail['message']}")
                    if detail.get('error'):
                        print(f"     오류: {detail['error']}")
        
        if summary['summary']['warnings'] > 0:
            print("\n⚠️ 경고 사항:")
            for detail in summary['details']:
                if detail['status'] == 'WARN':
                    print(f"   • {detail['test']}: {detail['message']}")


async def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="SpecGate Phase 1 표준 준수 검증 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python scripts/validate-input-standards.py --check-all
  python scripts/validate-input-standards.py --check-confluence --verbose
  python scripts/validate-input-standards.py --check-speclint --output report.json
        """
    )
    
    parser.add_argument(
        "--check-all", 
        action="store_true",
        help="모든 구성 요소 검증"
    )
    parser.add_argument(
        "--check-confluence",
        action="store_true", 
        help="Confluence 연동만 검증"
    )
    parser.add_argument(
        "--check-speclint",
        action="store_true",
        help="SpecLint 엔진만 검증"
    )
    parser.add_argument(
        "--check-html-converter",
        action="store_true",
        help="HTML 변환기만 검증"
    )
    parser.add_argument(
        "--check-files",
        action="store_true",
        help="파일 구조만 검증"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="검증 리포트 저장 경로 (JSON 형식)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="상세 로그 출력"
    )
    
    args = parser.parse_args()
    
    # 로그 레벨 설정
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 검증기 초기화
    validator = SpecGateValidator()
    
    # 검증 실행
    success = True
    
    try:
        if args.check_all or not any([
            args.check_confluence, args.check_speclint, 
            args.check_html_converter, args.check_files
        ]):
            success = await validator.validate_all()
        else:
            if args.check_files:
                success &= await validator.validate_file_structure()
            if args.check_html_converter:
                success &= await validator.validate_html_converter()
            if args.check_speclint:
                success &= await validator.validate_speclint_engine()
            if args.check_confluence:
                success &= await validator.validate_confluence_integration()
    
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단됨")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        sys.exit(1)
    
    # 결과 출력
    validator.print_summary()
    
    # 리포트 저장
    if args.output:
        validator.save_report(args.output)
    
    # 종료 코드
    if success and validator.result.failed == 0:
        print("\n🎉 모든 검증이 성공적으로 완료되었습니다!")
        sys.exit(0)
    else:
        print("\n💔 일부 검증에서 문제가 발견되었습니다. 위의 결과를 확인하세요.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
