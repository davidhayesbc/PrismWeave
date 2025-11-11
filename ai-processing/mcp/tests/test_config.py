"""
Tests for MCP configuration loading and validation
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from src.core.config import (
    Config,
    MCPConfig,
    MCPCreationConfig,
    MCPGitConfig,
    MCPPathsConfig,
    MCPRateLimitingConfig,
    MCPSearchConfig,
    load_config,
)


class TestMCPPathsConfig:
    """Tests for MCPPathsConfig"""

    def test_default_values(self) -> None:
        """Test default path values"""
        config = MCPPathsConfig()

        assert config.documents_root == "../../PrismWeaveDocs"
        assert config.documents_dir == "documents"
        assert config.generated_dir == "generated"
        assert config.images_dir == "images"
        assert config.tech_dir == "tech"

    def test_custom_values(self) -> None:
        """Test custom path values"""
        config = MCPPathsConfig(documents_root="/custom/path", documents_dir="docs")

        assert config.documents_root == "/custom/path"
        assert config.documents_dir == "docs"


class TestMCPSearchConfig:
    """Tests for MCPSearchConfig"""

    def test_default_values(self) -> None:
        """Test default search values"""
        config = MCPSearchConfig()

        assert config.max_results == 20
        assert config.similarity_threshold == 0.6
        assert config.default_filters == {}

    def test_custom_values(self) -> None:
        """Test custom search values"""
        config = MCPSearchConfig(max_results=50, similarity_threshold=0.8, default_filters={"category": "tech"})

        assert config.max_results == 50
        assert config.similarity_threshold == 0.8
        assert config.default_filters == {"category": "tech"}


class TestMCPCreationConfig:
    """Tests for MCPCreationConfig"""

    def test_default_values(self) -> None:
        """Test default creation values"""
        config = MCPCreationConfig()

        assert config.auto_process is True
        assert config.auto_commit is False
        assert config.default_category == "general"


class TestMCPGitConfig:
    """Tests for MCPGitConfig"""

    def test_default_values(self) -> None:
        """Test default git values"""
        config = MCPGitConfig()

        assert config.auto_push is False
        assert config.commit_message_template == "Add document: {title}"
        assert config.branch == "main"


class TestMCPRateLimitingConfig:
    """Tests for MCPRateLimitingConfig"""

    def test_default_values(self) -> None:
        """Test default rate limiting values"""
        config = MCPRateLimitingConfig()

        assert config.search == 60
        assert config.create == 30
        assert config.process == 20


class TestMCPConfig:
    """Tests for MCPConfig"""

    def test_default_values(self) -> None:
        """Test default MCP configuration"""
        config = MCPConfig()

        assert isinstance(config.paths, MCPPathsConfig)
        assert isinstance(config.search, MCPSearchConfig)
        assert isinstance(config.creation, MCPCreationConfig)
        assert isinstance(config.git, MCPGitConfig)
        assert isinstance(config.rate_limiting, MCPRateLimitingConfig)


class TestConfig:
    """Tests for main Config class"""

    def test_default_config(self) -> None:
        """Test creating config with defaults"""
        config = Config()

        assert config.ollama_host == "http://localhost:11434"
        assert config.ollama_timeout == 60
        assert config.chunk_size == 1000
        assert isinstance(config.mcp, MCPConfig)

    def test_mcp_config_included(self) -> None:
        """Test that MCP config is included"""
        config = Config()

        assert config.mcp is not None
        assert config.mcp.paths.documents_root == "../../PrismWeaveDocs"
        assert config.mcp.search.max_results == 20

    def test_validation_success(self) -> None:
        """Test validation with valid config"""
        config = Config()

        issues = config.validate()

        assert len(issues) == 0

    def test_validation_invalid_chunk_size(self) -> None:
        """Test validation with invalid chunk size"""
        config = Config(chunk_size=-10)

        issues = config.validate()

        assert len(issues) > 0
        assert any("chunk size" in issue.lower() for issue in issues)

    def test_validation_invalid_similarity_threshold(self) -> None:
        """Test validation with invalid similarity threshold"""
        config = Config()
        config.mcp.search.similarity_threshold = 1.5

        issues = config.validate()

        assert len(issues) > 0
        assert any("similarity" in issue.lower() for issue in issues)


class TestLoadConfig:
    """Tests for load_config function"""

    def test_load_from_yaml(self) -> None:
        """Test loading configuration from YAML file"""
        config_data = {
            "ollama": {"host": "http://custom:11434", "timeout": 120, "models": {"embedding": "custom-model"}},
            "processing": {"chunk_size": 2000, "chunk_overlap": 400},
            "vector": {"collection_name": "test_collection", "persist_directory": "/custom/path"},
            "mcp": {
                "paths": {"documents_root": "/custom/docs", "documents_dir": "articles"},
                "search": {"max_results": 50, "similarity_threshold": 0.8},
                "creation": {"auto_process": False, "auto_commit": True, "default_category": "tech"},
                "git": {"auto_push": True, "branch": "develop"},
                "rate_limiting": {"search": 100, "create": 50, "process": 30},
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            config = load_config(config_path)

            # Check Ollama settings
            assert config.ollama_host == "http://custom:11434"
            assert config.ollama_timeout == 120
            assert config.embedding_model == "custom-model"

            # Check processing settings
            assert config.chunk_size == 2000
            assert config.chunk_overlap == 400

            # Check vector settings
            assert config.collection_name == "test_collection"
            assert config.chroma_db_path == "/custom/path"

            # Check MCP paths
            assert config.mcp.paths.documents_root == "/custom/docs"
            assert config.mcp.paths.documents_dir == "articles"

            # Check MCP search
            assert config.mcp.search.max_results == 50
            assert config.mcp.search.similarity_threshold == 0.8

            # Check MCP creation
            assert config.mcp.creation.auto_process is False
            assert config.mcp.creation.auto_commit is True
            assert config.mcp.creation.default_category == "tech"

            # Check MCP git
            assert config.mcp.git.auto_push is True
            assert config.mcp.git.branch == "develop"

            # Check MCP rate limiting
            assert config.mcp.rate_limiting.search == 100
            assert config.mcp.rate_limiting.create == 50
            assert config.mcp.rate_limiting.process == 30

        finally:
            config_path.unlink()

    def test_load_nonexistent_file(self) -> None:
        """Test loading with non-existent config file"""
        config = load_config(Path("/nonexistent/config.yaml"))

        # Should return default config
        assert config.ollama_host == "http://localhost:11434"
        assert isinstance(config.mcp, MCPConfig)

    def test_load_partial_config(self) -> None:
        """Test loading config with only some sections"""
        config_data = {
            "ollama": {"host": "http://custom:11434"},
            "mcp": {"search": {"max_results": 30}},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            config = load_config(config_path)

            # Should have custom values
            assert config.ollama_host == "http://custom:11434"
            assert config.mcp.search.max_results == 30

            # Should have defaults for missing values
            assert config.ollama_timeout == 60
            assert config.mcp.paths.documents_dir == "documents"

        finally:
            config_path.unlink()

    def test_from_file_class_method(self) -> None:
        """Test Config.from_file class method"""
        config_data = {"ollama": {"host": "http://test:11434"}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            config = Config.from_file(config_path)

            assert config.ollama_host == "http://test:11434"

        finally:
            config_path.unlink()
