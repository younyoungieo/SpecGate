# US-000: MCP Server 기본 구조 설계 문서

## 1. 기능 개요

### 1.1 목적
SpecGate MCP Server의 기본 구조를 FastMCP 2.0 표준에 맞게 구축하여 Phase 1의 MCP 도구들을 구현할 수 있는 기반을 마련한다.

### 1.2 핵심 기능
- FastMCP 2.0 프레임워크 기반 서버 구축
- Context 기반 도구 구현 (로깅, 진행상황 보고, 사용자 상호작용)
- 미들웨어 아키텍처 (로깅, 에러처리, 인증)
- fastmcp.json 기반 설정 관리
- 서버 시작/종료 및 배포 관리

## 2. FastMCP 2.0 서버 구조

### 2.1 서버 구성
```python
from fastmcp import FastMCP, Context
from fastmcp.server.middleware.logging import StructuredLoggingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware

# FastMCP 2.0 서버 인스턴스 생성
mcp = FastMCP(
    name="specgate-server",
    description="SpecGate MCP Server for Phase 1"
)

# 미들웨어 추가
mcp.add_middleware(StructuredLoggingMiddleware())
mcp.add_middleware(ErrorHandlingMiddleware())
```

### 2.2 FastMCP 2.0 도구 구조
```python
# FastMCP 2.0 도구 정의 패턴
@mcp.tool
async def confluence_fetch(
    label: str, 
    space_key: str | None = None, 
    limit: int = 10,
    ctx: Context
) -> dict:
    """Confluence 문서 수집 및 HTML→MD 변환
    
    Args:
        label: 검색할 라벨
        space_key: Confluence 스페이스 키 (선택사항)
        limit: 최대 결과 수 (기본값: 10)
        ctx: FastMCP Context (로깅, 진행상황 보고용)
    
    Returns:
        dict: 수집된 문서 정보
    """
    # Context를 통한 로깅 및 진행상황 보고
    await ctx.info(f"Confluence 문서 수집 시작: {label}")
    await ctx.report_progress(0, 100, "문서 검색 중...")
    
    try:
        # 구현 로직
        result = {"status": "success", "documents": []}
        await ctx.report_progress(100, 100, "수집 완료")
        return result
    except Exception as e:
        await ctx.error(f"문서 수집 실패: {str(e)}")
        raise
```

## 3. FastMCP 2.0 도구별 구현 구조

### 3.1 confluence.fetch 도구
```python
@mcp.tool(
    name="confluence.fetch",
    description="Confluence 문서 수집 및 HTML→MD 변환",
    tags={"confluence", "document", "phase1"}
)
async def confluence_fetch(
    label: str, 
    space_key: str | None = None, 
    limit: int = 10,
    ctx: Context
) -> dict:
    """Confluence에서 라벨 기준으로 문서를 수집하고 HTML을 Markdown으로 변환
    
    Args:
        label: 검색할 라벨 (필수)
        space_key: Confluence 스페이스 키 (선택사항)
        limit: 최대 결과 수 (기본값: 10)
        ctx: FastMCP Context
    
    Returns:
        dict: {
            "status": str,
            "documents": List[dict],
            "metadata": dict
        }
    """
    await ctx.info(f"Confluence 문서 수집 시작 - 라벨: {label}")
    await ctx.report_progress(0, 100, "Confluence API 연결 중...")
    
    try:
        # 1단계: Confluence API 호출
        await ctx.report_progress(20, 100, "문서 검색 중...")
        documents = await _search_confluence_documents(label, space_key, limit)
        
        # 2단계: HTML→MD 변환
        await ctx.report_progress(60, 100, "HTML→Markdown 변환 중...")
        converted_docs = await _convert_html_to_markdown(documents)
        
        # 3단계: 메타데이터 생성
        await ctx.report_progress(90, 100, "메타데이터 생성 중...")
        metadata = {
            "total_count": len(converted_docs),
            "search_label": label,
            "space_key": space_key,
            "timestamp": datetime.now().isoformat()
        }
        
        result = {
            "status": "success",
            "documents": converted_docs,
            "metadata": metadata
        }
        
        await ctx.report_progress(100, 100, "수집 완료")
        await ctx.info(f"총 {len(converted_docs)}개 문서 수집 완료")
        return result
        
    except Exception as e:
        await ctx.error(f"Confluence 문서 수집 실패: {str(e)}")
        raise ToolError(f"문서 수집 중 오류 발생: {str(e)}")

# 내부 헬퍼 함수들
async def _search_confluence_documents(label: str, space_key: str | None, limit: int) -> list:
    """Confluence API를 통해 문서 검색"""
    # 구현 예정
    pass

async def _convert_html_to_markdown(documents: list) -> list:
    """HTML 문서를 Markdown으로 변환"""
    # 구현 예정
    pass
```

