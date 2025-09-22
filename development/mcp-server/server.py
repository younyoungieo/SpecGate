"""
SpecGate MCP Server - Phase 1 Implementation
FastMCP 2.12 기반 서버 구조
"""
import asyncio
import logging
import httpx
import os
import subprocess
import json
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from fastmcp import FastMCP

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("SpecGate Server 🚀")

# 클라이언트 작업 디렉토리 저장용
client_work_dir = None

# 초기 로깅은 콘솔로만 설정. 실제 파일 경로는 클라이언트 디렉토리 감지 후 재설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# 표준화된 데이터 구조
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


# =============================================================================
# 1. confluence.fetch 도구 구현 (리팩토링된 모듈 사용)
# =============================================================================
from confluence import ConfluenceService

# Confluence 서비스 인스턴스 생성
confluence_service = ConfluenceService()

@mcp.tool()
async def confluence_fetch(
    label: str, 
    space_key: str | None = None, 
    limit: int = 10,
    save_html: bool = True,
    output_dir: str | None = None,
    auto_pipeline: bool = True
) -> dict:
    """Confluence에서 라벨 기준으로 문서를 수집하고 HTML 원본을 저장
    
    Args:
        label: 검색할 라벨 (필수)
        space_key: Confluence 스페이스 키 (선택사항)
        limit: 최대 결과 수 (기본값: 10)
        save_html: HTML 원본 저장 여부 (기본값: True)
        output_dir: HTML 파일 저장 디렉토리 (기본값: None, 자동 감지)
    
    Returns:
        dict: {
            "status": str,
            "documents": List[dict],
            "metadata": dict (html_files 포함)
        }
    """
    # output_dir이 지정되지 않으면 자동으로 클라이언트 작업 디렉토리 사용
    if output_dir is None:
        output_dir = _get_client_work_dir()
    # 클라이언트 작업 디렉토리 고정 및 로그 경로 재설정
    try:
        import os as _os
        _od = _os.path.normpath(output_dir)
        marker = _os.path.join("SpecGate", "data")
        if marker in _od:
            head = _od.split(marker)[0]
            client_root = head.rstrip(_os.sep)
        else:
            client_root = _od
        _set_client_work_dir(client_root)
    except Exception:
        pass
    
    fetch_result = await confluence_service.fetch_documents(label, space_key, limit, save_html, output_dir)

    # 자동 파이프라인: HTML → MD → Lint
    if auto_pipeline and fetch_result.get("status") == "success":
        try:
            import os as _os
            documents = fetch_result.get("documents", [])
            html_files = fetch_result.get("metadata", {}).get("html_files", [])
            md_results = []
            for idx, doc in enumerate(documents):
                html_content = doc.get("html_content")
                if not html_content:
                    continue
                filename_base = None
                if idx < len(html_files):
                    filename_base = _os.path.basename(html_files[idx])
                md_conv = await html_to_md(
                    html_content=html_content,
                    preserve_structure=True,
                    save_to_file=True,
                    output_path=None,
                    output_dir=output_dir,
                    filename_base=filename_base
                )
                markdown_text = md_conv.get("markdown")
                lint_result = await speclint_lint(markdown_text, "full", save_report=True, output_dir=output_dir) if markdown_text else {"score": 0}
                md_results.append({
                    "title": doc.get("title"),
                    "html_file": html_files[idx] if idx < len(html_files) else None,
                    "markdown_file": md_conv.get("conversion_info", {}).get("file_path"),
                    "lint": lint_result
                })
            fetch_result["metadata"]["pipeline_results"] = md_results
        except Exception as e:
            logging.getLogger("specgate.pipeline").warning(f"자동 파이프라인 처리 중 경고: {e}")
    
    return fetch_result


# =============================================================================
# 2. speclint.lint 도구 구현 (리팩토링된 모듈 사용)
# =============================================================================
from speclint import SpecLint

# SpecLint 인스턴스 생성
speclint_engine = SpecLint()

