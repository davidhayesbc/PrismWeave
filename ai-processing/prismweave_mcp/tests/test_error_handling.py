"""
Tests for Error Handling

Unit tests for error handling utilities.
"""

import logging
from unittest.mock import MagicMock, patch

import pytest

from prismweave_mcp.utils.error_handling import (
    DocumentExistsError,
    DocumentNotFoundError,
    ErrorCode,
    GitError,
    InvalidPathError,
    MCPError,
    PermissionDeniedError,
    ProcessingError,
    SearchError,
    create_error_response,
    handle_tool_error,
    log_error,
    validate_arguments,
)


def test_error_code_enum():
    """Test ErrorCode enum values"""
    assert ErrorCode.UNKNOWN_ERROR == "UNKNOWN_ERROR"
    assert ErrorCode.DOCUMENT_NOT_FOUND == "DOCUMENT_NOT_FOUND"
    assert ErrorCode.PROCESSING_FAILED == "PROCESSING_FAILED"
    assert ErrorCode.SEARCH_FAILED == "SEARCH_FAILED"
    assert ErrorCode.GIT_OPERATION_FAILED == "GIT_OPERATION_FAILED"


def test_mcp_error_basic():
    """Test basic MCPError"""
    error = MCPError("Test error")
    
    assert str(error) == "Test error"
    assert error.message == "Test error"
    assert error.code == ErrorCode.UNKNOWN_ERROR
    assert error.details == {}


def test_mcp_error_with_code_and_details():
    """Test MCPError with code and details"""
    details = {"key": "value"}
    error = MCPError(
        "Test error",
        ErrorCode.INVALID_INPUT,
        details
    )
    
    assert error.message == "Test error"
    assert error.code == ErrorCode.INVALID_INPUT
    assert error.details == details


def test_document_not_found_error():
    """Test DocumentNotFoundError"""
    error = DocumentNotFoundError("doc123")
    
    assert "doc123" in str(error)
    assert error.code == ErrorCode.DOCUMENT_NOT_FOUND


def test_document_exists_error():
    """Test DocumentExistsError"""
    error = DocumentExistsError("/path/to/doc.md")
    
    assert "/path/to/doc.md" in str(error)
    assert error.code == ErrorCode.DOCUMENT_EXISTS


def test_invalid_path_error():
    """Test InvalidPathError"""
    error = InvalidPathError("/bad/path", "contains ..")
    
    assert "/bad/path" in str(error)
    assert "contains .." in str(error)
    assert error.code == ErrorCode.INVALID_PATH


def test_permission_denied_error():
    """Test PermissionDeniedError"""
    error = PermissionDeniedError("update", "not in generated folder")
    
    assert "update" in str(error)
    assert "not in generated folder" in str(error)
    assert error.code == ErrorCode.PERMISSION_DENIED


def test_processing_error():
    """Test ProcessingError"""
    error = ProcessingError("embeddings", "model not available")
    
    assert "embeddings" in str(error)
    assert "model not available" in str(error)
    assert error.code == ErrorCode.PROCESSING_FAILED


def test_search_error():
    """Test SearchError"""
    error = SearchError("index corrupted")
    
    assert "index corrupted" in str(error)
    assert error.code == ErrorCode.SEARCH_FAILED


def test_git_error_commit():
    """Test GitError for commit operation"""
    error = GitError("commit", "no changes to commit")
    
    assert "commit" in str(error)
    assert "no changes to commit" in str(error)
    assert error.code == ErrorCode.GIT_COMMIT_FAILED


def test_git_error_push():
    """Test GitError for push operation"""
    error = GitError("push", "remote rejected")
    
    assert "push" in str(error)
    assert "remote rejected" in str(error)
    assert error.code == ErrorCode.GIT_PUSH_FAILED


def test_git_error_generic():
    """Test GitError for generic operation"""
    error = GitError("pull", "connection failed")
    
    assert "pull" in str(error)
    assert error.code == ErrorCode.GIT_OPERATION_FAILED


def test_create_error_response_from_mcp_error():
    """Test creating error response from MCPError"""
    error = MCPError(
        "Test error",
        ErrorCode.INVALID_INPUT,
        {"field": "test_field"}
    )
    
    response = create_error_response(error)
    
    assert response["error"] == "Test error"
    assert response["error_code"] == "INVALID_INPUT"
    assert response["details"]["field"] == "test_field"