### 3.2 speclint.lint 도구
```python
@mcp.tool(
    name="speclint.lint",
    description="문서 품질 검사 및 점수 계산",
    tags={"quality", "linting", "phase1"}
)
async def speclint_lint(
    content: str,
    check_type: str = "full",
    ctx: Context
) -> dict:
    """문서의 표준 템플릿 준수 여부를 검사하고 품질 점수를 계산
    
    Args:
        content: 검사할 문서 내용 (필수)
        check_type: 검사 유형 ("full", "basic", "structure") (기본값: "full")
        ctx: FastMCP Context
    
    Returns:
        dict: {
            "score": int,  # 0-100 점수
            "violations": List[dict],
            "suggestions": List[str],
            "metadata": dict
        }
    """
    await ctx.info(f"문서 품질 검사 시작 - 검사 유형: {check_type}")
    await ctx.report_progress(0, 100, "문서 분석 중...")
    
    try:
        # 1단계: 문서 구조 분석
        await ctx.report_progress(20, 100, "문서 구조 분석 중...")
        structure_analysis = await _analyze_document_structure(content)
        
        # 2단계: 템플릿 준수 검사
        await ctx.report_progress(50, 100, "템플릿 준수 검사 중...")
        template_violations = await _check_template_compliance(content, check_type)
        
        # 3단계: 품질 점수 계산
        await ctx.report_progress(80, 100, "품질 점수 계산 중...")
        quality_score = await _calculate_quality_score(structure_analysis, template_violations)
        
        # 4단계: 개선 제안 생성
        await ctx.report_progress(95, 100, "개선 제안 생성 중...")
        suggestions = await _generate_improvement_suggestions(template_violations)
        
        result = {
            "score": quality_score,
            "violations": template_violations,
            "suggestions": suggestions,
            "metadata": {
                "check_type": check_type,
                "content_length": len(content),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        await ctx.report_progress(100, 100, "검사 완료")
        await ctx.info(f"품질 검사 완료 - 점수: {quality_score}/100")
        return result
        
    except Exception as e:
        await ctx.error(f"품질 검사 실패: {str(e)}")
        raise ToolError(f"품질 검사 중 오류 발생: {str(e)}")

# 내부 헬퍼 함수들
async def _analyze_document_structure(content: str) -> dict:
    """문서 구조 분석"""
    # 구현 예정
    pass

async def _check_template_compliance(content: str, check_type: str) -> list:
    """템플릿 준수 검사"""
    # 구현 예정
    pass

async def _calculate_quality_score(structure: dict, violations: list) -> int:
    """품질 점수 계산 (0-100)"""
    # 구현 예정
    pass

async def _generate_improvement_suggestions(violations: list) -> list:
    """개선 제안 생성"""
    # 구현 예정
    pass
```

