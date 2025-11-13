"""
Git Operations MCP Tools

MCP tool implementations for version control operations.
"""

from typing import Any

from prismweave_mcp.managers.git_manager import GitManager
from prismweave_mcp.schemas.requests import CommitToGitRequest
from prismweave_mcp.schemas.responses import CommitToGitResponse, ErrorResponse
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

    async def commit_to_git(self, request: CommitToGitRequest) -> dict[str, Any]:
        """
        Commit changes to git repository

        Args:
            request: Git commit request

        Returns:
            CommitToGitResponse dict or ErrorResponse dict
        """
        try:
            # Commit changes using GitManager (use correct field names from schema)
            result = await self.git_manager.commit_changes(
                message=request.commit_message, files=request.file_paths or None, push=request.push
            )

            if not result["success"]:
                error = ErrorResponse(
                    error=result.get("error", "Failed to commit changes"),
                    error_code="GIT_COMMIT_FAILED",
                    details={"commit_message": request.commit_message, "file_paths": request.file_paths},
                )
                return error.model_dump()

            # Convert to response format (schema: success, commit_hash, message)
            response = CommitToGitResponse(
                success=True,
                commit_hash=result.get("commit_sha"),
                message=request.commit_message,
            )

            return response.model_dump()

        except Exception as e:
            error = ErrorResponse(
                error=f"Failed to commit changes: {str(e)}",
                error_code="GIT_OPERATION_EXCEPTION",
                details={"commit_message": request.commit_message, "file_paths": request.file_paths},
            )
            return error.model_dump()
