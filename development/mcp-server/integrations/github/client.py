from __future__ import annotations

"""
GitHub API 클라이언트 (정리된 위치: integrations/github)
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


LOGGER_NAME = "specgate.github.client"


@dataclass
class GitHubIssue:
    title: str
    body: str
    labels: Optional[List[str]] = None


class GitHubIssueTemplates:
    @staticmethod
    def create_hitl_review_issue(
        project_name: str,
        doc_type: str,
        score: int,
        confluence_url: str,
        violations: List[Dict[str, Any]],
        suggestions: List[str],
    ) -> GitHubIssue:
        title = f"[HITL 검토] {project_name} {doc_type} - 품질점수 {score}점"
        body_lines: List[str] = [
            f"문서 품질 점수: {score}",
            "",
            f"Confluence: {confluence_url}",
            "",
            "## 위반사항",
        ]
        for v in (violations or []):
            body_lines.append(f"- {v.get('rule_id', 'RULE')} - {v.get('message', '')}")
        body_lines.append("")
        body_lines.append("## 개선 제안")
        for s in (suggestions or []):
            body_lines.append(f"- {s}")

        labels = ["specgate:hitl", "specgate:review_required"]
        return GitHubIssue(title=title, body="\n".join(body_lines), labels=labels)

    @staticmethod
    def create_mandatory_fix_issue(
        project_name: str,
        doc_type: str,
        score: int,
        confluence_url: str,
        violations: List[Dict[str, Any]],
        suggestions: List[str],
    ) -> GitHubIssue:
        title = f"[필수 수정] {project_name} {doc_type} - 품질점수 {score}점"
        body_lines: List[str] = [
            "문서 품질이 기준 미달입니다. 아래 항목을 수정해주세요.",
            "",
            f"문서 품질 점수: {score}",
            f"Confluence: {confluence_url}",
            "",
            "## 위반사항",
        ]
        for v in (violations or []):
            body_lines.append(f"- {v.get('rule_id', 'RULE')} - {v.get('message', '')}")
        body_lines.append("")
        body_lines.append("## 개선 제안")
        for s in (suggestions or []):
            body_lines.append(f"- {s}")

        labels = ["specgate:mandatory_fix", "specgate:review_required"]
        return GitHubIssue(title=title, body="\n".join(body_lines), labels=labels)


class GitHubAPIClient:
    def __init__(self) -> None:
        self.logger = logging.getLogger(LOGGER_NAME)
        self.token: Optional[str] = None
        self.owner: Optional[str] = None
        self.repo: Optional[str] = None
        self.base_url: Optional[str] = None
        self._validate_environment()

    def _validate_environment(self) -> None:
        self.token = os.getenv("GITHUB_TOKEN")
        self.owner = os.getenv("GITHUB_OWNER")
        self.repo = os.getenv("GITHUB_REPO")

        if self.token:
            self.logger.info(f"✅ GITHUB_TOKEN: {self.token[:8]}...")
        else:
            self.logger.warning("❌ GITHUB_TOKEN 미설정")

        if self.owner:
            self.logger.info(f"✅ GITHUB_OWNER: {self.owner[:10]}...")
        else:
            self.logger.warning("❌ GITHUB_OWNER 미설정")

        if self.repo:
            self.logger.info(f"✅ GITHUB_REPO: {self.repo[:10]}...")
        else:
            self.logger.warning("❌ GITHUB_REPO 미설정")

        if self.owner and self.repo:
            self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"

    def is_configured(self) -> bool:
        return bool(self.token and self.owner and self.repo and self.base_url)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def create_issue(self, issue: GitHubIssue) -> Dict[str, Any]:
        if not self.is_configured():
            return {"status": "error", "error": "GitHub client not configured"}

        payload: Dict[str, Any] = {
            "title": issue.title,
            "body": issue.body,
        }
        if issue.labels:
            payload["labels"] = issue.labels

        url = f"{self.base_url}/issues"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=self._headers(), json=payload)
            if resp.status_code in (200, 201):
                data = resp.json()
                number = data.get("number")
                html_url = data.get("html_url")
                self.logger.info(f"✅ GitHub Issue 생성 성공: #{number} - {issue.title}")
                return {"status": "success", "issue_number": number, "issue_url": html_url}
            else:
                try:
                    error_text = resp.text
                except Exception:
                    error_text = f"status={resp.status_code}"
                self.logger.error(f"❌ Issue 생성 실패: {error_text}")
                return {"status": "error", "error": error_text}

    async def get_issue(self, issue_number: int) -> Dict[str, Any]:
        if not self.is_configured():
            return {"status": "error", "error": "GitHub client not configured"}
        url = f"{self.base_url}/issues/{issue_number}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self._headers())
            if resp.status_code == 200:
                return {"status": "success", "issue": resp.json()}
            return {"status": "error", "error": resp.text}

    async def update_issue(self, issue_number: int, fields: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_configured():
            return {"status": "error", "error": "GitHub client not configured"}
        url = f"{self.base_url}/issues/{issue_number}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.patch(url, headers=self._headers(), json=fields)
            if resp.status_code == 200:
                return {"status": "success", "issue": resp.json()}
            return {"status": "error", "error": resp.text}

    async def add_comment(self, issue_number: int, comment: str) -> Dict[str, Any]:
        if not self.is_configured():
            return {"status": "error", "error": "GitHub client not configured"}
        url = f"{self.base_url}/issues/{issue_number}/comments"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=self._headers(), json={"body": comment})
            if resp.status_code in (200, 201):
                return {"status": "success", "comment": resp.json()}
            return {"status": "error", "error": resp.text}

    async def add_labels(self, issue_number: int, labels: List[str]) -> Dict[str, Any]:
        if not self.is_configured():
            return {"status": "error", "error": "GitHub client not configured"}
        url = f"{self.base_url}/issues/{issue_number}/labels"
        payload = {"labels": labels}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=self._headers(), json=payload)
            if resp.status_code in (200, 201):
                return {"status": "success", "labels": resp.json()}
            return {"status": "error", "error": resp.text}



