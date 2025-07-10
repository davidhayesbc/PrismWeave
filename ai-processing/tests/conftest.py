"""
Pytest configuration and setup for PrismWeave AI processing tests
"""

import os
import sys
from pathlib import Path
import tempfile
import shutil
import pytest

# Add src directory to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Test configuration
TEST_CONFIG = {
    "ollama": {
        "host": "http://localhost:11434", 
        "timeout": 30,
        "models": {
            "large": "test-model",
            "medium": "test-model",
            "small": "test-model", 
            "embedding": "test-embedding"
        }
    },
    "processing": {
        "max_concurrent": 2,
        "chunk_size": 500,
        "chunk_overlap": 100,
        "min_chunk_size": 50,
        "summary_timeout": 60,
        "tagging_timeout": 30,
        "categorization_timeout": 15,
        "min_word_count": 10,
        "max_word_count": 10000,
        "max_summary_length": 200,
        "max_tags": 5
    },
    "vector": {
        "collection_name": "test_documents",
        "persist_directory": "./test_chroma_db",
        "embedding_function": "sentence-transformers",
        "max_results": 5,
        "similarity_threshold": 0.8
    },
    "log_level": "DEBUG"
}


@pytest.fixture(scope="session")
def test_temp_dir():
    """Create temporary directory for test files"""
    temp_dir = tempfile.mkdtemp(prefix="prismweave_test_")
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session") 
def test_config():
    """Test configuration fixture"""
    return TEST_CONFIG


@pytest.fixture
def cleanup_test_files():
    """Cleanup any test files created during testing"""
    created_files = []
    
    def register_file(file_path):
        created_files.append(file_path)
    
    yield register_file
    
    # Cleanup
    for file_path in created_files:
        try:
            if Path(file_path).exists():
                Path(file_path).unlink()
        except Exception:
            pass


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Set test environment variables
    os.environ["PRISMWEAVE_TEST"] = "1"
    os.environ["PRISMWEAVE_LOG_LEVEL"] = "DEBUG"
    
    yield
    
    # Cleanup environment
    os.environ.pop("PRISMWEAVE_TEST", None)
    os.environ.pop("PRISMWEAVE_LOG_LEVEL", None)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance benchmarks"
    )
    config.addinivalue_line(
        "markers", "network: marks tests that require network access"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Add markers based on test names
    for item in items:
        # Mark slow tests
        if "performance" in item.nodeid or "large" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if "integration" in item.nodeid or "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark performance tests
        if "performance" in item.nodeid or "benchmark" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        
        # Mark network tests
        if "ollama" in item.nodeid and "mock" not in item.nodeid:
            item.add_marker(pytest.mark.network)


# Custom pytest hooks
def pytest_runtest_setup(item):
    """Setup for each test"""
    # Skip network tests if no Ollama server
    if "network" in [marker.name for marker in item.iter_markers()]:
        try:
            import aiohttp
            import asyncio
            
            async def check_ollama():
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get("http://localhost:11434/api/version", timeout=5) as response:
                            return response.status == 200
                except:
                    return False
            
            if not asyncio.run(check_ollama()):
                pytest.skip("Ollama server not available")
        except ImportError:
            pytest.skip("aiohttp not available for network tests")


def pytest_runtest_teardown(item):
    """Teardown for each test"""
    # Clean up any test artifacts
    test_dirs = ["./test_chroma_db", "./perf_test_chroma_db", "./test_data"]
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            try:
                shutil.rmtree(test_dir)
            except Exception:
                pass


# Test utilities
class TestUtils:
    """Utility functions for tests"""
    
    @staticmethod
    def create_temp_file(content: str, suffix: str = ".txt", directory: str = None) -> str:
        """Create temporary file with content"""
        if directory:
            temp_dir = Path(directory)
            temp_dir.mkdir(exist_ok=True)
            fd, path = tempfile.mkstemp(suffix=suffix, dir=directory)
        else:
            fd, path = tempfile.mkstemp(suffix=suffix)
        
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return path
    
    @staticmethod
    def create_temp_config(config_data: dict, format: str = "yaml") -> str:
        """Create temporary config file"""
        if format == "yaml":
            import yaml
            content = yaml.dump(config_data)
            suffix = ".yaml"
        elif format == "json":
            import json
            content = json.dumps(config_data, indent=2)
            suffix = ".json"
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return TestUtils.create_temp_file(content, suffix)
    
    @staticmethod
    def assert_file_exists(file_path: str):
        """Assert that file exists"""
        assert Path(file_path).exists(), f"File does not exist: {file_path}"
    
    @staticmethod
    def assert_file_not_exists(file_path: str):
        """Assert that file does not exist"""
        assert not Path(file_path).exists(), f"File should not exist: {file_path}"
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes"""
        return Path(file_path).stat().st_size
    
    @staticmethod
    def count_lines(file_path: str) -> int:
        """Count lines in file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)