def test_create_error_response_from_generic_exception():
    """Test creating error response from generic exception"""
    error = ValueError("Invalid value")
    
    response = create_error_response(error)
    
    assert response["error"] == "Invalid value"
    assert response["error_code"] == "UNKNOWN_ERROR"
    assert response["details"]["type"] == "ValueError"


def test_create_error_response_with_context():
    """Test creating error response with context"""
    error = Exception("Test error")
    
    response = create_error_response(error, context="Tool execution")
    
    assert response["details"]["context"] == "Tool execution"


def test_create_error_response_with_traceback():
    """Test creating error response with traceback"""
    error = Exception("Test error")
    
    response = create_error_response(error, include_traceback=True)
    
    assert "traceback" in response["details"]
    assert isinstance(response["details"]["traceback"], str)


def test_log_error_with_mcp_error(caplog):
    """Test logging MCPError"""
    error = MCPError(
        "Test error",
        ErrorCode.DOCUMENT_NOT_FOUND,
        {"doc_id": "123"}
    )
    
    with caplog.at_level(logging.ERROR):
        log_error(error)
    
    assert "DOCUMENT_NOT_FOUND" in caplog.text
    assert "Test error" in caplog.text


def test_log_error_with_context(caplog):
    """Test logging error with context"""
    error = Exception("Test error")
    
    with caplog.at_level(logging.ERROR):
        log_error(error, context="Test context")
    
    assert "Test context" in caplog.text


def test_log_error_with_custom_level(caplog):
    """Test logging error with custom level"""
    error = Exception("Warning message")
    
    with caplog.at_level(logging.WARNING):
        log_error(error, level=logging.WARNING)
    
    assert "Warning message" in caplog.text


@pytest.mark.asyncio
async def test_handle_tool_error():
    """Test handling tool errors"""
    error = MCPError("Tool failed", ErrorCode.TOOL_EXECUTION_FAILED)
    
    response = await handle_tool_error(
        error,
        "test_tool",
        {"arg1": "value1"}
    )
    
    assert response["error"] == "Tool failed"
    assert response["error_code"] == "TOOL_EXECUTION_FAILED"
    assert response["details"]["tool"] == "test_tool"
    assert response["details"]["arguments"] == {"arg1": "value1"}


@pytest.mark.asyncio
async def test_handle_tool_error_logs(caplog):
    """Test that handle_tool_error logs the error"""
    error = Exception("Test error")
    
    with caplog.at_level(logging.ERROR):
        await handle_tool_error(error, "test_tool", {})
    
    assert "Tool: test_tool" in caplog.text


def test_validate_arguments_success():
    """Test successful argument validation"""
    arguments = {"required1": "value1", "required2": "value2"}
    
    # Should not raise
    validate_arguments(arguments, ["required1", "required2"])


def test_validate_arguments_missing_required():
    """Test validation with missing required arguments"""
    arguments = {"required1": "value1"}
    
    with pytest.raises(MCPError) as exc_info:
        validate_arguments(arguments, ["required1", "required2"])
    
    assert "Missing required arguments" in str(exc_info.value)
    assert exc_info.value.code == ErrorCode.INVALID_INPUT
    assert "required2" in exc_info.value.details["missing"]


def test_validate_arguments_with_optional():
    """Test validation with optional arguments"""
    arguments = {"required1": "value1"}
    optional = {"optional1": "default1", "optional2": "default2"}
    
    validate_arguments(arguments, ["required1"], optional)
    
    # Optional defaults should be added
    assert arguments["optional1"] == "default1"
    assert arguments["optional2"] == "default2"


def test_validate_arguments_optional_not_overwrite():
    """Test that validation doesn't overwrite provided optional arguments"""
    arguments = {"required1": "value1", "optional1": "provided"}
    optional = {"optional1": "default1"}
    
    validate_arguments(arguments, ["required1"], optional)
    
    # Should keep provided value
    assert arguments["optional1"] == "provided"


def test_validate_arguments_empty_required():
    """Test validation with no required arguments"""
    arguments = {}
    
    # Should not raise
    validate_arguments(arguments, [])


def test_validate_arguments_multiple_missing():
    """Test validation with multiple missing arguments"""
    arguments = {}
    
    with pytest.raises(MCPError) as exc_info:
        validate_arguments(arguments, ["arg1", "arg2", "arg3"])
    
    assert len(exc_info.value.details["missing"]) == 3
