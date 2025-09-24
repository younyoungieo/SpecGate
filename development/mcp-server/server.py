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

# client_work_dir 글로벌 변수 제거됨 - 경로 설정 로직 단순화

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
from confluence_fetch import ConfluenceService

# Confluence 서비스 인스턴스 생성
confluence_service = ConfluenceService()

@mcp.tool()
async def confluence_fetch(
    label: str, 
    space_key: str | None = None, 
    limit: int = 10,
    save_html: bool = True,
    output_dir: str | None = None,
    auto_pipeline: bool = True,
    auto_create_github_issues: bool = True
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
    # _set_client_work_dir() 호출 제거됨 - 경로 설정 로직 단순화
    
    try:
        fetch_result = await confluence_service.fetch_documents(label, space_key, limit, save_html, output_dir)
    except RuntimeError as e:
        if "This event loop is already running" in str(e):
            # 이벤트 루프 충돌 시 간단한 오류 메시지 반환
            return {
                "status": "error",
                "documents": [],
                "metadata": {
                    "error": "이벤트 루프 충돌로 인해 Confluence 서비스를 실행할 수 없습니다. 서버를 재시작해주세요.",
                    "timestamp": datetime.now().isoformat(),
                    "search_label": label
                }
            }
        else:
            raise

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
                # HTML to Markdown 변환 (직접 변환기 인스턴스 사용)
                md_files_dir = _get_specgate_data_dir("md_files")
                
                # HTML 파일명 기반으로 MD 파일명 생성
                md_output_path = None
                html_timestamp = None
                if filename_base:
                    base_no_ext = _os.path.splitext(filename_base)[0]
                    md_output_path = _os.path.join(md_files_dir, f"{base_no_ext}.md")
                    # MD 파일 중복 처리: 동일 제목의 기존 타임스탬프 파일 제거
                    try:
                        import re as _re, glob as _glob
                        # safe_title 및 타임스탬프 분리
                        m_ts = _re.match(r"^(?P<safe>.+?)_(?P<ts>\d{8}_\d{6})$", base_no_ext)
                        safe_for_match = m_ts.group("safe") if m_ts else base_no_ext
                        html_timestamp = m_ts.group("ts") if m_ts else None
                        pattern = _os.path.join(md_files_dir, f"{safe_for_match}_*.md")
                        ts_regex = _re.compile(rf"^{_re.escape(safe_for_match)}_\d{{8}}_\d{{6}}\.md$")
                        for old_md in _glob.glob(pattern):
                            base_md = _os.path.basename(old_md)
                            if not ts_regex.match(base_md):
                                continue
                            try:
                                _os.remove(old_md)
                                logging.getLogger("specgate.html_to_md").info(f"기존 MD 파일 삭제(중복 처리): {old_md}")
                            except Exception as _e:
                                logging.getLogger("specgate.html_to_md").warning(f"기존 MD 파일 삭제 실패: {old_md} ({_e})")
                    except Exception as _outer_e:
                        logging.getLogger("specgate.html_to_md").warning(f"MD 중복 처리 단계 오류: {_outer_e}")
                
                # 문서 제목 가져오기
                document_title = doc.get("title", "")
                
                md_conv = await html_converter.convert(
                    html_content=html_content,
                    preserve_structure=True,
                    save_to_file=bool(md_output_path),
                    output_path=md_output_path,
                    document_title=document_title
                )
                markdown_text = md_conv.get("markdown")
                
                # SpecLint 품질 검사 (직접 엔진 인스턴스 사용)
                if markdown_text:
                    # auto_create_github_issues는 내부 speclint_lint의 HITL 호출과 별개로,
                    # 자동 파이프라인 단계에서의 HITL 연동 여부를 제어
                    lint_result = await speclint_engine.lint(markdown_text, "full", document_title)
                    # HITL 워크플로우 연동 (auto_pipeline 경로에서도 이슈 생성)
                    try:
                        # 문서 메타정보 준비
                        document_title = doc.get("title") or "unknown"
                        project_name = "unknown_project"
                        doc_type = "설계서"
                        # 제목에서 프로젝트명/문서유형 추출 시도: "[프로젝트명] 문서유형 설계서"
                        import re as _re
                        m = _re.match(r"\[([^\]]+)\]\s+(\w+)\s+설계서", document_title or "")
                        if m:
                            project_name = m.group(1)
                            doc_type = m.group(2)

                        from workflows.hitl.manager import DocumentInfo as _DocumentInfo, QualityResult as _QualityResult

                        document_info = _DocumentInfo(
                            title=document_title,
                            project_name=project_name,
                            doc_type=doc_type,
                            confluence_url=doc.get("url") or "N/A",
                            content=markdown_text,
                            metadata=lint_result.get("metadata", {})
                        )
                        quality_result = _QualityResult(
                            score=lint_result.get("score", 0),
                            violations=lint_result.get("violations", []),
                            suggestions=lint_result.get("suggestions", []),
                            metadata=lint_result.get("metadata", {})
                        )

                        hitl_result = None
                        if auto_create_github_issues:
                            hitl_result = await hitl_manager.process_quality_result(document_info, quality_result)

                        # 결과를 lint_result 메타데이터에 첨부
                        lint_result.setdefault("hitl_workflow", {})
                        lint_result["hitl_workflow"].update({
                            "status": getattr(hitl_result, "status", "unknown"),
                            "message": getattr(hitl_result, "message", ""),
                            "next_action": getattr(hitl_result, "next_action", None),
                            "issue_url": getattr(hitl_result, "issue_url", None),
                            "issue_number": getattr(hitl_result, "issue_number", None),
                            "workflow_id": getattr(hitl_result, "workflow_id", None),
                        })
                    except Exception as _hitl_e:
                        logging.getLogger("specgate.hitl").warning(f"자동 파이프라인 HITL 연동 실패: {_hitl_e}")
                    
                    # 품질 리포트 저장
                    try:
                        import json
                        from datetime import datetime
                        
                        reports_dir = _get_specgate_data_dir("quality_reports")
                        
                        # HTML 파일명에서 추출한 타임스탬프 사용 (없으면 현재 시각)
                        timestamp = html_timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
                        score = lint_result.get("score", 0)
                        quality_level = lint_result.get("metadata", {}).get("quality_level", "unknown")
                        report_filename = f"quality_report_{score}pts_{quality_level}_{timestamp}.json"
                        report_path = _os.path.join(reports_dir, report_filename)
                        
                        report_data = {
                            "timestamp": datetime.now().isoformat(),
                            "file_timestamp": timestamp,
                            "quality_score": score,
                            "quality_level": quality_level,
                            "check_type": "full",
                            "violations": lint_result.get("violations", []),
                            "suggestions": lint_result.get("suggestions", []),
                            "metadata": lint_result.get("metadata", {}),
                            "content_length": len(markdown_text)
                        }
                        
                        with open(report_path, 'w', encoding='utf-8') as f:
                            json.dump(report_data, f, ensure_ascii=False, indent=2)
                        
                        lint_result["metadata"]["report_saved"] = True
                        lint_result["metadata"]["report_path"] = report_path
                        
                        logging.getLogger("specgate.pipeline").info(f"품질 리포트 저장: {report_path}")
                        
                    except Exception as report_e:
                        logging.getLogger("specgate.pipeline").warning(f"품질 리포트 저장 실패: {report_e}")
                        lint_result["metadata"]["report_saved"] = False
                        lint_result["metadata"]["report_error"] = str(report_e)
                else:
                    lint_result = {"score": 0}
                md_results.append({
                    "title": doc.get("title"),
                    "html_file": html_files[idx] if idx < len(html_files) else None,
                    "markdown_file": md_output_path or md_conv.get("conversion_info", {}).get("file_path"),
                    "lint": lint_result
                })
            fetch_result["metadata"]["pipeline_results"] = md_results
        except Exception as e:
            logging.getLogger("specgate.pipeline").warning(f"자동 파이프라인 처리 중 경고: {e}")
    
    return fetch_result


# =============================================================================
# 2. speclint.lint 도구 구현 (HITL 워크플로우 통합)
# =============================================================================
from speclint_lint import SpecLint
from workflows.hitl.manager import HITLWorkflowManager, DocumentInfo, QualityResult

# SpecLint 인스턴스 생성
speclint_engine = SpecLint()

# HITL 워크플로우 매니저 생성
hitl_manager = HITLWorkflowManager()

@mcp.tool()
async def speclint_lint(
    content: str,
    check_type: str = "full",
    save_report: bool = True,
    output_dir: str = None,
    enable_hitl: bool = True,
    document_title: str = None,
    project_name: str = None,
    doc_type: str = None,
    confluence_url: str = None
) -> dict:
    """문서의 표준 템플릿 준수 여부를 검사하고 품질 점수를 계산
    
    Args:
        content: 검사할 문서 내용 (필수)
        check_type: 검사 유형 ("full", "basic", "structure") (기본값: "full")
        save_report: 품질 리포트 파일 저장 여부 (기본값: True)
        output_dir: 저장할 디렉토리 (기본값: None, 자동 감지)
        enable_hitl: HITL 워크플로우 활성화 여부 (기본값: True)
        document_title: 문서 제목 (HITL용, 기본값: None)
        project_name: 프로젝트명 (HITL용, 기본값: None)
        doc_type: 문서 유형 (HITL용, 기본값: None)
        confluence_url: Confluence URL (HITL용, 기본값: None)
    
    Returns:
        dict: {
            "score": int,  # 0-100 점수
            "violations": List[dict],
            "suggestions": List[str],
            "metadata": dict,
            "hitl_workflow": dict  # HITL 워크플로우 결과 (enable_hitl=True인 경우)
        }
    """
    result = await speclint_engine.lint(content, check_type, document_title)
    
    # HITL 워크플로우 처리
    hitl_result = None
    if enable_hitl:
        try:
            # 문서 정보 추출 (제목에서 프로젝트명과 문서유형 추출 시도)
            if not document_title:
                # content에서 제목 추출 시도
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('# '):
                        document_title = line[2:].strip()
                        break
            
            if not project_name and document_title:
                # 제목에서 프로젝트명 추출 시도: "[프로젝트명] [문서유형] 설계서"
                import re
                match = re.match(r'\[([^\]]+)\]\s+(\w+)\s+설계서', document_title)
                if match:
                    project_name = match.group(1)
                    if not doc_type:
                        doc_type = match.group(2)
            
            # 기본값 설정
            if not project_name:
                project_name = "unknown_project"
            if not doc_type:
                doc_type = "설계서"
            if not document_title:
                document_title = f"{project_name} {doc_type}"
            
            # 문서 정보 생성
            document_info = DocumentInfo(
                title=document_title,
                project_name=project_name,
                doc_type=doc_type,
                confluence_url=confluence_url or "N/A",
                content=content,
                metadata=result.get("metadata", {})
            )
            
            # 품질 결과 생성
            quality_result = QualityResult(
                score=result.get("score", 0),
                violations=result.get("violations", []),
                suggestions=result.get("suggestions", []),
                metadata=result.get("metadata", {})
            )
            
            # HITL 워크플로우 실행
            hitl_result = await hitl_manager.process_quality_result(document_info, quality_result)
            
            # 결과에 HITL 워크플로우 정보 추가
            result["hitl_workflow"] = {
                "status": hitl_result.status,
                "message": hitl_result.message,
                "next_action": hitl_result.next_action,
                "issue_url": hitl_result.issue_url,
                "issue_number": hitl_result.issue_number,
                "workflow_id": hitl_result.workflow_id
            }
            
            logging.getLogger("specgate.hitl").info(f"HITL 워크플로우 완료: {hitl_result.status}")
            
        except Exception as e:
            logging.getLogger("specgate.hitl").warning(f"HITL 워크플로우 처리 중 오류: {e}")
            result["hitl_workflow"] = {
                "status": "error",
                "message": f"HITL 워크플로우 처리 중 오류: {str(e)}",
                "next_action": "manual_review_required"
            }
    
    # 품질 리포트 저장
    if save_report:
        try:
            import os
            import json
            from datetime import datetime
            
            # 출력 디렉토리 결정 및 생성
            reports_dir = _get_specgate_data_dir("quality_reports", output_dir)
            
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
# 2.5. HITL 워크플로우 관리 도구
# =============================================================================

@mcp.tool()
async def hitl_check_status(workflow_id: str) -> dict:
    """HITL 워크플로우 상태 확인
    
    Args:
        workflow_id: 워크플로우 ID (필수)
    
    Returns:
        dict: 워크플로우 상태 정보
    """
    try:
        result = await hitl_manager.check_workflow_status(workflow_id)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"워크플로우 상태 확인 실패: {str(e)}"
        }

