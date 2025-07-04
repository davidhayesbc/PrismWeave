"""
Document processor for PrismWeave AI processing
Handles document analysis, summarization, tagging, and categorization
"""

import os
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
import re
import hashlib

try:
    import frontmatter
    import markdown
    from bs4 import BeautifulSoup
    import nltk
    import textstat
    from langdetect import detect
except ImportError:
    # Handle missing dependencies gracefully
    frontmatter = None
    markdown = None
    BeautifulSoup = None
    nltk = None
    textstat = None
    detect = None

from ..models.ollama_client import OllamaClient
from ..utils.config import get_config

logger = logging.getLogger(__name__)

@dataclass
class DocumentMetadata:
    """Document metadata structure"""
    title: str
    source_url: str
    domain: str
    captured_date: str
    author: Optional[str] = None
    tags: List[str] = None
    summary: str = ""
    category: str = "unsorted"
    quality_score: float = 0.0
    word_count: int = 0
    reading_time: int = 0
    language: str = "en"
    difficulty: str = "unknown"
    content_type: str = "article"
    last_processed: Optional[str] = None
    processing_version: str = "1.0"

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class ProcessingResult:
    """Result of document processing"""
    success: bool
    document_path: str
    metadata: Optional[DocumentMetadata] = None
    generated_summary: str = ""
    suggested_tags: List[str] = None
    suggested_category: str = ""
    quality_score: float = 0.0
    processing_time: float = 0.0
    error: Optional[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.suggested_tags is None:
            self.suggested_tags = []
        if self.warnings is None:
            self.warnings = []

class DocumentProcessor:
    """Main document processor for AI analysis"""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.ollama_client = OllamaClient(
            host=self.config.ollama.host,
            timeout=self.config.ollama.timeout
        )
        
        # Processing statistics
        self.stats = {
            "processed_count": 0,
            "error_count": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.ollama_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.ollama_client.__aexit__(exc_type, exc_val, exc_tb)
    
    def _extract_content_from_markdown(self, file_path: Path) -> Tuple[DocumentMetadata, str]:
        """Extract frontmatter and content from markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if frontmatter:
                    post = frontmatter.load(f)
                    content = post.content
                    metadata_dict = post.metadata
                else:
                    # Fallback parsing
                    content = f.read()
                    metadata_dict = {}
                    # Simple frontmatter extraction
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            content = parts[2].strip()
            
            # Create metadata object
            metadata = DocumentMetadata(
                title=metadata_dict.get('title', file_path.stem),
                source_url=metadata_dict.get('url', metadata_dict.get('source_url', '')),
                domain=metadata_dict.get('domain', ''),
                captured_date=metadata_dict.get('captured_date', metadata_dict.get('date', '')),
                author=metadata_dict.get('author'),
                tags=metadata_dict.get('tags', []),
                summary=metadata_dict.get('summary', ''),
                category=metadata_dict.get('category', 'unsorted'),
                quality_score=float(metadata_dict.get('quality_score', 0.0)),
                last_processed=metadata_dict.get('last_processed')
            )
            
            return metadata, content
            
        except Exception as e:
            logger.error(f"Failed to extract content from {file_path}: {e}")
            # Return minimal metadata
            metadata = DocumentMetadata(
                title=file_path.stem,
                source_url="",
                domain="",
                captured_date=""
            )
            return metadata, ""
    
    def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure and extract basic metrics"""
        analysis = {
            "word_count": 0,
            "paragraph_count": 0,
            "code_block_count": 0,
            "link_count": 0,
            "image_count": 0,
            "header_count": 0,
            "reading_time": 0,
            "complexity_score": 0.0,
            "has_code": False,
            "has_technical_terms": False
        }
        
        if not content:
            return analysis
        
        # Basic text metrics
        words = content.split()
        analysis["word_count"] = len(words)
        analysis["reading_time"] = max(1, analysis["word_count"] // 200)  # ~200 WPM
        
        # Count markdown elements
        analysis["paragraph_count"] = len([p for p in content.split('\n\n') if p.strip()])
        analysis["code_block_count"] = content.count('```')
        analysis["link_count"] = content.count('](')
        analysis["image_count"] = content.count('![')
        analysis["header_count"] = len(re.findall(r'^#+\s', content, re.MULTILINE))
        
        # Technical content detection
        analysis["has_code"] = '```' in content or '`' in content
        
        technical_terms = [
            'api', 'framework', 'library', 'function', 'class', 'method',
            'algorithm', 'database', 'server', 'client', 'protocol',
            'javascript', 'python', 'java', 'react', 'vue', 'angular'
        ]
        content_lower = content.lower()
        analysis["has_technical_terms"] = any(term in content_lower for term in technical_terms)
        
        # Complexity scoring using textstat if available
        if textstat:
            try:
                analysis["complexity_score"] = textstat.flesch_reading_ease(content)
            except:
                analysis["complexity_score"] = 50.0  # Default moderate complexity
        
        return analysis
    
    async def _generate_summary(self, content: str, title: str) -> str:
        """Generate document summary using LLM"""
        if not content.strip():
            return ""
        
        # Use small model for quick summarization
        model_config = self.config.get_model_config('small')
        model = model_config.get('primary', 'phi3:mini')
        
        # Truncate content if too long
        max_content = self.config.processing.max_content_length
        if len(content) > max_content:
            content = content[:max_content] + "..."
        
        system_prompt = """You are a document summarization expert. Create a concise, informative summary that:
1. Captures the main points and key insights
2. Is 2-3 sentences long
3. Uses clear, professional language
4. Highlights the most valuable information for future reference"""
        
        user_prompt = f"""Title: {title}

Content:
{content}

Please provide a concise summary of this document:"""
        
        try:
            result = await self.ollama_client.generate(
                model=model,
                prompt=user_prompt,
                system=system_prompt
            )
            return result.response.strip() if hasattr(result, 'response') else ""
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return ""
    
    async def _suggest_tags(self, content: str, title: str, existing_tags: List[str]) -> List[str]:
        """Suggest relevant tags for the document"""
        if not content.strip():
            return existing_tags
        
        model_config = self.config.get_model_config('small')
        model = model_config.get('primary', 'phi3:mini')
        
        # Get predefined tags from config
        tech_tags = self.config.get('taxonomy', {}).get('tech_tags', [])
        
        system_prompt = f"""You are a document tagging expert. Suggest 3-7 relevant tags for this document.

Available technical tags: {', '.join(tech_tags)}

Rules:
1. Use existing tags when appropriate
2. Suggest new tags for concepts not covered
3. Focus on: technologies, concepts, methodologies, domains
4. Return only a comma-separated list of tags
5. No explanations or additional text"""
        
        user_prompt = f"""Title: {title}

Existing tags: {', '.join(existing_tags) if existing_tags else 'None'}

Content sample:
{content[:1000]}...

Suggested tags:"""
        
        try:
            result = await self.ollama_client.generate(
                model=model,
                prompt=user_prompt,
                system=system_prompt
            )
            
            if hasattr(result, 'response'):
                # Parse comma-separated tags
                suggested = [tag.strip() for tag in result.response.split(',')]
                suggested = [tag for tag in suggested if tag and len(tag) > 1]
                
                # Combine with existing tags, remove duplicates
                all_tags = list(set(existing_tags + suggested))
                return all_tags[:10]  # Limit to 10 tags
            
        except Exception as e:
            logger.error(f"Failed to suggest tags: {e}")
        
        return existing_tags
    
    async def _categorize_document(self, content: str, title: str, tags: List[str]) -> str:
        """Categorize document into appropriate folder"""
        if not content.strip():
            return "unsorted"
        
        model_config = self.config.get_model_config('small')
        model = model_config.get('primary', 'phi3:mini')
        
        categories = self.config.get('taxonomy', {}).get('categories', [
            'tech', 'research', 'business', 'tutorial', 'reference', 'news', 'opinion'
        ])
        
        system_prompt = f"""You are a document categorization expert. Classify this document into ONE of these categories:

{', '.join(categories)}

Guidelines:
- tech: Programming, software development, technical tutorials
- research: Academic papers, studies, analysis, data science
- business: Business strategy, management, finance, marketing  
- tutorial: Step-by-step guides, how-to articles
- reference: Documentation, specifications, reference materials
- news: Current events, announcements, industry news
- opinion: Opinion pieces, blogs, personal perspectives

Return only the category name, nothing else."""
        
        user_prompt = f"""Title: {title}

Tags: {', '.join(tags)}

Content sample:
{content[:800]}...

Category:"""
        
        try:
            result = await self.ollama_client.generate(
                model=model,
                prompt=user_prompt,
                system=system_prompt
            )
            
            if hasattr(result, 'response'):
                category = result.response.strip().lower()
                if category in categories:
                    return category
            
        except Exception as e:
            logger.error(f"Failed to categorize document: {e}")
        
        # Fallback categorization based on tags
        tag_str = ' '.join(tags).lower()
        if any(term in tag_str for term in ['programming', 'code', 'development', 'software']):
            return 'tech'
        elif any(term in tag_str for term in ['research', 'study', 'analysis', 'data']):
            return 'research'
        elif any(term in tag_str for term in ['business', 'strategy', 'management']):
            return 'business'
        elif any(term in tag_str for term in ['tutorial', 'how-to', 'guide']):
            return 'tutorial'
        
        return 'unsorted'
    
    def _calculate_quality_score(self, content: str, metadata: DocumentMetadata, analysis: Dict[str, Any]) -> float:
        """Calculate document quality score (0-10)"""
        score = 5.0  # Base score
        
        # Content length scoring
        word_count = analysis["word_count"]
        if word_count > 1000:
            score += 2.0
        elif word_count > 500:
            score += 1.0
        elif word_count < 100:
            score -= 2.0
        
        # Structure scoring
        if analysis["header_count"] > 0:
            score += 0.5
        if analysis["paragraph_count"] > 3:
            score += 0.5
        
        # Technical content bonus
        if analysis["has_code"]:
            score += 1.0
        if analysis["has_technical_terms"]:
            score += 0.5
        
        # Metadata completeness
        if metadata.source_url:
            score += 0.5
        if metadata.author:
            score += 0.5
        if len(metadata.tags) > 2:
            score += 0.5
        
        # Readability (if textstat available)
        if analysis.get("complexity_score", 0) > 0:
            complexity = analysis["complexity_score"]
            if 30 <= complexity <= 70:  # Good readability range
                score += 1.0
        
        return min(10.0, max(0.0, score))
    
    async def process_document(self, file_path: Path) -> ProcessingResult:
        """Process a single document with AI analysis"""
        start_time = time.time()
        
        try:
            # Extract content and metadata
            metadata, content = self._extract_content_from_markdown(file_path)
            
            if not content.strip():
                return ProcessingResult(
                    success=False,
                    document_path=str(file_path),
                    error="Empty or invalid document content"
                )
            
            # Analyze content structure
            analysis = self._analyze_content_structure(content)
            
            # Update basic metadata
            metadata.word_count = analysis["word_count"]
            metadata.reading_time = analysis["reading_time"]
            
            # Detect language if possible
            if detect:
                try:
                    metadata.language = detect(content[:1000])
                except:
                    metadata.language = "en"
            
            # AI-powered analysis
            tasks = []
            
            # Generate summary
            summary_task = self._generate_summary(content, metadata.title)
            tasks.append(("summary", summary_task))
            
            # Suggest tags
            tags_task = self._suggest_tags(content, metadata.title, metadata.tags)
            tasks.append(("tags", tags_task))
            
            # Execute AI tasks concurrently
            results = {}
            for task_name, task in tasks:
                try:
                    results[task_name] = await task
                except Exception as e:
                    logger.error(f"Task {task_name} failed: {e}")
                    results[task_name] = None
            
            # Process results
            generated_summary = results.get("summary", "")
            suggested_tags = results.get("tags", metadata.tags)
            
            # Categorize document
            suggested_category = await self._categorize_document(
                content, metadata.title, suggested_tags
            )
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(content, metadata, analysis)
            
            # Update metadata
            metadata.summary = generated_summary or metadata.summary
            metadata.tags = suggested_tags
            metadata.category = suggested_category
            metadata.quality_score = quality_score
            metadata.last_processed = time.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self.stats["processed_count"] += 1
            self.stats["total_processing_time"] += processing_time
            self.stats["average_processing_time"] = (
                self.stats["total_processing_time"] / self.stats["processed_count"]
            )
            
            return ProcessingResult(
                success=True,
                document_path=str(file_path),
                metadata=metadata,
                generated_summary=generated_summary,
                suggested_tags=suggested_tags,
                suggested_category=suggested_category,
                quality_score=quality_score,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.stats["error_count"] += 1
            logger.error(f"Failed to process document {file_path}: {e}")
            
            return ProcessingResult(
                success=False,
                document_path=str(file_path),
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    async def process_batch(self, file_paths: List[Path]) -> List[ProcessingResult]:
        """Process multiple documents in batch"""
        batch_size = self.config.processing.batch_size
        results = []
        
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            batch_tasks = [self.process_document(path) for path in batch]
            
            try:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"Batch processing error: {result}")
                        results.append(ProcessingResult(
                            success=False,
                            document_path="unknown",
                            error=str(result)
                        ))
                    else:
                        results.append(result)
            
            except Exception as e:
                logger.error(f"Batch processing failed: {e}")
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return self.stats.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on processing components"""
        health = {
            "processor_ready": True,
            "ollama_available": False,
            "models_available": [],
            "config_loaded": bool(self.config),
            "statistics": self.get_statistics()
        }
        
        try:
            health["ollama_available"] = await self.ollama_client.is_available()
            
            if health["ollama_available"]:
                models = await self.ollama_client.list_models()
                health["models_available"] = [model.name for model in models]
        
        except Exception as e:
            health["error"] = str(e)
            health["processor_ready"] = False
        
        return health