@mcp.tool()
async def speclint_lint(
    content: str,
    check_type: str = "full",
    save_report: bool = True,
    output_dir: str = None
) -> dict:
    """문서의 표준 템플릿 준수 여부를 검사하고 품질 점수를 계산
    
    Args:
        content: 검사할 문서 내용 (필수)
        check_type: 검사 유형 ("full", "basic", "structure") (기본값: "full")
        save_report: 품질 리포트 파일 저장 여부 (기본값: True)
        output_dir: 저장할 디렉토리 (기본값: None, 자동 감지)
    
    Returns:
        dict: {
            "score": int,  # 0-100 점수
            "violations": List[dict],
            "suggestions": List[str],
            "metadata": dict
        }
    """
    result = await speclint_engine.lint(content, check_type)
    
    # 품질 리포트 저장
    if save_report:
        try:
            import os
            import json
            from datetime import datetime
            
            # 출력 디렉토리 결정 (quality_reports/)
            if output_dir:
                _od = os.path.normpath(output_dir)
                marker = os.path.join("SpecGate", "data")
                if marker in _od:
                    # SpecGate/data 이후의 하위 폴더는 제거하고 'quality_reports'로 고정
                    marker_idx = _od.find(marker)
                    before_specgate = _od[:marker_idx]
                    reports_dir = os.path.join(before_specgate, marker, "quality_reports")
                else:
                    # 프로젝트 루트로 간주하여 SpecGate/data/quality_reports 하위로 저장
                    reports_dir = os.path.join(output_dir, "SpecGate", "data", "quality_reports")
            else:
                # 자동으로 클라이언트 작업 디렉토리 사용
                client_dir = _get_client_work_dir()
                reports_dir = os.path.join(client_dir, "SpecGate", "data", "quality_reports")
            
            os.makedirs(reports_dir, exist_ok=True)
            
            # 클라이언트 루트 경로 업데이트
            try:
                specgate_dir = os.path.dirname(os.path.dirname(reports_dir))  # {client}/SpecGate
                client_root = os.path.dirname(specgate_dir)                   # {client}
                _set_client_work_dir(client_root)
            except Exception:
                pass
            
            # 리포트 파일명 생성 (타임스탬프 포함)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            score = result.get("score", 0)
            quality_level = result.get("metadata", {}).get("quality_level", "unknown")
            report_filename = f"quality_report_{score}pts_{quality_level}_{timestamp}.json"
            report_path = os.path.join(reports_dir, report_filename)
            
            # 리포트 데이터 준비
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "quality_score": result.get("score", 0),
                "quality_level": quality_level,
                "check_type": check_type,
                "violations": result.get("violations", []),
                "suggestions": result.get("suggestions", []),
                "metadata": result.get("metadata", {}),
                "content_length": len(content) if content else 0
            }
            
            # JSON 파일로 저장
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            # 결과에 저장 정보 추가
            result["metadata"]["report_saved"] = True
            result["metadata"]["report_path"] = report_path
            
            logging.getLogger("specgate.speclint").info(f"품질 리포트 저장 완료: {report_path}")
            
        except Exception as e:
            logging.getLogger("specgate.speclint").warning(f"품질 리포트 저장 실패: {e}")
            result["metadata"]["report_saved"] = False
            result["metadata"]["report_error"] = str(e)
    
    return result


# =============================================================================
# 3. html.to_md 도구 구현 (리팩토링된 모듈 사용)
# =============================================================================
from htmlconverter import HTMLToMarkdownConverter

# HTML→MD 변환기 인스턴스 생성
html_converter = HTMLToMarkdownConverter()

