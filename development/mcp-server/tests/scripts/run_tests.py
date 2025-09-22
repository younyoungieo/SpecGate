#!/usr/bin/env python3
"""
US-002 speclint.lint 테스트 실행 스크립트
Test Architect Quinn이 설계한 테스트 케이스를 실행합니다.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """테스트 실행"""
    print("🧪 US-002 speclint.lint 테스트 실행 시작")
    print("=" * 50)
    
    # 현재 디렉토리를 mcp-server로 변경
    os.chdir(Path(__file__).parent)
    
    # P0 테스트 실행 (Critical)
    print("\n🔥 P0 (Critical) 테스트 실행 중...")
    p0_result = subprocess.run([
        "python", "-m", "pytest", 
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_001_perfect_document_structure",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_002_title_format_validation",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_003_design_rules_section",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_004_rule_id_format",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_005_rule_type_validation",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_006_technical_spec_section",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_007_quality_score_calculation",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_008_deduction_calculation",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_009_final_score_range",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_011_error_message_generation",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_012_parsing_failure_error",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_013_auto_approval_logic",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_014_hitl_review_logic",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_015_mandatory_fix_logic",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_018_basic_error_handling",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_019_github_api_failure_handling",
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    if p0_result.returncode != 0:
        print("❌ P0 테스트 실패!")
        print(p0_result.stdout)
        print(p0_result.stderr)
        return False
    else:
        print("✅ P0 테스트 통과!")
    
    # P1 테스트 실행 (High)
    print("\n⚡ P1 (High) 테스트 실행 중...")
    p1_result = subprocess.run([
        "python", "-m", "pytest",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_010_log_message_generation",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_016_improvement_suggestions",
        "../unit/test_server.py::TestSpecLintLint::test_us002_unit_017_message_generation",
        "../integration/test_server.py::TestSpecLintIntegration::test_us002_int_001_document_structure_analysis",
        "../integration/test_server.py::TestSpecLintIntegration::test_us002_int_002_template_compliance_check",
        "../integration/test_server.py::TestSpecLintIntegration::test_us002_int_003_quality_grade_classification",
        "../integration/test_server.py::TestSpecLintIntegration::test_us002_int_004_logging_integration",
        "../integration/test_server.py::TestSpecLintIntegration::test_us002_int_005_error_handling_integration",
        "../integration/test_server.py::TestSpecLintIntegration::test_us002_int_006_batch_processing_logic",
        "../integration/test_server.py::TestSpecLintIntegration::test_us002_int_007_partial_failure_handling",
        "../integration/test_server.py::TestSpecLintIntegration::test_us002_int_008_github_issue_creation_logic",
        "../integration/test_server.py::TestSpecLintIntegration::test_us002_int_009_suggestion_generation_integration",
        "../integration/test_server.py::TestSpecLintIntegration::test_us002_int_010_error_handling_system",
        "../e2e/test_server.py::TestSpecLintE2E::test_us002_e2e_002_hitl_workflow",
        "../e2e/test_server.py::TestSpecLintE2E::test_us002_e2e_003_quality_processing_workflow",
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    if p1_result.returncode != 0:
        print("⚠️ P1 테스트 일부 실패 (개발 중이므로 계속 진행)")
        print(p1_result.stdout)
        print(p1_result.stderr)
    else:
        print("✅ P1 테스트 통과!")
    
    # P2 테스트 실행 (Medium)
    print("\n📋 P2 (Medium) 테스트 실행 중...")
    p2_result = subprocess.run([
        "python", "-m", "pytest",
        "../e2e/test_server.py::TestSpecLintE2E::test_us002_e2e_001_batch_workflow",
        "../e2e/test_server.py::TestSpecLintE2E::test_us002_e2e_004_user_message_display",
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    if p2_result.returncode != 0:
        print("ℹ️ P2 테스트 일부 실패 (선택사항이므로 계속 진행)")
        print(p2_result.stdout)
        print(p2_result.stderr)
    else:
        print("✅ P2 테스트 통과!")
    
    print("\n" + "=" * 50)
    print("🎉 US-002 테스트 실행 완료!")
    print("📊 테스트 결과 요약:")
    print(f"  - P0 (Critical): {'✅ 통과' if p0_result.returncode == 0 else '❌ 실패'}")
    print(f"  - P1 (High): {'✅ 통과' if p1_result.returncode == 0 else '⚠️ 일부 실패'}")
    print(f"  - P2 (Medium): {'✅ 통과' if p2_result.returncode == 0 else 'ℹ️ 일부 실패'}")
    
    return p0_result.returncode == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)