### 3.3 html.to_md 도구
```python
@mcp.tool(
    name="html.to_md",
    description="HTML을 Markdown으로 변환",
    tags={"conversion", "html", "markdown", "phase1"}
)
async def html_to_md(
    html_content: str,
    preserve_structure: bool = True,
    ctx: Context
) -> dict:
    """HTML 내용을 Markdown 형식으로 변환
    
    Args:
        html_content: 변환할 HTML 내용 (필수)
        preserve_structure: 구조 보존 여부 (기본값: True)
        ctx: FastMCP Context
    
    Returns:
        dict: {
            "markdown": str,
            "metadata": dict,
            "conversion_info": dict
        }
    """
    await ctx.info(f"HTML→Markdown 변환 시작 - 구조보존: {preserve_structure}")
    await ctx.report_progress(0, 100, "HTML 파싱 중...")
    
    try:
        # 1단계: HTML 파싱 및 구조 분석
        await ctx.report_progress(20, 100, "HTML 구조 분석 중...")
        parsed_html = await _parse_html_structure(html_content)
        
        # 2단계: Markdown 변환
        await ctx.report_progress(60, 100, "Markdown 변환 중...")
        markdown_content = await _convert_to_markdown(parsed_html, preserve_structure)
        
        # 3단계: 변환 정보 수집
        await ctx.report_progress(90, 100, "변환 정보 수집 중...")
        conversion_info = {
            "original_length": len(html_content),
            "converted_length": len(markdown_content),
            "compression_ratio": len(markdown_content) / len(html_content),
            "structure_preserved": preserve_structure,
            "elements_converted": await _count_converted_elements(parsed_html)
        }
        
        result = {
            "markdown": markdown_content,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "preserve_structure": preserve_structure
            },
            "conversion_info": conversion_info
        }
        
        await ctx.report_progress(100, 100, "변환 완료")
        await ctx.info(f"HTML→Markdown 변환 완료 - 압축률: {conversion_info['compression_ratio']:.2%}")
        return result
        
    except Exception as e:
        await ctx.error(f"HTML→Markdown 변환 실패: {str(e)}")
        raise ToolError(f"변환 중 오류 발생: {str(e)}")

# 내부 헬퍼 함수들
async def _parse_html_structure(html_content: str) -> dict:
    """HTML 구조 파싱"""
    # 구현 예정
    pass

async def _convert_to_markdown(parsed_html: dict, preserve_structure: bool) -> str:
    """HTML을 Markdown으로 변환"""
    # 구현 예정
    pass

async def _count_converted_elements(parsed_html: dict) -> dict:
    """변환된 요소 수 계산"""
    # 구현 예정
    pass
```

## 4. FastMCP 2.0 서버 관리

### 4.1 서버 시작 및 실행
```python
# main.py 또는 server.py
import asyncio
from fastmcp import FastMCP, Context
from fastmcp.server.middleware.logging import StructuredLoggingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from datetime import datetime

# FastMCP 서버 인스턴스 생성
mcp = FastMCP(
    name="specgate-server",
    description="SpecGate MCP Server for Phase 1 - Confluence 문서 처리"
)

# 미들웨어 등록
mcp.add_middleware(StructuredLoggingMiddleware())
mcp.add_middleware(ErrorHandlingMiddleware())

# 도구들 정의 (위에서 정의한 도구들)
# @mcp.tool 데코레이터로 자동 등록됨

if __name__ == "__main__":
    # 개발 환경에서 STDIO로 실행
    mcp.run()
    
    # 또는 HTTP 서버로 실행
    # mcp.run(transport="http", host="0.0.0.0", port=8000)
    
    # 또는 SSE로 실행
    # mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

### 4.2 fastmcp.json 설정 파일
```json
{
  "$schema": "https://gofastmcp.com/public/schemas/fastmcp.json/v1.json",
  "source": {
    "path": "server.py",
    "entrypoint": "mcp"
  },
  "environment": {
    "python": "3.11",
    "env": {
      "CONFLUENCE_API_KEY": "required",
      "CONFLUENCE_BASE_URL": "required",
      "CONFLUENCE_USERNAME": "optional",
      "LOG_LEVEL": "INFO"
    }
  },
  "deployment": {
    "transport": "http",
    "port": 8000,
    "host": "0.0.0.0"
  }
}
```

### 4.3 서버 생명주기 관리
```python
# 서버 시작 시 초기화
@mcp.server_startup
async def initialize_server():
    """서버 시작 시 초기화 작업"""
    print("🚀 SpecGate MCP Server 시작")
    print("📋 등록된 도구들:")
    tools = await mcp.list_tools()
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")

# 서버 종료 시 정리
@mcp.server_shutdown
async def cleanup_server():
    """서버 종료 시 정리 작업"""
    print("🛑 SpecGate MCP Server 종료")
    # 필요한 정리 작업 수행
```

## 5. FastMCP 2.0 도구 간 데이터 전달

### 5.1 표준화된 데이터 구조
```python
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class DocumentData:
    """문서 데이터 표준 구조"""
    id: str
    title: str
    content: str
    html_content: Optional[str] = None
    markdown_content: Optional[str] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class ProcessingResult:
    """처리 결과 표준 구조"""
    status: str  # "success", "error", "warning"
    data: Any
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

@dataclass
class QualityScore:
    """품질 점수 표준 구조"""
    total_score: int  # 0-100
    category_scores: Dict[str, int]
    violations: List[Dict[str, Any]]
    suggestions: List[str]
    metadata: Dict[str, Any]
