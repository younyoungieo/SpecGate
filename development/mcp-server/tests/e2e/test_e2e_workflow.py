#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

# mcp-server 루트를 모듈 경로에 추가
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from confluence_fetch import ConfluenceService
from speclint_lint import SpecLint
from workflows.hitl.manager import HITLWorkflowManager, DocumentInfo, QualityResult


async def run():
    confluence_service = ConfluenceService()
    speclint_engine = SpecLint()
    hitl_manager = HITLWorkflowManager()

    result = await confluence_service.fetch_documents(label="design", limit=1)
    docs = result.get("documents", [])
    if not docs:
        print("no docs")
        return 1

    doc = docs[0]
    quality = await speclint_engine.lint(doc["content"], "full")
    document_info = DocumentInfo(
        title=doc["title"],
        project_name="TestProject",
        doc_type="설계서",
        confluence_url=doc.get("url", ""),
        content=doc["content"],
        metadata=quality.get("metadata", {}),
    )
    quality_obj = QualityResult(
        score=quality.get("score", 0),
        violations=quality.get("violations", []),
        suggestions=quality.get("suggestions", []),
        metadata=quality.get("metadata", {}),
    )
    hitl = await hitl_manager.process_quality_result(document_info, quality_obj)
    print(hitl)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))