# Make TestUtils available as fixture
@pytest.fixture
def test_utils():
    """Test utilities fixture"""
    return TestUtils


# Async test utilities
class AsyncTestUtils:
    """Async utilities for tests"""
    
    @staticmethod
    async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1):
        """Wait for condition to become true"""
        import asyncio
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            if condition_func():
                return True
            
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"Condition not met within {timeout} seconds")
            
            await asyncio.sleep(interval)
    
    @staticmethod
    async def run_with_timeout(coro, timeout: float = 30.0):
        """Run coroutine with timeout"""
        import asyncio
        
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operation timed out after {timeout} seconds")


@pytest.fixture
def async_utils():
    """Async test utilities fixture"""
    return AsyncTestUtils


# Mock helpers
class MockHelpers:
    """Helper functions for creating mocks"""
    
    @staticmethod
    def create_mock_response(data: dict, status: int = 200):
        """Create mock HTTP response"""
        from unittest.mock import MagicMock
        
        mock_response = MagicMock()
        mock_response.status_code = status
        mock_response.json.return_value = data
        mock_response.text = str(data)
        
        return mock_response
    
    @staticmethod
    def create_mock_file(content: str, name: str = "test.txt"):
        """Create mock file object"""
        from unittest.mock import MagicMock
        import io
        
        mock_file = MagicMock()
        mock_file.read.return_value = content
        mock_file.name = name
        mock_file.__enter__.return_value = mock_file
        mock_file.__exit__.return_value = None
        
        # Make it behave like a file
        mock_file.readable.return_value = True
        mock_file.seekable.return_value = True
        mock_file.writable.return_value = False
        
        return mock_file


@pytest.fixture
def mock_helpers():
    """Mock helpers fixture"""
    return MockHelpers


# Error testing helpers
class ErrorTestHelpers:
    """Helpers for testing error conditions"""
    
    @staticmethod
    def assert_raises_with_message(exception_type, message_pattern, callable_obj, *args, **kwargs):
        """Assert that callable raises exception with specific message pattern"""
        import re
        
        with pytest.raises(exception_type) as exc_info:
            callable_obj(*args, **kwargs)
        
        assert re.search(message_pattern, str(exc_info.value)), \
            f"Exception message '{exc_info.value}' does not match pattern '{message_pattern}'"
    
    @staticmethod
    async def assert_async_raises_with_message(exception_type, message_pattern, async_callable, *args, **kwargs):
        """Assert that async callable raises exception with specific message pattern"""
        import re
        
        with pytest.raises(exception_type) as exc_info:
            await async_callable(*args, **kwargs)
        
        assert re.search(message_pattern, str(exc_info.value)), \
            f"Exception message '{exc_info.value}' does not match pattern '{message_pattern}'"


@pytest.fixture
def error_helpers():
    """Error testing helpers fixture"""
    return ErrorTestHelpers


# Performance testing helpers
class PerformanceHelpers:
    """Helpers for performance testing"""
    
    @staticmethod
    def measure_time(func, *args, **kwargs):
        """Measure execution time of function"""
        import time
        
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        return result, end_time - start_time
    
    @staticmethod
    async def measure_async_time(async_func, *args, **kwargs):
        """Measure execution time of async function"""
        import time
        
        start_time = time.perf_counter()
        result = await async_func(*args, **kwargs)
        end_time = time.perf_counter()
        
        return result, end_time - start_time
    
    @staticmethod
    def get_memory_usage():
        """Get current memory usage in MB"""
        try:
            import psutil
            return psutil.Process().memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0  # Return 0 if psutil not available


@pytest.fixture
def perf_helpers():
    """Performance testing helpers fixture"""
    return PerformanceHelpers


# Logging configuration for tests
def setup_test_logging():
    """Setup logging for tests"""
    import logging
    
    # Configure logging for tests
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test.log', mode='w')
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)


# Setup logging when module is imported
setup_test_logging()


# Export commonly used fixtures and utilities
__all__ = [
    'test_temp_dir',
    'test_config', 
    'cleanup_test_files',
    'test_utils',
    'async_utils',
    'mock_helpers',
    'error_helpers',
    'perf_helpers',
    'TestUtils',
    'AsyncTestUtils',
    'MockHelpers',
    'ErrorTestHelpers',
    'PerformanceHelpers'
]
