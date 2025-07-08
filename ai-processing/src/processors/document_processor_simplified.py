"""
Simplified document processor for PrismWeave AI processing
Clean, straightforward document analysis without complex fallback mechanisms
"""

import asyncio
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

import frontmatter
import nltk
import textstat
from langdetect import detect

from ..models.ollama_client_simplified import OllamaClient
from ..utils.config_simplified import get_config, get_model_for_purpose

logger = logging.getLogger(__name__)

@dataclass 
class DocumentAnalysis:
    """Results of document analysis"""
    summary: str
    tags: List[str]
    category: str
    word_count: int
    reading_time: int
    language: str
    readability_score: float
    key_topics: List[str]
    confidence: float

class DocumentProcessor:
    """Simplified document processor for AI-powered analysis"""
    
    def __init__(self):
        self.config = get_config()
        self._ensure_nltk_data()
    
    def _ensure_nltk_data(self):
        """Ensure required NLTK data is downloaded"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            logger.info("Downloading NLTK punkt tokenizer...")
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Downloading NLTK stopwords...")
            nltk.download('stopwords', quiet=True)
    
    async def process_document(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> DocumentAnalysis:
        """
        Process a document and generate comprehensive analysis
        
        Args:
            content: Document content (markdown/text)
            metadata: Optional metadata about the document
            
        Returns:
            DocumentAnalysis with generated insights
        """
        logger.info(f"Processing document ({len(content)} chars)")
        
        # Validate content length
        if len(content.strip()) < self.config.processing.min_word_count:
            raise ValueError(f"Content too short (minimum {self.config.processing.min_word_count} words)")
        
        # Parse frontmatter if present
        if content.startswith('---'):
            fm_post = frontmatter.loads(content)
            text_content = fm_post.content
            existing_metadata = fm_post.metadata
        else:
            text_content = content
            existing_metadata = {}
        
        # Merge metadata
        combined_metadata = {**(metadata or {}), **existing_metadata}
        
        # Extract basic statistics
        word_count = len(text_content.split())
        reading_time = max(1, word_count // 200)  # ~200 words per minute
        
        # Detect language
        try:
            language = detect(text_content[:1000])  # Use first 1000 chars for detection
        except:
            language = 'en'  # Default to English
        
        # Calculate readability
        try:
            readability_score = textstat.flesch_reading_ease(text_content)
        except:
            readability_score = 50.0  # Default moderate score
        
        # Clean text for AI processing
        clean_text = self._clean_text_for_ai(text_content)
        
        # Use single Ollama client instance for all AI operations
        async with OllamaClient(
            host=self.config.ollama.host, 
            timeout=self.config.ollama.timeout
        ) as client:
            
            # Run AI analysis tasks
            summary_task = self._generate_summary(client, clean_text)
            tags_task = self._suggest_tags(client, clean_text, combined_metadata)
            category_task = self._categorize_document(client, clean_text, combined_metadata)
            topics_task = self._extract_key_topics(client, clean_text)
            
            # Execute all AI tasks concurrently
            try:
                summary, tags, category, key_topics = await asyncio.gather(
                    summary_task,
                    tags_task, 
                    category_task,
                    topics_task,
                    return_exceptions=True
                )
                
                # Handle any exceptions in results
                if isinstance(summary, Exception):
                    logger.error(f"Summary generation failed: {summary}")
                    summary = "Summary generation failed"
                
                if isinstance(tags, Exception):
                    logger.error(f"Tag generation failed: {tags}")
                    tags = []
                
                if isinstance(category, Exception):
                    logger.error(f"Categorization failed: {category}")
                    category = "uncategorized"
                
                if isinstance(key_topics, Exception):
                    logger.error(f"Topic extraction failed: {key_topics}")
                    key_topics = []
                
            except Exception as e:
                logger.error(f"AI processing failed: {e}")
                # Return basic analysis without AI insights
                summary = f"Document with {word_count} words"
                tags = []
                category = "uncategorized"
                key_topics = []
        
        # Calculate confidence based on successful AI operations
        successful_operations = sum([
            summary != "Summary generation failed",
            len(tags) > 0,
            category != "uncategorized",
            len(key_topics) > 0
        ])
        confidence = successful_operations / 4.0
        
        analysis = DocumentAnalysis(
            summary=summary,
            tags=tags[:self.config.processing.max_tags],  # Limit number of tags
            category=category,
            word_count=word_count,
            reading_time=reading_time,
            language=language,
            readability_score=readability_score,
            key_topics=key_topics,
            confidence=confidence
        )
        
        logger.info(f"Document analysis completed (confidence: {confidence:.2f})")
        return analysis
    
    def _clean_text_for_ai(self, text: str) -> str:
        """Clean text for AI processing"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove markdown syntax that might confuse AI
        text = re.sub(r'[#*`_\[\]()]', '', text)
        
        # Limit length for AI processing
        max_chars = 4000  # Leave room for prompts
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        return text.strip()
    
    async def _generate_summary(self, client: OllamaClient, text: str) -> str:
        """Generate document summary using AI"""
        model = get_model_for_purpose('medium')
        
        prompt = f"""Summarize the following text in 2-3 concise sentences. Focus on the main points and key information:

{text}

Summary:"""
        
        try:
            result = await asyncio.wait_for(
                client.generate(model=model, prompt=prompt),
                timeout=self.config.processing.summary_timeout
            )
            
            summary = result.response.strip()
            
            # Limit summary length
            if len(summary) > self.config.processing.max_summary_length:
                summary = summary[:self.config.processing.max_summary_length] + "..."
            
            logger.debug(f"Generated summary: {len(summary)} chars")
            return summary
            
        except asyncio.TimeoutError:
            logger.warning("Summary generation timed out")
            raise
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            raise
    
    async def _suggest_tags(self, client: OllamaClient, text: str, metadata: Dict[str, Any]) -> List[str]:
        """Generate relevant tags for the document"""
        model = get_model_for_purpose('small')
        
        # Include existing tags from metadata if available
        existing_tags = metadata.get('tags', [])
        context = f"Existing tags: {', '.join(existing_tags)}" if existing_tags else ""
        
        prompt = f"""Analyze the following text and suggest 5-8 relevant tags. Return only the tags separated by commas, no explanation.

{context}

Text: {text}

Tags:"""
        
        try:
            result = await asyncio.wait_for(
                client.generate(model=model, prompt=prompt),
                timeout=self.config.processing.tagging_timeout
            )
            
            # Parse tags from response
            tags_text = result.response.strip()
            tags = [tag.strip().lower() for tag in tags_text.split(',') if tag.strip()]
            
            # Combine with existing tags and remove duplicates
            all_tags = list(set(existing_tags + tags))
            
            logger.debug(f"Generated {len(tags)} new tags, total: {len(all_tags)}")
            return all_tags
            
        except asyncio.TimeoutError:
            logger.warning("Tag generation timed out")
            raise
        except Exception as e:
            logger.error(f"Tag generation failed: {e}")
            raise
    
    async def _categorize_document(self, client: OllamaClient, text: str, metadata: Dict[str, Any]) -> str:
        """Categorize the document into a main category"""
        model = get_model_for_purpose('small')
        
        # Standard categories for classification
        categories = [
            "news", "reference", "tutorial", "research", "tech", 
            "business", "personal", "entertainment", "education", "health"
        ]
        
        prompt = f"""Classify the following text into ONE of these categories: {', '.join(categories)}

Text: {text}

Category:"""
        
        try:
            result = await asyncio.wait_for(
                client.generate(model=model, prompt=prompt),
                timeout=self.config.processing.categorization_timeout
            )
            
            # Extract category from response
            category = result.response.strip().lower()
            
            # Validate category is in our list
            if category in categories:
                logger.debug(f"Classified as: {category}")
                return category
            else:
                # Try to find partial match
                for cat in categories:
                    if cat in category:
                        logger.debug(f"Classified as: {cat} (partial match)")
                        return cat
                
                logger.warning(f"Unknown category '{category}', using 'uncategorized'")
                return "uncategorized"
            
        except asyncio.TimeoutError:
            logger.warning("Categorization timed out")
            raise
        except Exception as e:
            logger.error(f"Categorization failed: {e}")
            raise
    
    async def _extract_key_topics(self, client: OllamaClient, text: str) -> List[str]:
        """Extract key topics/concepts from the document"""
        model = get_model_for_purpose('small')
        
        prompt = f"""Extract 3-5 key topics or main concepts from this text. Return only the topics separated by commas:

{text}

Key topics:"""
        
        try:
            result = await asyncio.wait_for(
                client.generate(model=model, prompt=prompt),
                timeout=self.config.processing.categorization_timeout
            )
            
            # Parse topics from response
            topics_text = result.response.strip()
            topics = [topic.strip() for topic in topics_text.split(',') if topic.strip()]
            
            logger.debug(f"Extracted {len(topics)} key topics")
            return topics[:5]  # Limit to 5 topics
            
        except asyncio.TimeoutError:
            logger.warning("Topic extraction timed out")
            raise
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            raise
    
    async def process_file(self, file_path: Path) -> Tuple[DocumentAnalysis, Dict[str, Any]]:
        """Process a markdown file and return analysis with metadata"""
        logger.info(f"Processing file: {file_path}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise IOError(f"Failed to read file {file_path}: {e}")
        
        # Basic file metadata
        file_metadata = {
            'filename': file_path.name,
            'filepath': str(file_path),
            'file_size': file_path.stat().st_size,
            'modified_time': datetime.fromtimestamp(file_path.stat().st_mtime)
        }
        
        # Process document
        analysis = await self.process_document(content, file_metadata)
        
        return analysis, file_metadata
    
    def create_enriched_frontmatter(self, analysis: DocumentAnalysis, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create enriched frontmatter from analysis results"""
        frontmatter_data = {
            'title': metadata.get('filename', 'Untitled'),
            'summary': analysis.summary,
            'tags': analysis.tags,
            'category': analysis.category,
            'language': analysis.language,
            'word_count': analysis.word_count,
            'reading_time': analysis.reading_time,
            'readability_score': analysis.readability_score,
            'key_topics': analysis.key_topics,
            'processed_at': datetime.now().isoformat(),
            'confidence': analysis.confidence
        }
        
        # Include original metadata
        frontmatter_data.update(metadata)
        
        return frontmatter_data
    
    async def process_batch(self, file_paths: List[Path]) -> List[Tuple[Path, DocumentAnalysis, Dict[str, Any]]]:
        """Process multiple files with controlled concurrency"""
        logger.info(f"Processing batch of {len(file_paths)} files")
        
        semaphore = asyncio.Semaphore(self.config.processing.max_concurrent)
        
        async def process_single(file_path: Path):
            async with semaphore:
                try:
                    analysis, metadata = await self.process_file(file_path)
                    return (file_path, analysis, metadata)
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")
                    return (file_path, None, {'error': str(e)})
        
        tasks = [process_single(path) for path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and failed processing
        successful_results = [
            result for result in results 
            if not isinstance(result, Exception) and result[1] is not None
        ]
        
        logger.info(f"Successfully processed {len(successful_results)}/{len(file_paths)} files")
        return successful_results