@mcp.tool()
async def html_to_md(
    html_content: str,
    preserve_structure: bool = True,
    save_to_file: bool = True,
    output_path: str = None,
    output_dir: str = None,
    filename_base: str | None = None
) -> dict:
    """HTML 내용을 Markdown 형식으로 변환
    
    Args:
        html_content: 변환할 HTML 내용 (필수)
        preserve_structure: 구조 보존 여부 (기본값: True)
        save_to_file: 파일로 저장 여부 (기본값: True)
        output_path: 저장할 파일 경로 (기본값: None, 자동 생성)
        output_dir: 저장할 디렉토리 (기본값: None, 자동 감지)
        filename_base: HTML 파일명 기반으로 MD 파일명을 지정할 때 사용 (확장자 제외 가능)
    
    Returns:
        dict: {
            "markdown": str,
            "metadata": dict,
            "conversion_info": dict
        }
    """
    # 출력 경로 기본값 결정
    if save_to_file and not output_path:
        import os
        from datetime import datetime
        
        # 출력 디렉토리 결정 (최종 저장 디렉토리는 항상 SpecGate/data/md_files)
        if output_dir:
            _od = os.path.normpath(output_dir)
            marker = os.path.join("SpecGate", "data")
            if marker in _od:
                # SpecGate/data 이후의 하위 폴더는 제거하고 'md_files'로 고정
                # /Users/.../SpecGate_test/SpecGate/data -> /Users/.../SpecGate_test/SpecGate/data/md_files
                marker_idx = _od.find(marker)
                before_specgate = _od[:marker_idx]
                base_dir = os.path.join(before_specgate, marker, "md_files")
            else:
                # 프로젝트 루트로 간주하여 SpecGate/data/md_files 하위로 저장
                base_dir = os.path.join(output_dir, "SpecGate", "data", "md_files")
        else:
            # 자동으로 클라이언트 작업 디렉토리 사용
            client_dir = _get_client_work_dir()
            base_dir = os.path.join(client_dir, "SpecGate", "data", "md_files")
        
        os.makedirs(base_dir, exist_ok=True)
        # base_dir 기준으로 클라이언트 루트 추출하여 로깅 경로 고정
        try:
            import os as _os
            # base_dir = {client}/SpecGate/data/md_files
            specgate_dir = _os.path.dirname(_os.path.dirname(base_dir))  # {client}/SpecGate
            client_root = _os.path.dirname(specgate_dir)                 # {client}
            _set_client_work_dir(client_root)
        except Exception:
            pass
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        import re, glob
        if filename_base:
            import os as _os
            base_no_ext = _os.path.splitext(filename_base)[0]
            safe_title = re.sub(r'[^\w\- ]+', '', base_no_ext).strip().replace(' ', '_')[:80] or "converted"
            # HTML 파일명에 타임스탬프가 포함되어 있는지 확인
            ts_match = re.search(r"_(\d{8}_\d{6})$", safe_title)
            final_name = None
            if ts_match:
                final_name = f"{safe_title}.md"
            else:
                # html_files에서 동일 제목의 최신 타임스탬프를 찾아서 사용
                try:
                    client_dir = _get_client_work_dir()
                    html_dir = os.path.join(client_dir, "SpecGate", "data", "html_files")
                    candidates = []
                    for p in glob.glob(os.path.join(html_dir, f"{safe_title}_*.html")):
                        bn = os.path.basename(p)
                        m = re.match(rf"^{re.escape(safe_title)}_(\d{{8}}_\d{{6}})\.html$", bn)
                        if m:
                            candidates.append(m.group(1))
                    if candidates:
                        latest_ts = sorted(candidates)[-1]
                        final_name = f"{safe_title}_{latest_ts}.md"
                except Exception:
                    pass
            if not final_name:
                final_name = f"{safe_title}.md"
            output_path = os.path.join(base_dir, final_name)
        else:
            # HTML에서 제목 추출하여 파일명에 반영
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content or "", 'html.parser')
                title_tag = soup.find(['h1','h2','h3','h4','h5','h6']) or soup.find('title')
                raw_title = title_tag.get_text().strip() if title_tag else "converted"
            except Exception:
                raw_title = "converted"
            safe_title = re.sub(r'[^\w\- ]+', '', raw_title).strip().replace(' ', '_')[:80] or "converted"
            import re as _re
            ts_regex_md = _re.compile(rf"^{_re.escape(safe_title)}_\d{{8}}_\d{{6}}\.md$")
            for old_md in glob.glob(os.path.join(base_dir, f"{safe_title}_*.md")):
                base_md = os.path.basename(old_md)
                if not ts_regex_md.match(base_md):
                    continue
                try:
                    os.remove(old_md)
                    logging.getLogger("specgate.html_to_md").info(f"기존 MD 파일 삭제(중복 처리): {old_md}")
                except Exception as _e:
                    logging.getLogger("specgate.html_to_md").warning(f"기존 MD 파일 삭제 실패: {old_md} ({_e})")
            output_path = os.path.join(base_dir, f"{safe_title}_{timestamp}.md")

    return await html_converter.convert(html_content, preserve_structure, save_to_file, output_path)