@mcp.tool()
async def hitl_update_status(
    workflow_id: str, 
    new_status: str, 
    comment: str = None
) -> dict:
    """HITL 워크플로우 상태 업데이트
    
    Args:
        workflow_id: 워크플로우 ID (필수)
        new_status: 새로운 상태 (필수)
        comment: 상태 변경 코멘트 (선택사항)
    
    Returns:
        dict: 업데이트 결과
    """
    try:
        result = await hitl_manager.update_workflow_status(workflow_id, new_status, comment)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"워크플로우 상태 업데이트 실패: {str(e)}"
        }

@mcp.tool()
async def hitl_get_summary() -> dict:
    """HITL 워크플로우 요약 정보 조회
    
    Returns:
        dict: 워크플로우 요약 정보
    """
    try:
        summary = hitl_manager.get_workflow_summary()
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"워크플로우 요약 조회 실패: {str(e)}"
        }


# =============================================================================
# 3. html.to_md 도구 구현 (리팩토링된 모듈 사용)
# =============================================================================
from html_to_md import HTMLToMarkdownConverter

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
        
        # 출력 디렉토리 결정 및 생성
        base_dir = _get_specgate_data_dir("md_files", output_dir)
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
                # HTML 파일명에 타임스탬프가 있다면 동일 타임스탬프를 MD에도 사용
                final_name = f"{safe_title}.md"
            else:
                # html_files에서 동일 제목의 최신 타임스탬프를 찾아서 사용
                try:
                    client_dir = _get_client_work_dir()
                    html_dir = os.path.join(client_dir, ".specgate", "data", "html_files")
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
            # MD 파일 중복 처리: 동일 safe_title의 이전 타임스탬프 MD 삭제
            try:
                ts_regex_md = re.compile(rf"^{re.escape(safe_title)}_\d{{8}}_\d{{6}}\.md$")
                for old_md in glob.glob(os.path.join(base_dir, f"{safe_title}_*.md")):
                    base_md = os.path.basename(old_md)
                    if not ts_regex_md.match(base_md):
                        continue
                    try:
                        os.remove(old_md)
                        logging.getLogger("specgate.html_to_md").info(f"기존 MD 파일 삭제(중복 처리): {old_md}")
                    except Exception as _e:
                        logging.getLogger("specgate.html_to_md").warning(f"기존 MD 파일 삭제 실패: {old_md} ({_e})")
            except Exception as _outer_e:
                logging.getLogger("specgate.html_to_md").warning(f"MD 중복 처리 단계 오류: {_outer_e}")
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
def _get_specgate_data_dir(subfolder: str, output_dir: str = None) -> str:
    """SpecGate 데이터 디렉토리 경로를 생성하고 디렉토리를 생성한다.
    
    Args:
        subfolder: 하위 폴더명 ('html_files', 'md_files', 'quality_reports', 'logs')
        output_dir: 사용자 지정 출력 디렉토리 (선택사항)
    
    Returns:
        str: 생성된 디렉토리의 전체 경로
    """
    import os
    
    # 1. 출력 디렉토리 결정
    if output_dir:
        # 사용자가 지정한 디렉토리 사용
        _od = os.path.normpath(output_dir)
        marker = os.path.join(".specgate", "data")
        
        if marker in _od:
            # .specgate/data 이후의 하위 폴더는 제거하고 지정된 subfolder로 고정
            marker_idx = _od.find(marker)
            before_specgate = _od[:marker_idx]
            target_dir = os.path.join(before_specgate, ".specgate", "data", subfolder)
        else:
            # 프로젝트 루트로 간주하여 .specgate/data/{subfolder} 하위로 저장
            target_dir = os.path.join(output_dir, ".specgate", "data", subfolder)
    else:
        # 자동으로 클라이언트 작업 디렉토리 사용
        client_dir = _get_client_work_dir()
        if subfolder == 'logs':
            # 로그는 .specgate/logs 에 저장
            target_dir = os.path.join(client_dir, ".specgate", "logs")
        else:
            # 데이터는 .specgate/data/{subfolder} 에 저장  
            target_dir = os.path.join(client_dir, ".specgate", "data", subfolder)
    
    # 2. 디렉토리 생성
    os.makedirs(target_dir, exist_ok=True)
    
    # _set_client_work_dir() 호출 제거됨 - 경로 설정 로직 단순화
    
    return target_dir

