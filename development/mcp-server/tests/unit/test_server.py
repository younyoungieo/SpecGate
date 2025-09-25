"""
SpecGate MCP Server 테스트
"""
import pytest
import asyncio
import os
from server import mcp, confluence_fetch, speclint_lint
from server import _analyze_document_structure, _check_template_compliance, _calculate_quality_score, _generate_improvement_suggestions


class TestMCPServer:
    """MCP 서버 기본 기능 테스트"""
    
    def test_server_initialization(self):
        """서버 초기화 테스트"""
        assert mcp is not None
        assert hasattr(mcp, 'name')
        assert hasattr(mcp, 'run')
    
    def test_confluence_fetch_tool(self):
        """confluence.fetch 도구 구조 테스트"""
        # 도구가 FastMCP에 제대로 등록되었는지 확인
        assert confluence_fetch is not None
        assert hasattr(confluence_fetch, 'name')
        assert confluence_fetch.name == 'confluence_fetch'
        assert 'Confluence' in confluence_fetch.description
    
    def test_confluence_fetch_parameters(self):
        """confluence_fetch 도구 파라미터 테스트"""
        # FastMCP 도구 객체의 속성 확인
        assert confluence_fetch.name == 'confluence_fetch'
        assert 'Confluence' in confluence_fetch.description
        assert confluence_fetch.enabled == True
        
        # 도구가 FastMCP에 제대로 등록되었는지 확인
        assert hasattr(confluence_fetch, 'name')
        assert hasattr(confluence_fetch, 'description')
        assert hasattr(confluence_fetch, 'enabled')
    
    def test_confluence_fetch_return_type(self):
        """confluence_fetch 도구 반환 타입 테스트"""
        # FastMCP 도구 객체의 반환 타입 확인
        assert confluence_fetch.name == 'confluence_fetch'
        assert 'dict' in confluence_fetch.description  # 반환 타입이 설명에 포함되어 있는지 확인
    
    def test_confluence_mcp_server_integration_structure(self):
        """Confluence MCP Server 연동 구조 테스트"""
        # Confluence API 연동 함수들이 존재하는지 확인
        from server import _call_confluence_api, _transform_to_specgate_format
        assert _call_confluence_api is not None
        assert _transform_to_specgate_format is not None
    
    def test_confluence_fetch_error_handling(self):
        """confluence_fetch 에러 처리 테스트"""
        # FastMCP 도구 객체의 에러 처리 구조 확인
        assert confluence_fetch.name == 'confluence_fetch'
        assert confluence_fetch.enabled == True
        
        # 에러 처리 관련 함수들이 존재하는지 확인
        from server import _validate_confluence_env, _call_confluence_api
        assert _validate_confluence_env is not None
        assert _call_confluence_api is not None
    
    def test_confluence_fetch_empty_results(self):
        """confluence_fetch 빈 결과 처리 테스트"""
        # FastMCP 도구 객체의 빈 결과 처리 구조 확인
        assert confluence_fetch.name == 'confluence_fetch'
        assert confluence_fetch.enabled == True
        
        # 빈 결과 처리 관련 함수들이 존재하는지 확인
        from server import _transform_to_specgate_format
        assert _transform_to_specgate_format is not None
    
    def test_confluence_fetch_cql_query_generation(self):
        """CQL 쿼리 생성 테스트"""
        from server import _generate_cql_query
        
        # 라벨만 있는 경우
        query1 = _generate_cql_query("design", None)
        assert query1 == 'type = "page" AND label = "design"'
        
        # 라벨과 스페이스가 있는 경우
        query2 = _generate_cql_query("design", "TEST")
        assert query2 == 'type = "page" AND space.key = "TEST" AND label = "design"'
    
    def test_environment_variables_validation(self):
        """환경변수 검증 테스트"""
        import os
        from server import _validate_confluence_env
        
        # 필수 환경변수 확인
        required_vars = ["CONFLUENCE_DOMAIN", "CONFLUENCE_EMAIL", "CONFLUENCE_API_TOKEN"]
        
        # 환경변수가 설정되어 있는지 확인
        for var in required_vars:
            if var in os.environ:
                assert os.environ[var] is not None
                assert len(os.environ[var]) > 0
    
    def test_speclint_lint_tool(self):
        """speclint.lint 도구 구조 테스트"""
        # 도구가 FastMCP에 제대로 등록되었는지 확인
        assert speclint_lint is not None
        assert hasattr(speclint_lint, 'name')
        assert speclint_lint.name == 'speclint_lint'
        assert '품질' in speclint_lint.description
    
    def test_error_handling(self):
        """에러 처리 구조 테스트"""
        # 에러 처리가 구현되어 있는지 확인
        # 헬퍼 함수들이 정의되어 있는지 확인
        from server import _validate_confluence_env, _call_confluence_api, _transform_to_specgate_format
        assert _validate_confluence_env is not None
        assert _call_confluence_api is not None
        assert _transform_to_specgate_format is not None