# =============================================================================
# 서버 생명주기 관리
# =============================================================================
def _get_client_work_dir():
    """클라이언트 작업 디렉토리를 자동으로 감지"""
    import os
    # 우선순위: 명시 설정(_set_client_work_dir) → 환경변수 → 현재 프로세스 CWD 기준 추정
    global client_work_dir
    if client_work_dir and os.path.exists(client_work_dir):
        return client_work_dir

    env_dir = os.environ.get('CLIENT_WORK_DIR')
    if env_dir and os.path.exists(env_dir):
        client_work_dir = env_dir
        return client_work_dir

    # Cursor에서 MCP 클라이언트 프로젝트 루트는 사용자가 열어둔 워크스페이스 CWD일 가능성이 큼
    current_dir = os.getcwd()
    client_work_dir = current_dir
    return client_work_dir

def initialize_server():
    """서버 시작 시 초기화 작업"""
    print("🚀 SpecGate MCP Server 시작")
    print("📋 등록된 도구들:")
    print("  - confluence_fetch: Confluence 문서 수집 및 HTML 원본 저장")
    print("  - speclint_lint: 문서 품질 검사 및 점수 계산")
    print("  - html_to_md: HTML을 Markdown으로 변환")
    print("🗂️ 워크플로우 디렉토리:")
    print("  - html_files/: HTML 원본 저장")
    print("  - markdown_files/: 변환된 Markdown 저장")
    print("  - quality_reports/: 품질 검사 결과 저장")
    
    # 클라이언트 작업 디렉토리 자동 감지
    client_dir = _get_client_work_dir()
    print(f"📁 자동 감지된 클라이언트 작업 디렉토리: {client_dir}")

    # 파일 로거 재설정: SpecGate/logs/specgate.log
    try:
        specgate_root = os.path.join(client_dir, 'SpecGate')
        logs_dir = os.path.join(specgate_root, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        log_file_path = os.path.join(logs_dir, 'specgate.log')

        root_logger = logging.getLogger()
        # 기존 FileHandler 제거
        for h in list(root_logger.handlers):
            if isinstance(h, logging.FileHandler):
                root_logger.removeHandler(h)
        # 새로운 FileHandler 추가
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        root_logger.addHandler(file_handler)
        logging.getLogger('specgate').info(f"로그 파일 경로 설정: {log_file_path}")
    except Exception as e:
        logging.getLogger('specgate').warning(f"로그 파일 경로 설정 실패: {e}")

def _set_client_work_dir(new_dir: str):
    """세션 중에 클라이언트 작업 디렉토리를 명시적으로 설정하고 로깅 경로를 재설정한다."""
    import os as _os
    global client_work_dir
    if not new_dir:
        return
    # SpecGate/data 하위 경로가 넘어오면 프로젝트 루트로 승격
    marker = _os.path.join("SpecGate", "data")
    nd = _os.path.normpath(new_dir)
    if marker in nd:
        head = nd.split(marker)[0]
        nd = head.rstrip(_os.sep)
    client_work_dir = nd
    # 환경변수에도 주입하여 하위 모듈이 참조 가능하도록
    os.environ['CLIENT_WORK_DIR'] = client_work_dir

    # 로깅 파일 핸들러 재설정
    try:
        specgate_root = _os.path.join(client_work_dir, 'SpecGate')
        logs_dir = _os.path.join(specgate_root, 'logs')
        _os.makedirs(logs_dir, exist_ok=True)
        log_file_path = _os.path.join(logs_dir, 'specgate.log')
        root_logger = logging.getLogger()
        for h in list(root_logger.handlers):
            if isinstance(h, logging.FileHandler):
                root_logger.removeHandler(h)
        fh = logging.FileHandler(log_file_path)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        root_logger.addHandler(fh)
        logging.getLogger('specgate').info(f"로그 파일 경로 설정: {log_file_path}")
    except Exception as e:
        logging.getLogger('specgate').warning(f"로그 파일 경로 재설정 실패: {e}")

def cleanup_server():
    """서버 종료 시 정리 작업"""
    print("🛑 SpecGate MCP Server 종료")


# =============================================================================
# 서버 실행
# =============================================================================
if __name__ == "__main__":
    initialize_server()
    try:
        # FastMCP 서버 실행
        mcp.run()
    except KeyboardInterrupt:
        cleanup_server()