```

### 5.2 FastMCP 2.0 파이프라인 구조
```python
# 통합 파이프라인 도구
@mcp.tool(
    name="specgate.pipeline",
    description="Confluence 문서 수집부터 품질 검사까지 전체 파이프라인 실행",
    tags={"pipeline", "integration", "phase1"}
)
async def run_specgate_pipeline(
    label: str,
    space_key: str | None = None,
    limit: int = 10,
    check_type: str = "full",
    ctx: Context
) -> dict:
    """전체 SpecGate 파이프라인 실행
    
    Args:
        label: Confluence 검색 라벨
        space_key: Confluence 스페이스 키
        limit: 최대 문서 수
        check_type: 품질 검사 유형
        ctx: FastMCP Context
    
    Returns:
        dict: 전체 파이프라인 실행 결과
    """
    await ctx.info("🚀 SpecGate 파이프라인 시작")
    
    pipeline_results = {
        "status": "success",
        "stages": {},
        "final_result": None,
        "metadata": {
            "started_at": datetime.now().isoformat(),
            "total_documents": 0,
            "average_quality_score": 0
        }
    }
    
    try:
        # 1단계: Confluence 문서 수집
        await ctx.report_progress(0, 100, "1단계: Confluence 문서 수집")
        confluence_result = await confluence_fetch(label, space_key, limit, ctx)
        pipeline_results["stages"]["confluence_fetch"] = confluence_result
        
        documents = confluence_result.get("documents", [])
        pipeline_results["metadata"]["total_documents"] = len(documents)
        
        if not documents:
            await ctx.warning("수집된 문서가 없습니다.")
            pipeline_results["status"] = "warning"
            return pipeline_results
        
        # 2단계: HTML→Markdown 변환
        await ctx.report_progress(30, 100, "2단계: HTML→Markdown 변환")
        converted_documents = []
        
        for i, doc in enumerate(documents):
            await ctx.report_progress(
                30 + (i / len(documents)) * 40, 
                100, 
                f"문서 {i+1}/{len(documents)} 변환 중"
            )
            
            if doc.get("html_content"):
                html_result = await html_to_md(doc["html_content"], True, ctx)
                doc["markdown_content"] = html_result["markdown"]
                doc["conversion_info"] = html_result["conversion_info"]
                
            converted_documents.append(doc)
        
        pipeline_results["stages"]["html_to_md"] = {
            "converted_count": len(converted_documents),
            "documents": converted_documents
        }
        
        # 3단계: 품질 검사
        await ctx.report_progress(70, 100, "3단계: 품질 검사")
        quality_scores = []
        
        for i, doc in enumerate(converted_documents):
            await ctx.report_progress(
                70 + (i / len(converted_documents)) * 25, 
                100, 
                f"문서 {i+1}/{len(converted_documents)} 품질 검사 중"
            )
            
            content = doc.get("markdown_content", doc.get("content", ""))
            if content:
                quality_result = await speclint_lint(content, check_type, ctx)
                doc["quality_score"] = quality_result["score"]
                doc["quality_violations"] = quality_result["violations"]
                doc["quality_suggestions"] = quality_result["suggestions"]
                quality_scores.append(quality_result["score"])
        
        # 최종 결과 계산
        avg_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        pipeline_results["metadata"]["average_quality_score"] = round(avg_score, 2)
        
        pipeline_results["stages"]["speclint"] = {
            "checked_count": len(quality_scores),
            "average_score": avg_score,
            "scores": quality_scores
        }
        
        # 최종 결과 정리
        pipeline_results["final_result"] = {
            "documents": converted_documents,
            "summary": {
                "total_documents": len(converted_documents),
                "average_quality_score": avg_score,
                "high_quality_docs": len([s for s in quality_scores if s >= 80]),
                "needs_improvement": len([s for s in quality_scores if s < 60])
            }
        }
        
        await ctx.report_progress(100, 100, "파이프라인 완료")
        await ctx.info(f"✅ 파이프라인 완료 - 평균 품질 점수: {avg_score:.1f}/100")
        
        pipeline_results["metadata"]["completed_at"] = datetime.now().isoformat()
        return pipeline_results
        
    except Exception as e:
        await ctx.error(f"파이프라인 실행 실패: {str(e)}")
        pipeline_results["status"] = "error"
        pipeline_results["error_message"] = str(e)
        raise ToolError(f"파이프라인 실행 중 오류: {str(e)}")