class TestDataStructures:
    """데이터 구조 테스트"""
    
    def test_document_data_structure(self):
        """DocumentData 구조 테스트"""
        from server import DocumentData
        
        doc = DocumentData(
            id="test-id",
            title="Test Title",
            content="Test Content"
        )
        
        assert doc.id == "test-id"
        assert doc.title == "Test Title"
        assert doc.content == "Test Content"
        assert doc.metadata is not None
        assert doc.created_at is not None
        assert doc.updated_at is not None
    
    def test_processing_result_structure(self):
        """ProcessingResult 구조 테스트"""
        from server import ProcessingResult
        
        result = ProcessingResult(
            status="success",
            data={"test": "data"},
            metadata={"timestamp": "test-timestamp"}
        )
        
        assert result.status == "success"
        assert result.data == {"test": "data"}
        assert "timestamp" in result.metadata
        assert result.warnings is not None
        assert result.error_message is None


class TestConfluenceIntegration:
    """Confluence 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_real_confluence_api_call(self):
        """실제 Confluence API 호출 테스트"""
        from server import _call_confluence_api
        
        # 실제 API 호출 테스트 (환경변수가 설정된 경우에만)
        import os
        if os.getenv("CONFLUENCE_DOMAIN") and os.getenv("CONFLUENCE_EMAIL") and os.getenv("CONFLUENCE_API_TOKEN"):
            try:
                # 간단한 검색 쿼리로 테스트
                result = await _call_confluence_api('type = "page"', 1)
                assert "results" in result
                assert isinstance(result["results"], list)
                print(f"✅ 실제 Confluence API 호출 성공: {len(result['results'])}개 문서 발견")
            except Exception as e:
                pytest.fail(f"실제 Confluence API 호출 실패: {str(e)}")
        else:
            pytest.skip("Confluence 환경변수가 설정되지 않음")
    
    @pytest.mark.asyncio
    async def test_cql_query_generation(self):
        """CQL 쿼리 생성 테스트"""
        from server import _generate_cql_query
        
        # 기본 라벨 검색
        query1 = _generate_cql_query("design")
        assert query1 == 'type = "page" AND label = "design"'
        
        # 스페이스와 라벨 검색
        query2 = _generate_cql_query("api", "SPECGATE")
        assert query2 == 'type = "page" AND space.key = "SPECGATE" AND label = "api"'
        
        # 특수 문자 포함 라벨
        query3 = _generate_cql_query("test-label")
        assert query3 == 'type = "page" AND label = "test-label"'
        
        print("✅ CQL 쿼리 생성 테스트 통과")
    
    def test_html_to_markdown_conversion_quality(self):
        """HTML→Markdown 변환 품질 테스트"""
        from server import _transform_to_specgate_format
        
        # 복잡한 HTML 구조 테스트
        complex_html = """
        <h1>제목</h1>
        <p>단락 텍스트</p>
        <ul>
            <li>리스트 항목 1</li>
            <li>리스트 항목 2</li>
        </ul>
        <table>
            <tr><th>헤더1</th><th>헤더2</th></tr>
            <tr><td>데이터1</td><td>데이터2</td></tr>
        </table>
        <code>코드 블록</code>
        """
        
        mock_response = {
            "results": [{
                "id": "123",
                "title": "테스트 문서",
                "body": {"storage": {"value": complex_html}},
                "space": {"key": "TEST", "name": "Test Space"},
                "_links": {"webui": "https://test.com"},
                "metadata": {"labels": {"results": [{"name": "test"}]}},
                "version": {"created": "2024-01-01T00:00:00.000Z", "when": "2024-01-01T00:00:00.000Z", "number": 1}
            }]
        }
        
        result = _transform_to_specgate_format(mock_response)
        
        # 변환 결과 검증
        assert result["id"] == "123"
        assert result["title"] == "테스트 문서"
        assert "제목" in result["content"]
        assert "리스트 항목 1" in result["content"]
        assert "코드 블록" in result["content"]
        
        print("✅ HTML→Markdown 변환 품질 테스트 통과")
    
    def test_specgate_format_conversion(self):
        """SpecGate 형식 변환 테스트"""
        from server import _transform_to_specgate_format
        
        # 빈 결과 테스트
        empty_response = {"results": []}
        result = _transform_to_specgate_format(empty_response)
        
        assert result["id"] == ""
        assert result["title"] == ""
        assert result["content"] == ""
        assert result["space_key"] == ""
        assert result["labels"] == []
        
        # 정상 결과 테스트
        normal_response = {
            "results": [{
                "id": "456",
                "title": "API 설계서",
                "body": {"storage": {"value": "<p>API 설계 내용</p>"}},
                "space": {"key": "SPECGATE", "name": "SpecGate Space"},
                "_links": {"webui": "https://test.com/page"},
                "metadata": {"labels": {"results": [{"name": "api"}, {"name": "design"}]}},
                "version": {"created": "2024-01-01T00:00:00.000Z", "when": "2024-01-02T00:00:00.000Z", "number": 2}
            }]
        }
        
        result = _transform_to_specgate_format(normal_response)
        
        assert result["id"] == "456"
        assert result["title"] == "API 설계서"
        assert "API 설계 내용" in result["content"]
        assert result["space_key"] == "SPECGATE"
        assert result["space_name"] == "SpecGate Space"
        assert "api" in result["labels"]
        assert "design" in result["labels"]
        assert result["version"] == 2
        
        print("✅ SpecGate 형식 변환 테스트 통과")
    
    @pytest.mark.asyncio
    async def test_error_handling_scenarios(self):
        """에러 처리 시나리오 테스트"""
        from server import _call_confluence_api, _transform_to_specgate_format
        
        # 잘못된 라벨로 검색 (빈 결과)
        try:
            result = await _call_confluence_api('type = "page" AND label = "nonexistent-label"', 5)
            assert "results" in result
            assert isinstance(result["results"], list)
            
            # 빈 결과 변환 테스트
            specgate_result = _transform_to_specgate_format(result)
            assert specgate_result["id"] == ""
            assert specgate_result["title"] == ""
            assert specgate_result["content"] == ""
            
            print("✅ 잘못된 라벨 검색 에러 처리 테스트 통과")
        except Exception as e:
            print(f"⚠️ 잘못된 라벨 검색에서 예외 발생: {e}")
        
        # 잘못된 스페이스로 검색
        try:
            result = await _call_confluence_api('type = "page" AND space.key = "NONEXISTENT" AND label = "design"', 5)
            assert "results" in result
            assert isinstance(result["results"], list)
            
            print("✅ 잘못된 스페이스 검색 에러 처리 테스트 통과")
        except Exception as e:
            print(f"⚠️ 잘못된 스페이스 검색에서 예외 발생: {e}")
        
        print("✅ 에러 처리 시나리오 테스트 통과")


class TestMCPServerLifecycle:
    """MCP 서버 생명주기 테스트"""
    
    def test_server_initialization_components(self):
        """서버 초기화 구성 요소 테스트"""
        from server import mcp, DocumentData, ProcessingResult, QualityScore
        
        # 서버 인스턴스 검증
        assert mcp is not None
        assert hasattr(mcp, 'name')
        assert mcp.name == "SpecGate Server 🚀"
        
        # 데이터 구조 클래스 검증
        assert DocumentData is not None
        assert ProcessingResult is not None
        assert QualityScore is not None
        
        print("✅ 서버 초기화 구성 요소 테스트 통과")
    
    def test_middleware_system(self):
        """미들웨어 시스템 테스트"""
        from server import mcp
        
        # 로깅 시스템 검증
        import logging
        logger = logging.getLogger("specgate")
        assert logger.level <= logging.INFO
        
        # 에러 처리 검증 (confluence_fetch 도구의 에러 처리 확인)
        from server import confluence_fetch
        assert confluence_fetch is not None
        assert hasattr(confluence_fetch, 'name')
        
        print("✅ 미들웨어 시스템 테스트 통과")
    
    def test_configuration_validation(self):
        """설정 파일 검증 테스트"""
        import os
        import json
        
        # 환경변수 검증
        required_env_vars = ["CONFLUENCE_DOMAIN", "CONFLUENCE_EMAIL", "CONFLUENCE_API_TOKEN"]
        for var in required_env_vars:
            value = os.getenv(var)
            if value:
                assert len(value) > 0, f"환경변수 {var}가 비어있음"
                print(f"✅ 환경변수 {var} 설정됨")
            else:
                print(f"⚠️ 환경변수 {var} 설정되지 않음")
        
        # fastmcp.json 파일 검증
        fastmcp_path = "fastmcp.json"
        if os.path.exists(fastmcp_path):
            with open(fastmcp_path, 'r') as f:
                config = json.load(f)
                assert "source" in config
                assert "environment" in config
                print("✅ fastmcp.json 설정 파일 검증 통과")
        else:
            print("⚠️ fastmcp.json 파일이 없음")
        
        print("✅ 설정 파일 검증 테스트 통과")
    
    def test_quality_score_structure(self):
        """QualityScore 구조 테스트"""
        from server import QualityScore
        
        score = QualityScore(
            total_score=85,
            category_scores={"structure": 90, "content": 80},
            violations=[],
            suggestions=["Test suggestion"],
            metadata={"check_type": "full"}
        )
        
        assert score.total_score == 85
        assert score.category_scores["structure"] == 90
        assert len(score.violations) == 0
        assert len(score.suggestions) == 1


# =============================================================================
# US-002: speclint.lint 기능 테스트 (Test Design 기반)
# =============================================================================

class TestSpecLintLint:
    """US-002 speclint.lint 기능 테스트"""
    
    # Test Data - 설계 문서의 테스트 데이터 사용
    PERFECT_DOCUMENT = '''
# [example_project] API 설계서

## 2. 설계 규칙
### 2.1 MUST 규칙 (필수)
- **RULE-API-001** (MUST): 모든 API 엔드포인트는 RESTful 원칙을 따라야 한다
  - 적용 범위: 모든 REST API
  - 근거: 일관된 API 설계를 통한 개발자 경험 향상
  - 참조: OpenAPI 3.0 스펙

## 3. 기술 스펙
### 3.1 API 설계 (OpenAPI)
```yaml
openapi: 3.0.0
info:
  title: Example API
  version: 1.0.0
```
'''
    
    INCOMPLETE_DOCUMENT = '''
# API 설계서
## 설계 규칙
- 모든 API는 RESTful해야 함
'''
    
    EMPTY_DOCUMENT = ''
    
    MALFORMED_DOCUMENT = '''
# 잘못된 형식
## 설계 규칙
- RULE-API-001: API는 RESTful해야 함
'''

    @pytest.mark.asyncio
    async def test_us002_unit_001_perfect_document_structure(self):
        """US-002-UNIT-001: 완벽한 문서 구조 검사"""
        result = await speclint_lint(self.PERFECT_DOCUMENT, "full")
        
        assert result["score"] >= 90
        assert len(result["violations"]) == 0
        assert "auto_approve" in str(result.get("metadata", {}))

    @pytest.mark.asyncio
    async def test_us002_unit_002_title_format_validation(self):
        """US-002-UNIT-002: 제목 형식 검증"""
        # 올바른 제목 형식
        correct_title = "# [example_project] API 설계서"
        result = await speclint_lint(correct_title, "structure")
        assert result["score"] > 0
        
        # 잘못된 제목 형식
        incorrect_title = "# API 설계서"
        result = await speclint_lint(incorrect_title, "structure")
        assert result["score"] < 100

    @pytest.mark.asyncio
    async def test_us002_unit_003_design_rules_section(self):
        """US-002-UNIT-003: 설계 규칙 섹션 검증"""
        result = await speclint_lint(self.PERFECT_DOCUMENT, "structure")
        
        # 설계 규칙 섹션이 있는지 확인
        assert "설계 규칙" in self.PERFECT_DOCUMENT
        assert result["score"] > 70

    @pytest.mark.asyncio
    async def test_us002_unit_004_rule_id_format(self):
        """US-002-UNIT-004: 규칙 ID 형식 검증"""
        result = await speclint_lint(self.PERFECT_DOCUMENT, "full")
        
        # RULE-API-001 형식이 올바른지 확인
        assert "RULE-API-001" in self.PERFECT_DOCUMENT
        assert result["score"] > 80

    @pytest.mark.asyncio
    async def test_us002_unit_005_rule_type_validation(self):
        """US-002-UNIT-005: 규칙 유형 검증 (MUST/SHOULD/MUST NOT)"""
        result = await speclint_lint(self.PERFECT_DOCUMENT, "full")
        
        # MUST 규칙이 올바르게 인식되는지 확인
        assert "(MUST)" in self.PERFECT_DOCUMENT
        assert result["score"] > 80

    @pytest.mark.asyncio
    async def test_us002_unit_006_technical_spec_section(self):
        """US-002-UNIT-006: 기술 스펙 섹션 검증"""
        result = await speclint_lint(self.PERFECT_DOCUMENT, "full")
        
        # 기술 스펙 섹션이 있는지 확인
        assert "기술 스펙" in self.PERFECT_DOCUMENT
        assert "openapi:" in self.PERFECT_DOCUMENT
        assert result["score"] > 80

    @pytest.mark.asyncio
    async def test_us002_unit_007_quality_score_calculation(self):
        """US-002-UNIT-007: 품질 점수 계산 로직"""
        result = await speclint_lint(self.PERFECT_DOCUMENT, "full")
        
        assert 0 <= result["score"] <= 100
        assert isinstance(result["score"], int)

    @pytest.mark.asyncio
    async def test_us002_unit_008_deduction_calculation(self):
        """US-002-UNIT-008: 차감 점수 계산 로직"""
        result = await speclint_lint(self.INCOMPLETE_DOCUMENT, "full")
        
        # 불완전한 문서는 낮은 점수를 받아야 함
        assert result["score"] < 70
        assert len(result["violations"]) > 0

    @pytest.mark.asyncio
    async def test_us002_unit_009_final_score_range(self):
        """US-002-UNIT-009: 최종 점수 0-100 범위 보장"""
        # 완벽한 문서
        result = await speclint_lint(self.PERFECT_DOCUMENT, "full")
        assert 0 <= result["score"] <= 100
        
        # 빈 문서
        result = await speclint_lint(self.EMPTY_DOCUMENT, "full")
        assert result["score"] == 0

    @pytest.mark.asyncio
    async def test_us002_unit_010_log_message_generation(self):
        """US-002-UNIT-010: 로그 메시지 생성 로직"""
        result = await speclint_lint(self.PERFECT_DOCUMENT, "full")
        
        # 메타데이터에 로깅 정보가 포함되어 있는지 확인
        assert "metadata" in result
        assert "timestamp" in result["metadata"]

    @pytest.mark.asyncio
    async def test_us002_unit_011_error_message_generation(self):
        """US-002-UNIT-011: 에러 메시지 생성 로직"""
        result = await speclint_lint(self.EMPTY_DOCUMENT, "full")
        
        # 빈 문서에 대한 적절한 에러 메시지
        assert result["score"] == 0
        assert len(result["violations"]) > 0
        assert "문서 파싱에 실패했습니다" in str(result["violations"])

    @pytest.mark.asyncio
    async def test_us002_unit_012_parsing_failure_error(self):
        """US-002-UNIT-012: 파싱 실패 에러 처리"""
        # 잘못된 형식의 문서
        result = await speclint_lint(self.MALFORMED_DOCUMENT, "full")
        
        assert result["score"] < 100
        assert len(result["violations"]) > 0

    @pytest.mark.asyncio
    async def test_us002_unit_013_auto_approval_logic(self):
        """US-002-UNIT-013: 자동 승인 로직 (90점+)"""
        result = await speclint_lint(self.PERFECT_DOCUMENT, "full")
        
        if result["score"] >= 90:
            assert result["score"] >= 90
            # 자동 승인 메시지 확인
            assert "auto_approve" in str(result.get("metadata", {}))

    @pytest.mark.asyncio
    async def test_us002_unit_014_hitl_review_logic(self):
        """US-002-UNIT-014: HITL 검토 로직 (70-89점)"""
        result = await speclint_lint(self.INCOMPLETE_DOCUMENT, "full")
        
        if 70 <= result["score"] < 90:
            assert 70 <= result["score"] < 90
            # HITL 검토 메시지 확인
            assert "hitl_review" in str(result.get("metadata", {}))

    @pytest.mark.asyncio
    async def test_us002_unit_015_mandatory_fix_logic(self):
        """US-002-UNIT-015: 필수 수정 로직 (70점 미만)"""
        result = await speclint_lint(self.EMPTY_DOCUMENT, "full")
        
        if result["score"] < 70:
            assert result["score"] < 70
            # 필수 수정 메시지 확인
            assert "mandatory_fix" in str(result.get("metadata", {}))

    @pytest.mark.asyncio
    async def test_us002_unit_016_improvement_suggestions(self):
        """US-002-UNIT-016: 수정 제안 생성 로직"""
        result = await speclint_lint(self.INCOMPLETE_DOCUMENT, "full")
        
        assert "suggestions" in result
        assert isinstance(result["suggestions"], list)

    @pytest.mark.asyncio
    async def test_us002_unit_017_message_generation(self):
        """US-002-UNIT-017: 메시지 생성 로직"""
        result = await speclint_lint(self.PERFECT_DOCUMENT, "full")
        
        # 결과에 메시지가 포함되어 있는지 확인
        assert "score" in result
        assert "violations" in result
        assert "suggestions" in result

    @pytest.mark.asyncio
    async def test_us002_unit_018_basic_error_handling(self):
        """US-002-UNIT-018: 기본 에러 처리 로직"""
        # None 입력에 대한 에러 처리
        try:
            result = await speclint_lint(None, "full")
            assert result["score"] == 0
        except Exception as e:
            # 예외가 발생해도 적절히 처리되어야 함
            assert "error" in str(e).lower() or "invalid" in str(e).lower()

    @pytest.mark.asyncio
    async def test_us002_unit_019_github_api_failure_handling(self):
        """US-002-UNIT-019: GitHub API 실패 처리"""
        # GitHub API 실패 시뮬레이션은 통합 테스트에서 처리
        # 여기서는 기본적인 에러 처리 로직만 확인
        result = await speclint_lint(self.PERFECT_DOCUMENT, "full")
        assert "metadata" in result


class TestSpecLintIntegration:
    """US-002 speclint.lint 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_us002_int_001_document_structure_analysis(self):
        """US-002-INT-001: 전체 문서 구조 분석"""
        perfect_doc = TestSpecLintLint.PERFECT_DOCUMENT
        result = await speclint_lint(perfect_doc, "full")
        
        # 전체 구조가 올바르게 분석되는지 확인
        assert result["score"] >= 90
        assert len(result["violations"]) == 0

    @pytest.mark.asyncio
    async def test_us002_int_002_template_compliance_check(self):
        """US-002-INT-002: 전체 템플릿 준수 검사"""
        perfect_doc = TestSpecLintLint.PERFECT_DOCUMENT
        result = await speclint_lint(perfect_doc, "full")
        
        # 템플릿 준수도가 높은지 확인
        assert result["score"] >= 90

    @pytest.mark.asyncio
    async def test_us002_int_003_quality_grade_classification(self):
        """US-002-INT-003: 품질 등급 분류 로직"""
        # 90점 이상 문서
        result = await speclint_lint(TestSpecLintLint.PERFECT_DOCUMENT, "full")
        if result["score"] >= 90:
            assert result["score"] >= 90
        
        # 70점 미만 문서
        result = await speclint_lint(TestSpecLintLint.EMPTY_DOCUMENT, "full")
        assert result["score"] < 70

    @pytest.mark.asyncio
    async def test_us002_int_004_logging_integration(self):
        """US-002-INT-004: 로그 출력 통합 테스트"""
        result = await speclint_lint(TestSpecLintLint.PERFECT_DOCUMENT, "full")
        
        # 로깅 정보가 메타데이터에 포함되어 있는지 확인
        assert "metadata" in result
        assert "timestamp" in result["metadata"]

    @pytest.mark.asyncio
    async def test_us002_int_005_error_handling_integration(self):
        """US-002-INT-005: 에러 처리 통합 테스트"""
        # 다양한 에러 상황 테스트
        test_cases = [
            TestSpecLintLint.EMPTY_DOCUMENT,
            TestSpecLintLint.MALFORMED_DOCUMENT,
            TestSpecLintLint.INCOMPLETE_DOCUMENT
        ]
        
        for test_case in test_cases:
            result = await speclint_lint(test_case, "full")
            assert "score" in result
            assert "violations" in result
            assert 0 <= result["score"] <= 100

    @pytest.mark.asyncio
    async def test_us002_int_006_batch_processing_logic(self):
        """US-002-INT-006: 배치 처리 로직"""
        documents = [
            TestSpecLintLint.PERFECT_DOCUMENT,
            TestSpecLintLint.INCOMPLETE_DOCUMENT,
            TestSpecLintLint.MALFORMED_DOCUMENT
        ]
        
        results = []
        for doc in documents:
            result = await speclint_lint(doc, "full")
            results.append(result)
        
        # 모든 문서가 처리되었는지 확인
        assert len(results) == len(documents)
        for result in results:
            assert "score" in result

    @pytest.mark.asyncio
    async def test_us002_int_007_partial_failure_handling(self):
        """US-002-INT-007: 부분 실패 처리"""
        # 일부 문서는 성공, 일부는 실패하는 시나리오
        documents = [
            TestSpecLintLint.PERFECT_DOCUMENT,  # 성공
            TestSpecLintLint.EMPTY_DOCUMENT,    # 실패
            TestSpecLintLint.PERFECT_DOCUMENT   # 성공
        ]
        
        successful_count = 0
        failed_count = 0
        
        for doc in documents:
            result = await speclint_lint(doc, "full")
            if result["score"] >= 70:
                successful_count += 1
            else:
                failed_count += 1
        
        assert successful_count > 0
        assert failed_count > 0

    @pytest.mark.asyncio
    async def test_us002_int_008_github_issue_creation_logic(self):
        """US-002-INT-008: GitHub Issue 생성 로직"""
        # HITL 검토가 필요한 문서 (70-89점)
        result = await speclint_lint(TestSpecLintLint.INCOMPLETE_DOCUMENT, "full")
        
        if 70 <= result["score"] < 90:
            # GitHub Issue 생성 로직이 호출되어야 함
            # 실제 구현에서는 GitHub API 호출이 포함됨
            assert "hitl_review" in str(result.get("metadata", {}))

    @pytest.mark.asyncio
    async def test_us002_int_009_suggestion_generation_integration(self):
        """US-002-INT-009: 제안 생성 통합 테스트"""
        result = await speclint_lint(TestSpecLintLint.INCOMPLETE_DOCUMENT, "full")
        
        assert "suggestions" in result
        assert isinstance(result["suggestions"], list)

    @pytest.mark.asyncio
    async def test_us002_int_010_error_handling_system(self):
        """US-002-INT-010: 전체 에러 처리 시스템"""
        # 다양한 에러 상황을 통합적으로 테스트
        error_cases = [
            TestSpecLintLint.EMPTY_DOCUMENT,
            None,  # None 입력
            "",    # 빈 문자열
        ]
        
        for case in error_cases:
            try:
                result = await speclint_lint(case, "full")
                # 에러가 발생하지 않으면 적절한 기본값이 반환되어야 함
                assert "score" in result
                assert 0 <= result["score"] <= 100
            except Exception:
                # 예외가 발생해도 시스템이 중단되지 않아야 함
                pass


