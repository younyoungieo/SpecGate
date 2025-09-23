"""
HITL Workflow Manager (moved to workflows/hitl)
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

try:
    from integrations.github.client import GitHubAPIClient, GitHubIssueTemplates, GitHubIssue
except Exception:  # pragma: no cover
    from github_client import GitHubAPIClient, GitHubIssueTemplates, GitHubIssue


@dataclass
class DocumentInfo:
    title: str
    project_name: str
    doc_type: str
    confluence_url: str
    content: str
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


@dataclass
class QualityResult:
    score: int
    violations: List[Dict[str, Any]]
    suggestions: List[str]
    metadata: Dict[str, Any]

    @property
    def quality_level(self) -> str:
        if self.score >= 90:
            return "high_quality"
        elif self.score >= 70:
            return "medium_quality"
        return "low_quality"


@dataclass
class HITLWorkflowResult:
    status: str
    message: str
    next_action: str
    issue_url: Optional[str] = None
    issue_number: Optional[int] = None
    workflow_id: Optional[str] = None


class HITLWorkflowManager:
    def __init__(self) -> None:
        self.logger = logging.getLogger("specgate.hitl.manager")
        self.github_client = GitHubAPIClient()
        self.workflow_states: Dict[str, Dict[str, Any]] = {}

    async def process_quality_result(self, document: DocumentInfo, quality_result: QualityResult) -> HITLWorkflowResult:
        self.logger.info(f"HITL 워크플로우 시작 - 문서: {document.title}, 점수: {quality_result.score}")

        try:
            if not self.github_client.is_configured():
                return HITLWorkflowResult(
                    status="error",
                    message="GitHub 환경변수가 설정되지 않았습니다. HITL 워크플로우를 사용할 수 없습니다.",
                    next_action="github_setup_required",
                )

            if quality_result.quality_level == "high_quality":
                return await self._handle_auto_approve(document, quality_result)
            if quality_result.quality_level == "medium_quality":
                return await self._handle_hitl_review(document, quality_result)
            return await self._handle_mandatory_fix(document, quality_result)
        except Exception as e:  # pragma: no cover
            self.logger.error(f"HITL 워크플로우 처리 중 오류: {str(e)}")
            return HITLWorkflowResult(
                status="error",
                message=f"워크플로우 처리 중 오류 발생: {str(e)}",
                next_action="manual_review_required",
            )

    async def _handle_auto_approve(self, document: DocumentInfo, quality_result: QualityResult) -> HITLWorkflowResult:
        self.logger.info(f"자동 승인 - 문서: {document.title}, 점수: {quality_result.score}")
        workflow_id = f"auto_approve_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.workflow_states[workflow_id] = {
            "status": "auto_approve",
            "document": document.title,
            "score": quality_result.score,
            "timestamp": datetime.now().isoformat(),
        }
        return HITLWorkflowResult(
            status="auto_approve",
            message="✅ 문서가 표준을 준수합니다 (90점 이상). Phase 2 진행 가능합니다.",
            next_action="proceed_to_phase2",
            workflow_id=workflow_id,
        )

    async def _handle_hitl_review(self, document: DocumentInfo, quality_result: QualityResult) -> HITLWorkflowResult:
        self.logger.info(f"HITL 검토 요청 - 문서: {document.title}, 점수: {quality_result.score}")
        issue = GitHubIssueTemplates.create_hitl_review_issue(
            project_name=document.project_name,
            doc_type=document.doc_type,
            score=quality_result.score,
            confluence_url=document.confluence_url,
            violations=quality_result.violations,
            suggestions=quality_result.suggestions,
        )
        result = await self.github_client.create_issue(issue)
        if result["status"] == "success":
            workflow_id = f"hitl_review_{result['issue_number']}"
            self.workflow_states[workflow_id] = {
                "status": "hitl_review_pending",
                "document": document.title,
                "score": quality_result.score,
                "issue_number": result["issue_number"],
                "issue_url": result["issue_url"],
                "timestamp": datetime.now().isoformat(),
            }
            return HITLWorkflowResult(
                status="hitl_review_required",
                message=f"⚠️ HITL 검토가 필요합니다. GitHub Issue: {result['issue_url']}",
                next_action="manual_review_required",
                issue_url=result["issue_url"],
                issue_number=result["issue_number"],
                workflow_id=workflow_id,
            )
        return HITLWorkflowResult(
            status="error",
            message=f"GitHub Issue 생성 실패: {result.get('error', 'Unknown error')}",
            next_action="manual_review_required",
        )

    async def _handle_mandatory_fix(self, document: DocumentInfo, quality_result: QualityResult) -> HITLWorkflowResult:
        self.logger.info(f"필수 수정 요청 - 문서: {document.title}, 점수: {quality_result.score}")
        issue = GitHubIssueTemplates.create_mandatory_fix_issue(
            project_name=document.project_name,
            doc_type=document.doc_type,
            score=quality_result.score,
            confluence_url=document.confluence_url,
            violations=quality_result.violations,
            suggestions=quality_result.suggestions,
        )
        result = await self.github_client.create_issue(issue)
        if result["status"] == "success":
            workflow_id = f"mandatory_fix_{result['issue_number']}"
            self.workflow_states[workflow_id] = {
                "status": "mandatory_fix_pending",
                "document": document.title,
                "score": quality_result.score,
                "issue_number": result["issue_number"],
                "issue_url": result["issue_url"],
                "timestamp": datetime.now().isoformat(),
            }
            return HITLWorkflowResult(
                status="mandatory_fix_required",
                message=f"❌ 문서 수정이 필수입니다. GitHub Issue: {result['issue_url']}",
                next_action="manual_fix_required",
                issue_url=result["issue_url"],
                issue_number=result["issue_number"],
                workflow_id=workflow_id,
            )
        return HITLWorkflowResult(
            status="error",
            message=f"GitHub Issue 생성 실패: {result.get('error', 'Unknown error')}",
            next_action="manual_review_required",
        )

    async def check_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        if workflow_id not in self.workflow_states:
            return {"status": "not_found", "message": f"워크플로우 ID를 찾을 수 없습니다: {workflow_id}"}
        workflow = self.workflow_states[workflow_id]
        if workflow.get("issue_number"):
            try:
                issue_result = await self.github_client.get_issue(workflow["issue_number"])
                if issue_result["status"] == "success":
                    issue = issue_result["issue"]
                    workflow["github_status"] = issue["state"]
                    workflow["github_labels"] = [label["name"] for label in issue.get("labels", [])]
                    if "specgate:approved" in workflow["github_labels"]:
                        workflow["status"] = "approved"
                    elif "specgate:rejected" in workflow["github_labels"]:
                        workflow["status"] = "rejected"
                    elif "specgate:fixed" in workflow["github_labels"]:
                        workflow["status"] = "fixed"
            except Exception:  # pragma: no cover
                self.logger.warning("Issue 상태 확인 실패")
        return {"status": "success", "workflow": workflow}

    async def update_workflow_status(self, workflow_id: str, new_status: str, comment: str = None) -> Dict[str, Any]:
        if workflow_id not in self.workflow_states:
            return {"status": "not_found", "message": f"워크플로우 ID를 찾을 수 없습니다: {workflow_id}"}
        workflow = self.workflow_states[workflow_id]
        old_status = workflow["status"]
        workflow["status"] = new_status
        workflow["updated_at"] = datetime.now().isoformat()
        if workflow.get("issue_number") and comment:
            try:
                await self.github_client.add_comment(workflow["issue_number"], comment)
            except Exception:  # pragma: no cover
                self.logger.warning("Issue 댓글 추가 실패")
        self.logger.info(f"워크플로우 상태 업데이트: {workflow_id} ({old_status} → {new_status})")
        return {"status": "success", "workflow": workflow, "message": f"상태가 {old_status}에서 {new_status}로 변경되었습니다."}

    def get_workflow_summary(self) -> Dict[str, Any]:
        total_workflows = len(self.workflow_states)
        status_counts: Dict[str, int] = {}
        for workflow in self.workflow_states.values():
            status = workflow["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        return {
            "total_workflows": total_workflows,
            "status_counts": status_counts,
            "recent_workflows": list(self.workflow_states.values())[-5:],
        }


