"""
Deprecated shim. Use integrations.github.client instead.
"""

from integrations.github.client import (
    GitHubAPIClient,
    GitHubIssueTemplates,
    GitHubIssue,
)

__all__ = [
    "GitHubAPIClient",
    "GitHubIssueTemplates",
    "GitHubIssue",
]