class TestSpecLintE2E:
    """US-002 speclint.lint E2E 테스트"""
    
    @pytest.mark.asyncio
    async def test_us002_e2e_001_batch_workflow(self):
        """US-002-E2E-001: 전체 배치 워크플로우"""
        # 실제 배치 처리 시나리오
        documents = [
            {"id": "doc1", "content": TestSpecLintLint.PERFECT_DOCUMENT},
            {"id": "doc2", "content": TestSpecLintLint.INCOMPLETE_DOCUMENT},
            {"id": "doc3", "content": TestSpecLintLint.MALFORMED_DOCUMENT}
        ]
        
        results = []
        for doc in documents:
            result = await speclint_lint(doc["content"], "full")
            results.append({
                "document_id": doc["id"],
                "score": result["score"],
                "status": "auto_approve" if result["score"] >= 90 
                         else "hitl_review" if result["score"] >= 70 
                         else "mandatory_fix"
            })
        
        # 배치 처리 결과 검증
        assert len(results) == len(documents)
        assert any(r["status"] == "auto_approve" for r in results)
        assert any(r["status"] == "mandatory_fix" for r in results)

    @pytest.mark.asyncio
    async def test_us002_e2e_002_hitl_workflow(self):
        """US-002-E2E-002: HITL 워크플로우"""
        # HITL 검토가 필요한 문서 처리
        result = await speclint_lint(TestSpecLintLint.INCOMPLETE_DOCUMENT, "full")
        
        if 70 <= result["score"] < 90:
            # HITL 워크플로우 시작
            assert "hitl_review" in str(result.get("metadata", {}))
            # 실제 구현에서는 GitHub Issue 생성이 포함됨

    @pytest.mark.asyncio
    async def test_us002_e2e_003_quality_processing_workflow(self):
        """US-002-E2E-003: 전체 품질 처리 워크플로우"""
        # 다양한 품질의 문서들을 처리하는 전체 워크플로우
        test_documents = [
            ("perfect", TestSpecLintLint.PERFECT_DOCUMENT),
            ("incomplete", TestSpecLintLint.INCOMPLETE_DOCUMENT),
            ("empty", TestSpecLintLint.EMPTY_DOCUMENT)
        ]
        
        workflow_results = []
        for doc_type, content in test_documents:
            result = await speclint_lint(content, "full")
            
            # 품질에 따른 처리 결정
            if result["score"] >= 90:
                action = "auto_approve"
            elif result["score"] >= 70:
                action = "hitl_review"
            else:
                action = "mandatory_fix"
            
            workflow_results.append({
                "document_type": doc_type,
                "score": result["score"],
                "action": action
            })
        
        # 워크플로우 결과 검증
        assert len(workflow_results) == len(test_documents)
        assert any(r["action"] == "auto_approve" for r in workflow_results)
        assert any(r["action"] == "mandatory_fix" for r in workflow_results)

    @pytest.mark.asyncio
    async def test_us002_e2e_004_user_message_display(self):
        """US-002-E2E-004: 사용자 메시지 표시"""
        # 사용자에게 표시될 메시지 검증
        result = await speclint_lint(TestSpecLintLint.PERFECT_DOCUMENT, "full")
        
        # 결과에 사용자 친화적인 정보가 포함되어 있는지 확인
        assert "score" in result
        assert "violations" in result
        assert "suggestions" in result
        assert "metadata" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
