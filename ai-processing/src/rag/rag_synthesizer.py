"""
PrismWeave RAG Synthesizer
Advanced Retrieval Augmented Generation for intelligent document synthesis
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from ..models.ollama_client import OllamaClient
from ..search.semantic_search import SemanticSearch, SearchResult
from ..utils.config_simplified import get_config


@dataclass
class RAGQuery:
    """Structured RAG query with context and parameters"""
    question: str
    context_types: Optional[List[str]] = field(default_factory=lambda: None)  # ['tech', 'research', 'tutorial']
    required_tags: Optional[List[str]] = field(default_factory=lambda: None)
    max_context_documents: int = 10
    synthesis_style: str = "comprehensive"  # 'brief', 'comprehensive', 'technical'
    include_sources: bool = True


@dataclass
class RAGResponse:
    """Structured RAG response with synthesis and provenance"""
    question: str
    answer: str
    sources: List[SearchResult]
    confidence_score: float
    synthesis_model: str
    context_document_count: int
    processing_time: float
    timestamp: datetime


class RAGSynthesizer:
    """Advanced RAG system for document synthesis and question answering"""

    def __init__(self):
        self.config = get_config()
        self.ollama_client: Optional[OllamaClient] = None
        self.search_engine: Optional[SemanticSearch] = None
        self.logger = logging.getLogger(__name__)

        # Synthesis prompts for different styles
        self.synthesis_prompts = {
            "brief": {
                "system": "You are a concise knowledge synthesizer. Provide brief, accurate answers based on the provided documents. Be direct and factual.",
                "template": """Based on the following documents, answer this question briefly: {question}

CONTEXT DOCUMENTS:
{context}

Instructions:
- Provide a concise, factual answer (2-3 sentences maximum)
- Only use information from the provided documents
- If the documents don't contain enough information, say so clearly
- Do not speculate or add information not in the documents

Answer:"""
            },

            "comprehensive": {
                "system": "You are an expert knowledge synthesizer. Analyze the provided documents and create comprehensive, well-structured answers that combine insights from multiple sources.",
                "template": """Based on the following documents, provide a comprehensive answer to this question: {question}

CONTEXT DOCUMENTS:
{context}

Instructions:
- Synthesize information from all relevant documents
- Create a well-structured, comprehensive response
- Include specific details and examples when available
- Identify patterns and connections across documents
- If conflicting information exists, acknowledge and explain it
- Use clear headings and bullet points for complex information
- Only use information from the provided documents

Comprehensive Answer:"""
            },

            "technical": {
                "system": "You are a technical expert who creates detailed, accurate technical documentation and explanations. Focus on implementation details, code examples, and precise technical information.",
                "template": """Based on the following technical documents, provide a detailed technical answer to: {question}

CONTEXT DOCUMENTS:
{context}

Instructions:
- Focus on technical details, implementation specifics, and code examples
- Include relevant APIs, commands, configuration details
- Explain technical concepts clearly with proper terminology
- Provide step-by-step guidance when applicable
- Include warnings about potential issues or limitations
- Reference specific versions, tools, or technologies mentioned
- Only use technical information from the provided documents