```

## 6. FastMCP 2.0 에러 처리 및 미들웨어

### 6.1 에러 처리 미들웨어
```python
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp import ToolError

# 자동 에러 처리 미들웨어
mcp.add_middleware(ErrorHandlingMiddleware())

# 커스텀 에러 처리
@mcp.tool_error_handler
def handle_tool_error(error: Exception, tool_name: str, ctx: Context) -> dict:
    """도구별 커스텀 에러 처리"""
    await ctx.error(f"도구 '{tool_name}' 실행 중 오류: {str(error)}")
    
    if isinstance(error, ToolError):
        return {
            "status": "error",
            "error_type": "tool_error",
            "message": str(error),
            "tool": tool_name
        }
    else:
        return {
            "status": "error", 
            "error_type": "system_error",
            "message": "시스템 오류가 발생했습니다.",
            "tool": tool_name
        }
```

### 6.2 로깅 미들웨어
```python
from fastmcp.server.middleware.logging import StructuredLoggingMiddleware
import logging

# 구조화된 로깅 미들웨어
mcp.add_middleware(StructuredLoggingMiddleware())

# 커스텀 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('specgate.log'),
        logging.StreamHandler()
    ]
)
```

### 6.3 인증 미들웨어 (향후 확장용)
```python
# 향후 Confluence API 인증을 위한 미들웨어
from fastmcp.server.middleware import Middleware
from fastmcp.server.dependencies import get_http_headers

class ConfluenceAuthMiddleware(Middleware):
    """Confluence API 인증 미들웨어"""
    
    async def on_call_tool(self, context, call_next):
        # Confluence 관련 도구 호출 시 API 키 검증
        if context.message.name.startswith('confluence.'):
            headers = get_http_headers()
            api_key = headers.get('X-Confluence-API-Key')
            
            if not api_key:
                raise ToolError("Confluence API 키가 필요합니다.")
        
        return await call_next(context)

# 미들웨어 등록 (필요시)
# mcp.add_middleware(ConfluenceAuthMiddleware())
```

## 7. 구현 우선순위 및 마일스톤

### 7.1 1단계 (핵심 기능) - Sprint 1
- ✅ FastMCP 2.0 서버 기본 구조 구축
- ✅ 기본 도구 3개 구현 (confluence.fetch, speclint.lint, html.to_md)
- ✅ Context 기반 로깅 및 진행상황 보고
- ✅ fastmcp.json 설정 파일 구성
- ✅ 기본 에러 처리 미들웨어

### 7.2 2단계 (고도화) - Sprint 2
- 🔄 도구 간 데이터 전달 표준화
- 🔄 통합 파이프라인 도구 구현
- 🔄 구조화된 로깅 시스템
- 🔄 상세한 에러 처리 및 복구 로직
- 🔄 단위 테스트 및 통합 테스트

### 7.3 3단계 (확장) - Sprint 3+
- 📋 인증 미들웨어 구현
- 📋 성능 모니터링 및 메트릭 수집
- 📋 캐싱 시스템 구현
- 📋 배포 자동화 (Docker, Azure)
- 📋 API 문서 자동 생성

### 7.4 배포 및 운영
- 📋 Azure Container Instances 배포
- 📋 헬스체크 및 모니터링
- 📋 로그 수집 및 분석
- 📋 백업 및 복구 전략

## 8. 개발 환경 설정

### 8.1 의존성 관리 (pyproject.toml)
```toml
[project]
name = "specgate-mcp-server"
version = "1.0.0"
description = "SpecGate MCP Server for Phase 1"
dependencies = [
    "fastmcp>=2.0.0",
    "httpx>=0.25.0",
    "beautifulsoup4>=4.12.0",
    "markdownify>=0.11.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 8.2 환경 변수 설정 (.env)
```env
# Confluence 설정
CONFLUENCE_API_KEY=your_api_key_here
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your_username

# 로깅 설정
LOG_LEVEL=INFO
LOG_FILE=specgate.log

# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_TRANSPORT=http
```

### 8.3 개발 명령어
```bash
# 개발 환경 설정
uv venv
uv pip install -e .

# 서버 실행 (STDIO)
fastmcp run server.py

# 서버 실행 (HTTP)
fastmcp run server.py --transport http --port 8000

# 테스트 실행
pytest tests/

# 코드 포맷팅
black .
ruff check --fix .
```
