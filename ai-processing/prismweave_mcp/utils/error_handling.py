"""
Error Handling Utilities

Centralized error handling for MCP server operations.
"""

import logging
import traceback
from enum import Enum
from typing import Any

from prismweave_mcp.schemas.responses import ErrorResponse

logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    """Standard error codes for MCP operations"""

    # General errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # Document errors
    DOCUMENT_NOT_FOUND = "DOCUMENT_NOT_FOUND"
    DOCUMENT_EXISTS = "DOCUMENT_EXISTS"
    INVALID_PATH = "INVALID_PATH"
    PERMISSION_DENIED = "PERMISSION_DENIED"

    # Processing errors
    PROCESSING_FAILED = "PROCESSING_FAILED"
    EMBEDDING_GENERATION_FAILED = "EMBEDDING_GENERATION_FAILED"
    TAG_GENERATION_FAILED = "TAG_GENERATION_FAILED"

    # Search errors
    SEARCH_FAILED = "SEARCH_FAILED"
    INDEX_NOT_AVAILABLE = "INDEX_NOT_AVAILABLE"

    # Git errors
    GIT_OPERATION_FAILED = "GIT_OPERATION_FAILED"
    GIT_COMMIT_FAILED = "GIT_COMMIT_FAILED"
    GIT_PUSH_FAILED = "GIT_PUSH_FAILED"

    # Tool errors
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_EXECUTION_FAILED = "TOOL_EXECUTION_FAILED"


class MCPError(Exception):
    """Base exception for MCP operations"""

    def __init__(self, message: str, code: ErrorCode = ErrorCode.UNKNOWN_ERROR, details: dict[str, Any] | None = None):
        """
        Initialize MCP error

        Args:
            message: Error message
            code: Error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class DocumentNotFoundError(MCPError):
    """Raised when a document cannot be found"""

    def __init__(self, identifier: str, details: dict[str, Any] | None = None):
        super().__init__(f"Document not found: {identifier}", ErrorCode.DOCUMENT_NOT_FOUND, details)


class DocumentExistsError(MCPError):
    """Raised when attempting to create a document that already exists"""

    def __init__(self, path: str, details: dict[str, Any] | None = None):
        super().__init__(f"Document already exists: {path}", ErrorCode.DOCUMENT_EXISTS, details)


class InvalidPathError(MCPError):
    """Raised when a path is invalid or unsafe"""

    def __init__(self, path: str, reason: str, details: dict[str, Any] | None = None):
        super().__init__(f"Invalid path '{path}': {reason}", ErrorCode.INVALID_PATH, details)


class PermissionDeniedError(MCPError):
    """Raised when operation is not permitted"""

    def __init__(self, operation: str, reason: str, details: dict[str, Any] | None = None):
        super().__init__(f"Permission denied for '{operation}': {reason}", ErrorCode.PERMISSION_DENIED, details)


class ProcessingError(MCPError):
    """Raised when document processing fails"""

    def __init__(self, operation: str, reason: str, details: dict[str, Any] | None = None):
        super().__init__(f"Processing failed for '{operation}': {reason}", ErrorCode.PROCESSING_FAILED, details)


class SearchError(MCPError):
    """Raised when search operation fails"""

    def __init__(self, reason: str, details: dict[str, Any] | None = None):
        super().__init__(f"Search failed: {reason}", ErrorCode.SEARCH_FAILED, details)


class GitError(MCPError):
    """Raised when git operation fails"""

    def __init__(self, operation: str, reason: str, details: dict[str, Any] | None = None):
        code = ErrorCode.GIT_OPERATION_FAILED
        if "commit" in operation.lower():
            code = ErrorCode.GIT_COMMIT_FAILED
        elif "push" in operation.lower():
            code = ErrorCode.GIT_PUSH_FAILED

        super().__init__(f"Git operation '{operation}' failed: {reason}", code, details)


def create_error_response(
    error: Exception, context: str | None = None, include_traceback: bool = False
) -> dict[str, Any]:
    """
    Create a standardized error response

    Args:
        error: The exception that occurred
        context: Additional context about the error
        include_traceback: Whether to include full traceback (for debugging)

    Returns:
        ErrorResponse dict
    """
    # Extract error details
    if isinstance(error, MCPError):
        code = error.code.value
        message = error.message
        details = error.details
    else:
        code = ErrorCode.UNKNOWN_ERROR.value
        message = str(error)
        details = {"type": type(error).__name__}

    # Add context if provided
    if context:
        details["context"] = context

    # Add traceback for debugging
    if include_traceback:
        details["traceback"] = traceback.format_exc()

    # Create error response
    response = ErrorResponse(error=message, error_code=code, details=details)

    return response.model_dump()


def log_error(error: Exception, context: str | None = None, level: int = logging.ERROR) -> None:
    """
    Log an error with context

    Args:
        error: The exception to log
        context: Additional context
        level: Logging level
    """
    # Build log message
    message_parts = []

    if context:
        message_parts.append(f"[{context}]")

    if isinstance(error, MCPError):
        message_parts.append(f"{error.code.value}: {error.message}")
        if error.details:
            message_parts.append(f"Details: {error.details}")
    else:
        message_parts.append(f"{type(error).__name__}: {error}")

    message = " ".join(message_parts)

    # Log with appropriate level
    logger.log(level, message, exc_info=level >= logging.ERROR)


async def handle_tool_error(error: Exception, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """
    Handle errors from tool execution

    Args:
        error: The exception that occurred
        tool_name: Name of the tool that failed
        arguments: Arguments passed to the tool

    Returns:
        ErrorResponse dict
    """
    # Log the error
    context = f"Tool: {tool_name}"
    log_error(error, context)

    # Create error response with tool context
    response = create_error_response(error, context)

    # Add tool-specific details
    response["details"]["tool"] = tool_name
    response["details"]["arguments"] = arguments

    return response


def validate_arguments(arguments: dict[str, Any], required: list[str], optional: dict[str, Any] | None = None) -> None:
    """
    Validate tool arguments

    Args:
        arguments: Arguments to validate
        required: List of required argument names
        optional: Dict of optional arguments with default values

    Raises:
        MCPError: If validation fails
    """
    # Check required arguments
    missing = [arg for arg in required if arg not in arguments]
    if missing:
        raise MCPError(
            f"Missing required arguments: {', '.join(missing)}", ErrorCode.INVALID_INPUT, {"missing": missing}
        )

    # Add optional arguments with defaults
    if optional:
        for key, default_value in optional.items():
            if key not in arguments:
                arguments[key] = default_value