def _get_client_work_dir():
    """클라이언트 작업 디렉토리를 자동으로 감지"""
    import os
    # 우선순위: 환경변수 → 현재 디렉토리 (글로벌 캐시 제거)
    # global client_work_dir 캐시를 사용하지 않음 - 매번 새로 감지

    # 1. 환경변수 확인
    env_dir = os.environ.get('CLIENT_WORK_DIR')
    if env_dir and os.path.exists(env_dir):
        return env_dir

    # 2. 기본값: 현재 작업 디렉토리
    current_dir = os.getcwd()
    return current_dir

def initialize_server():
    """서버 시작 시 초기화 작업"""
    print("🚀 SpecGate MCP Server 시작")
    print("📋 등록된 도구들:")
    print("  - confluence_fetch: Confluence 문서 수집 및 HTML 원본 저장")
    print("  - speclint_lint: 문서 품질 검사 및 점수 계산 (HITL 워크플로우 통합)")
    print("  - html_to_md: HTML을 Markdown으로 변환")
    print("  - hitl_check_status: HITL 워크플로우 상태 확인")
    print("  - hitl_update_status: HITL 워크플로우 상태 업데이트")
    print("  - hitl_get_summary: HITL 워크플로우 요약 조회")
    print("🗂️ 워크플로우 디렉토리:")
    print("  - .specgate/data/html_files/: HTML 원본 저장")
    print("  - .specgate/data/md_files/: 변환된 Markdown 저장")
    print("  - .specgate/data/quality_reports/: 품질 검사 결과 저장")
    print("  - .specgate/logs/: 서버 실행 로그")
    print("🔄 HITL 워크플로우:")
    print("  - 90점 이상: 자동 승인 → Phase 2 진행")
    print("  - 70-89점: HITL 검토용 GitHub Issue 생성")
    print("  - 70점 미만: 필수 수정용 GitHub Issue 생성")
    
    # 클라이언트 작업 디렉토리 자동 감지
    client_dir = _get_client_work_dir()
    print(f"📁 자동 감지된 클라이언트 작업 디렉토리: {client_dir}")

    # 파일 로거 재설정: .specgate/logs/specgate.log
    try:
        logs_dir = _get_specgate_data_dir("logs")
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

# _set_client_work_dir() 함수 제거됨 - 경로 설정 로직 단순화

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
