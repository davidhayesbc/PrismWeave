"""
Configuration management for PrismWeave AI processing
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class MCPPathsConfig:
    """MCP paths configuration"""

    documents_root: str = "../../PrismWeaveDocs"
    documents_dir: str = "documents"
    generated_dir: str = "generated"
    images_dir: str = "images"
    tech_dir: str = "tech"


@dataclass
class MCPSearchConfig:
    """MCP search configuration"""

    max_results: int = 20
    similarity_threshold: float = 0.6
    default_filters: dict = field(default_factory=dict)


@dataclass
class MCPCreationConfig:
    """MCP document creation configuration"""

    auto_process: bool = True
    auto_commit: bool = False
    default_category: str = "general"


@dataclass
class MCPGitConfig:
    """MCP git integration configuration"""

    auto_push: bool = False
    commit_message_template: str = "Add document: {title}"
    branch: str = "main"


@dataclass
class MCPRateLimitingConfig:
    """MCP rate limiting configuration"""

    search: int = 60
    create: int = 30
    process: int = 20


@dataclass
class MCPConfig:
    """MCP server configuration"""

    paths: MCPPathsConfig = field(default_factory=MCPPathsConfig)
    search: MCPSearchConfig = field(default_factory=MCPSearchConfig)
    creation: MCPCreationConfig = field(default_factory=MCPCreationConfig)
    git: MCPGitConfig = field(default_factory=MCPGitConfig)
    rate_limiting: MCPRateLimitingConfig = field(default_factory=MCPRateLimitingConfig)


@dataclass
class Config:
    """Configuration for PrismWeave document processing"""

    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    ollama_timeout: int = 60
    embedding_model: str = "nomic-embed-text:latest"

    # Document processing settings
    chunk_size: int = 1000  # Smaller chunks for web documents
    chunk_overlap: int = 200

    # ChromaDB settings
    chroma_db_path: str = "../../PrismWeaveDocs/.prismweave/chroma_db"
    collection_name: str = "documents"

    # MCP settings
    mcp: MCPConfig = field(default_factory=MCPConfig)

    def validate(self) -> list[str]:
        """Validate configuration and return any issues"""
        issues = []

        if not self.ollama_host:
            issues.append("Ollama host cannot be empty")

        if self.chunk_size <= 0:
            issues.append("Chunk size must be positive")

        if self.chunk_overlap >= self.chunk_size:
            issues.append("Chunk overlap must be less than chunk size")

        if not self.embedding_model:
            issues.append("Embedding model cannot be empty")

        # MCP validation
        if self.mcp.search.max_results <= 0:
            issues.append("MCP search max_results must be positive")

        if not 0 <= self.mcp.search.similarity_threshold <= 1:
            issues.append("MCP search similarity_threshold must be between 0 and 1")

        if self.mcp.rate_limiting.search <= 0:
            issues.append("MCP rate limiting search must be positive")

        return issues

    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from YAML file"""
        return load_config(config_path)


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from YAML file or use defaults"""

    if config_path is None:
        # Look for config.yaml in the ai-processing directory
        config_path = Path(__file__).parent.parent.parent / "config.yaml"

    if not config_path.exists():
        print(f"Config file not found at {config_path}, using defaults")
        return Config()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        # Extract relevant values with fallbacks to defaults
        config = Config()

        # Ollama settings
        if "ollama" in config_data:
            ollama_config = config_data["ollama"]
            config.ollama_host = ollama_config.get("host", config.ollama_host)
            config.ollama_timeout = ollama_config.get("timeout", config.ollama_timeout)

            if "models" in ollama_config:
                config.embedding_model = ollama_config["models"].get("embedding", config.embedding_model)

        # Processing settings
        if "processing" in config_data:
            processing_config = config_data["processing"]
            config.chunk_size = processing_config.get("chunk_size", config.chunk_size)
            config.chunk_overlap = processing_config.get("chunk_overlap", config.chunk_overlap)

        # Vector database settings
        if "vector" in config_data:
            vector_config = config_data["vector"]
            config.chroma_db_path = vector_config.get("persist_directory", config.chroma_db_path)
            config.collection_name = vector_config.get("collection_name", config.collection_name)

        # MCP settings
        if "mcp" in config_data:
            mcp_data = config_data["mcp"]

            # MCP Paths
            if "paths" in mcp_data:
                paths_data = mcp_data["paths"]
                config.mcp.paths = MCPPathsConfig(
                    documents_root=paths_data.get("documents_root", config.mcp.paths.documents_root),
                    documents_dir=paths_data.get("documents_dir", config.mcp.paths.documents_dir),
                    generated_dir=paths_data.get("generated_dir", config.mcp.paths.generated_dir),
                    images_dir=paths_data.get("images_dir", config.mcp.paths.images_dir),
                    tech_dir=paths_data.get("tech_dir", config.mcp.paths.tech_dir),
                )

            # MCP Search
            if "search" in mcp_data:
                search_data = mcp_data["search"]
                config.mcp.search = MCPSearchConfig(
                    max_results=search_data.get("max_results", config.mcp.search.max_results),
                    similarity_threshold=search_data.get(
                        "similarity_threshold", config.mcp.search.similarity_threshold
                    ),
                    default_filters=search_data.get("default_filters", config.mcp.search.default_filters),
                )

            # MCP Creation
            if "creation" in mcp_data:
                creation_data = mcp_data["creation"]
                config.mcp.creation = MCPCreationConfig(
                    auto_process=creation_data.get("auto_process", config.mcp.creation.auto_process),
                    auto_commit=creation_data.get("auto_commit", config.mcp.creation.auto_commit),
                    default_category=creation_data.get("default_category", config.mcp.creation.default_category),
                )

            # MCP Git
            if "git" in mcp_data:
                git_data = mcp_data["git"]
                config.mcp.git = MCPGitConfig(
                    auto_push=git_data.get("auto_push", config.mcp.git.auto_push),
                    commit_message_template=git_data.get(
                        "commit_message_template", config.mcp.git.commit_message_template
                    ),
                    branch=git_data.get("branch", config.mcp.git.branch),
                )

            # MCP Rate Limiting
            if "rate_limiting" in mcp_data:
                rate_data = mcp_data["rate_limiting"]
                config.mcp.rate_limiting = MCPRateLimitingConfig(
                    search=rate_data.get("search", config.mcp.rate_limiting.search),
                    create=rate_data.get("create", config.mcp.rate_limiting.create),
                    process=rate_data.get("process", config.mcp.rate_limiting.process),
                )

        return config

    except Exception as e:
        print(f"Error loading config from {config_path}: {e}")
        print("Using default configuration")
        return Config()