Technical Answer:"""
            }
        }

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()

    async def initialize(self) -> None:
        """Initialize RAG components"""
        try:
            self.logger.info("Initializing RAG Synthesizer...")

            # Initialize Ollama client
            self.ollama_client = OllamaClient()
            await self.ollama_client.__aenter__()

            # Initialize search engine
            self.search_engine = SemanticSearch()
            await self.search_engine.__aenter__()

            # Verify models are available
            await self._verify_models()

            self.logger.info("RAG Synthesizer initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize RAG Synthesizer: {e}")
            raise

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.search_engine:
            await self.search_engine.__aexit__(None, None, None)
        if self.ollama_client:
            await self.ollama_client.__aexit__(None, None, None)

    async def query(self, rag_query: RAGQuery) -> RAGResponse:
        """
        Process a RAG query and generate synthesized response

        Args:
            rag_query: Structured query with context and parameters

        Returns:
            RAGResponse with synthesized answer and sources
        """
        start_time = datetime.now()

        try:
            self.logger.info(f"Processing RAG query: {rag_query.question}")

            # Step 1: Retrieve relevant documents
            context_docs = await self._retrieve_context(rag_query)

            if not context_docs:
                return RAGResponse(
                    question=rag_query.question,
                    answer="I couldn't find relevant documents to answer your question. Please try rephrasing or check if documents on this topic exist in the knowledge base.",
                    sources=[],
                    confidence_score=0.0,
                    synthesis_model="none",
                    context_document_count=0,
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    timestamp=datetime.now()
                )

            # Step 2: Generate synthesized response
            answer, model_used, confidence = await self._synthesize_response(
                rag_query, context_docs
            )

            # Step 3: Create structured response
            response = RAGResponse(
                question=rag_query.question,
                answer=answer,
                sources=context_docs,
                confidence_score=confidence,
                synthesis_model=model_used,
                context_document_count=len(context_docs),
                processing_time=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now()
            )

            self.logger.info(f"RAG query completed in {response.processing_time:.2f}s")
            return response

        except Exception as e:
            self.logger.error(f"RAG query failed: {e}")
            return RAGResponse(
                question=rag_query.question,
                answer=f"An error occurred while processing your query: {str(e)}",
                sources=[],
                confidence_score=0.0,
                synthesis_model="error",
                context_document_count=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now()
            )

    async def _retrieve_context(self, rag_query: RAGQuery) -> List[SearchResult]:
        """Retrieve relevant documents for the query"""
        try:
            # Perform semantic search
            search_response = await self.search_engine.search(
                query=rag_query.question,
                max_results=rag_query.max_context_documents * 2  # Get extra for filtering
            )

            context_docs = search_response.results

            # Apply filters if specified
            if rag_query.context_types:
                context_docs = [
                    doc for doc in context_docs
                    if doc.metadata.get('category') in rag_query.context_types
                ]

            if rag_query.required_tags:
                context_docs = [
                    doc for doc in context_docs
                    if any(tag in doc.metadata.get('tags', []) for tag in rag_query.required_tags)
                ]

            # Limit to requested number
            context_docs = context_docs[:rag_query.max_context_documents]

            self.logger.info(f"Retrieved {len(context_docs)} context documents")
            return context_docs

        except Exception as e:
            self.logger.error(f"Failed to retrieve context: {e}")
            return []

    async def _synthesize_response(
        self,
        rag_query: RAGQuery,
        context_docs: List[SearchResult]
    ) -> Tuple[str, str, float]:
        """Generate synthesized response from context documents"""

        # Prepare context text
        context_text = self._prepare_context_text(context_docs)

        # Select appropriate model and prompt
        model_config = self.config.get_model_config('large')
        model_name = model_config['primary']

        prompt_config = self.synthesis_prompts.get(
            rag_query.synthesis_style,
            self.synthesis_prompts['comprehensive']
        )

        # Format prompt
        formatted_prompt = prompt_config['template'].format(
            question=rag_query.question,
            context=context_text
        )

        try:
            # Generate response
            result = await self.ollama_client.generate(
                model=model_name,
                prompt=formatted_prompt,
                system=prompt_config['system'],
                options={
                    'temperature': 0.1,  # Low temperature for factual accuracy
                    'top_p': 0.9,
                    'num_predict': 2000
                }
            )

            # Calculate confidence based on context quality
            confidence = self._calculate_confidence(context_docs, rag_query.question)

            return result.response.strip(), model_name, confidence

        except Exception as e:
            self.logger.error(f"Failed to synthesize response: {e}")
            return f"Error generating response: {str(e)}", model_name, 0.0

    def _prepare_context_text(self, context_docs: List[SearchResult]) -> str:
        """Prepare formatted context text from search results"""
        context_parts = []

        for i, doc in enumerate(context_docs, 1):
            doc_header = f"--- DOCUMENT {i}: {doc.title} ---"
            doc_metadata = f"Source: {doc.document_path}"
            if doc.metadata.get('url'):
                doc_metadata += f"\nOriginal URL: {doc.metadata['url']}"
            if doc.metadata.get('tags'):
                doc_metadata += f"\nTags: {', '.join(doc.metadata['tags'])}"

            # Get document content (truncate if very long)
            content = doc.snippet
            if len(content) > 2000:
                content = content[:2000] + "... [truncated]"

            context_parts.append(f"{doc_header}\n{doc_metadata}\n\nContent:\n{content}\n")

        return "\n".join(context_parts)

    def _calculate_confidence(self, context_docs: List[SearchResult], question: str) -> float:
        """Calculate confidence score based on context quality"""
        if not context_docs:
            return 0.0

        # Base confidence on similarity scores
        similarity_scores = [doc.similarity_score for doc in context_docs]
        avg_similarity = sum(similarity_scores) / len(similarity_scores)

        # Adjust for number of relevant documents
        doc_count_factor = min(len(context_docs) / 5.0, 1.0)  # Optimal around 5 docs

        # Adjust for content quality
        quality_scores = [
            doc.metadata.get('quality_score', 5.0) for doc in context_docs
        ]
        avg_quality = sum(quality_scores) / len(quality_scores)
        quality_factor = avg_quality / 10.0  # Normalize to 0-1

        # Combined confidence
        confidence = avg_similarity * 0.5 + doc_count_factor * 0.3 + quality_factor * 0.2
        return min(max(confidence, 0.0), 1.0)  # Clamp to 0-1

    async def _verify_models(self) -> None:
        """Verify required models are available"""
        model_config = self.config.get_model_config('large')
        primary_model = model_config['primary']

        if not await self.ollama_client.model_exists(primary_model):
            self.logger.warning(f"Primary model {primary_model} not found, checking fallback...")
            fallback_model = model_config['fallback']
            if not await self.ollama_client.model_exists(fallback_model):
                raise RuntimeError(f"Neither primary ({primary_model}) nor fallback ({fallback_model}) models are available")

    # Convenience methods for common query types

    async def ask_question(self, question: str, style: str = "comprehensive") -> RAGResponse:
        """Simple question asking interface"""
        query = RAGQuery(
            question=question,
            synthesis_style=style,
            max_context_documents=10
        )
        return await self.query(query)

    async def technical_query(self, question: str, technologies: List[str] = None) -> RAGResponse:
        """Technical question with technology filter"""
        query = RAGQuery(
            question=question,
            context_types=["tech", "tutorial", "reference"],
            required_tags=technologies or [],
            synthesis_style="technical",
            max_context_documents=8
        )
        return await self.query(query)

    async def research_synthesis(self, topic: str) -> RAGResponse:
        """Research-focused synthesis"""
        query = RAGQuery(
            question=f"Provide a comprehensive overview of research on: {topic}",
            context_types=["research", "reference"],
            synthesis_style="comprehensive",
            max_context_documents=15
        )
        return await self.query(query)

    async def quick_answer(self, question: str) -> RAGResponse:
        """Quick, brief answers"""
        query = RAGQuery(
            question=question,
            synthesis_style="brief",
            max_context_documents=5
        )
        return await self.query(query)


# Example usage functions
async def main():
    """Example usage of RAG Synthesizer"""
    async with RAGSynthesizer() as rag:

        # Example 1: General question
        response = await rag.ask_question(
            "What are the best practices for TypeScript development?"
        )
        print(f"Q: {response.question}")
        print(f"A: {response.answer}")
        print(f"Sources: {len(response.sources)} documents")
        print(f"Confidence: {response.confidence_score:.2f}")
        print("-" * 80)

        # Example 2: Technical query
        response = await rag.technical_query(
            "How do I implement RAG with Ollama?",
            technologies=["ai", "ollama", "python"]
        )
        print(f"Technical Q: {response.question}")
        print(f"Technical A: {response.answer}")
        print("-" * 80)

        # Example 3: Research synthesis
        response = await rag.research_synthesis("machine learning interpretability")
        print("Research Topic: machine learning interpretability")
        print(f"Research Overview: {response.answer}")


if __name__ == "__main__":
    asyncio.run(main())
