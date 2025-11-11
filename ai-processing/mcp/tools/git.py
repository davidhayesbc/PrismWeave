"""
Git Operations MCP Tools

MCP tool implementations for version control operations.
"""

from typing import Any, Dict

from mcp.managers.git_manager import GitManager
from mcp.schemas.requests import CommitToGitRequest
from mcp.schemas.responses import CommitToGitResponse, ErrorResponse
from src.core.config import Config


class GitTools:
    """MCP tools for git operations"""

    def __init__(self, config: Config):
        """
        Initialize git tools

        Args:
            config: Configuration object
        """
        self.config = config
        self.git_manager = GitManager(config)

    async def commit_to_git(self, request: CommitToGitRequest) -> Dict[str, Any]:
        """
        Commit changes to git repository

        Args:
            request: Git commit request

        Returns:
            CommitToGitResponse dict or ErrorResponse dict
        """
        try:
            # Commit changes using GitManager
            result = self.git_manager.commit_changes(
                message=request.message, files=request.paths or None, push=request.push
            )

            if not result["success"]:
                error = ErrorResponse(
                    error=result.get("error", "Failed to commit changes"),
                    error_code="GIT_COMMIT_FAILED",
                    details={"message": request.message, "paths": request.paths},
                )
                return error.model_dump()

            # Convert to response format
            response = CommitToGitResponse(
                success=True,
                commit_hash=result.get("commit_sha"),
                files_committed=result.get("files_committed", 0),
                pushed=result.get("pushed", False),
                branch=result.get("branch"),
            )

            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to commit changes: {str(e)}",
                error_code="GIT_OPERATION_EXCEPTION",
                details={"message": request.message, "paths": request.paths},
            )
            return error.model_dump()
