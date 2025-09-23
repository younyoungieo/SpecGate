#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from workflows.hitl.manager import HITLWorkflowManager, DocumentInfo, QualityResult


async def run():
    manager = HITLWorkflowManager()
    if not manager.github_client.is_configured():
        print("skip: github not configured")
        return 0

    # 간단한 세 케이스
    cases = [
        ("auto", 95, "auto_approve"),
        ("review", 75, "hitl_review_required"),
        ("fix", 45, "mandatory_fix_required"),
    ]
    ok = 0
    for name, score, expected in cases:
        doc = DocumentInfo(
            title=f"[{name}] 설계서",
            project_name="TestProject",
            doc_type="설계서",
            confluence_url="https://confluence.example.com/test",
            content="test",
        )
        quality = QualityResult(score=score, violations=[], suggestions=[], metadata={})
        result = await manager.process_quality_result(doc, quality)
        print(name, result.status, result.issue_url)
        ok += int(result.status == expected)
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))


