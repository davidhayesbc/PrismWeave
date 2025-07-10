#!/usr/bin/env python3
"""
PrismWeave LangChain RAG Integration
Enhanced RAG system using LangChain for better retrieval and generation
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys

try:
    from langchain.schema import Document
    from langchain.vectorstores import Chroma
    from langchain.embeddings import OllamaEmbeddings
    from langchain.llms import Ollama
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.retrievers import EnsembleRetriever, MultiQueryRetriever
    from langchain.retrievers.document_compressors import LLMChainExtractor
    from langchain.retrievers import ContextualCompressionRetriever
    from langchain.prompts import PromptTemplate
    from langchain.schema.runnable import RunnablePassthrough
    from langchain.schema.output_parser import StrOutputParser
except ImportError as e:
    print(f"LangChain not installed. Install with: pip install langchain langchain-community")
    print(f"Error: {e}")
    sys.exit(1)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

try:
    from src.utils.config_simplified import get_config
    from src.search.semantic_search import SemanticSearch
except ImportError as e:
    print(f"PrismWeave modules not found: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)

class PrismWeaveLangChainRAG:
    """LangChain-enhanced RAG system for PrismWeave"""
    
    def __init__(self):
        self.config = get_config()
        self.llm: Optional[Ollama] = None
        self.embeddings: Optional[OllamaEmbeddings] = None
        self.vectorstore: Optional[Chroma] = None
        self.memory: Optional[ConversationBufferWindowMemory] = None
        self.qa_chain: Optional[ConversationalRetrievalChain] = None
        self.retrievers: Dict[str, Any] = {}
        
    async def initialize(self) -> None:
        """Initialize LangChain components"""
        try:
            logger.info("Initializing LangChain RAG system...")
            
            # Initialize Ollama LLM
            self.llm = Ollama(
                base_url=self.config.ollama.host,
                model=self.config.ollama.models.get('large', 'llama3.1:8b'),
                temperature=0.1
            )
            
            # Initialize Ollama embeddings
            self.embeddings = OllamaEmbeddings(
                base_url=self.config.ollama.host,
                model=self.config.ollama.models.get('embedding', 'nomic-embed-text')
            )
            
            # Initialize vector store (connect to existing Chroma DB)
            persist_directory = self.config.vector.persist_directory
            if not Path(persist_directory).is_absolute():
                persist_directory = str(Path.cwd() / persist_directory)
                
            self.vectorstore = Chroma(
                collection_name=self.config.vector.collection_name,
                embedding_function=self.embeddings,
                persist_directory=persist_directory
            )
            
            # Initialize conversation memory
            self.memory = ConversationBufferWindowMemory(
                k=5,  # Keep last 5 exchanges
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            
            # Setup advanced retrievers
            await self._setup_retrievers()
            
            # Initialize QA chains
            await self._setup_qa_chains()
            
            logger.info("LangChain RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain RAG: {e}")
            raise
    
    async def _setup_retrievers(self) -> None:
        """Setup various retrieval strategies"""
        
        # Basic similarity retriever
        self.retrievers['similarity'] = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.config.vector.max_results}
        )
        
        # Multi-query retriever (generates multiple query variations)
        self.retrievers['multi_query'] = MultiQueryRetriever.from_llm(
            retriever=self.retrievers['similarity'],
            llm=self.llm
        )
        
        # Ensemble retriever (combines multiple strategies)
        self.retrievers['ensemble'] = EnsembleRetriever(
            retrievers=[self.retrievers['similarity']],
            weights=[1.0]
        )
        
        # Contextual compression retriever (filters and compresses results)
        compressor = LLMChainExtractor.from_llm(self.llm)
        self.retrievers['compressed'] = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=self.retrievers['similarity']
        )
    
    async def _setup_qa_chains(self) -> None:
        """Setup QA chains with different strategies"""
        
        # Conversational RAG chain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retrievers['multi_query'],
            memory=self.memory,
            return_source_documents=True,
            verbose=True
        )
        
        # Custom prompt templates for different styles
        self.prompt_templates = {
            'comprehensive': PromptTemplate(
                input_variables=["context", "question"],
                template="""Use the following pieces of context to answer the question at the end. 
                If you don't know the answer, just say that you don't know, don't try to make up an answer.
                Provide a comprehensive, well-structured answer that synthesizes information from multiple sources.
                Include specific details and examples when available.

                Context:
                {context}

                Question: {question}
                
                Comprehensive Answer:"""
            ),
            
            'brief': PromptTemplate(
                input_variables=["context", "question"],
                template="""Use the following context to provide a brief, direct answer to the question.
                Be concise and factual. Maximum 2-3 sentences.

                Context:
                {context}

                Question: {question}
                
                Brief Answer:"""
            ),
            
            'technical': PromptTemplate(
                input_variables=["context", "question"], 
                template="""Use the following technical documentation to provide a detailed technical answer.
                Include implementation details, code examples, API references, and step-by-step guidance when applicable.
                Focus on practical, actionable technical information.

                Context:
                {context}

                Question: {question}
                
                Technical Answer:"""
            )
        }
    
    async def query(
        self, 
        question: str, 
        style: str = "comprehensive",
        retriever_strategy: str = "multi_query",
        use_conversation_memory: bool = True
    ) -> Dict[str, Any]:
        """
        Query the RAG system with LangChain enhancements
        
        Args:
            question: The question to ask
            style: Response style (comprehensive, brief, technical)
            retriever_strategy: Which retriever to use
            use_conversation_memory: Whether to use conversation context
            
        Returns:
            Dict with answer, sources, and metadata
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Processing LangChain RAG query: {question}")
            
            if use_conversation_memory and self.qa_chain:
                # Use conversational chain with memory
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.qa_chain({"question": question})
                )
                
                answer = result["answer"]
                source_documents = result.get("source_documents", [])
                
            else:
                # Use custom chain without conversation memory
                retriever = self.retrievers.get(retriever_strategy, self.retrievers['similarity'])
                prompt = self.prompt_templates.get(style, self.prompt_templates['comprehensive'])
                
                # Create custom chain
                def format_docs(docs):
                    return "\n\n".join([doc.page_content for doc in docs])
                
                rag_chain = (
                    {"context": retriever | format_docs, "question": RunnablePassthrough()}
                    | prompt
                    | self.llm
                    | StrOutputParser()
                )
                
                # Get answer and source documents separately
                answer = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: rag_chain.invoke(question)
                )
                
                source_documents = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: retriever.get_relevant_documents(question)
                )
            
            # Process source documents
            sources = []
            for doc in source_documents[:5]:  # Limit to top 5
                source_info = {
                    "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                    "metadata": doc.metadata,
                    "title": doc.metadata.get('title', 'Unknown'),
                    "document_path": doc.metadata.get('source', 'Unknown')
                }
                sources.append(source_info)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "question": question,
                "answer": answer,
                "sources": sources,
                "source_count": len(source_documents),
                "processing_time": processing_time,
                "retriever_strategy": retriever_strategy,
                "style": style,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"LangChain RAG query failed: {e}")
            return {
                "question": question,
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "source_count": 0,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def ask_with_conversation(self, question: str) -> Dict[str, Any]:
        """Ask a question with conversation memory"""
        return await self.query(question, use_conversation_memory=True)
    
    async def technical_query(self, question: str) -> Dict[str, Any]:
        """Technical query with compressed retrieval"""
        return await self.query(
            question,
            style="technical",
            retriever_strategy="compressed"
        )
    
    async def research_synthesis(self, topic: str) -> Dict[str, Any]:
        """Research synthesis using ensemble retriever"""
        question = f"Provide a comprehensive overview of research on: {topic}"
        return await self.query(
            question,
            style="comprehensive", 
            retriever_strategy="ensemble"
        )
    
    async def clear_conversation(self) -> None:
        """Clear conversation memory"""
        if self.memory:
            self.memory.clear()
    
    async def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        if not self.memory:
            return []
        
        history = []
        if hasattr(self.memory, 'chat_memory') and hasattr(self.memory.chat_memory, 'messages'):
            for message in self.memory.chat_memory.messages:
                history.append({
                    "type": message.__class__.__name__,
                    "content": message.content
                })
        return history
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add new documents to the vector store"""
        try:
            docs = []
            for doc_data in documents:
                doc = Document(
                    page_content=doc_data['content'],
                    metadata=doc_data.get('metadata', {})
                )
                docs.append(doc)
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.vectorstore.add_documents(docs)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
    async def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Direct similarity search"""
        try:
            docs = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.vectorstore.similarity_search(query, k=k)
            )
            
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "title": doc.metadata.get('title', 'Unknown')
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            if self.memory:
                self.memory.clear()
            logger.info("LangChain RAG cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# Context manager support
class LangChainRAGContext:
    """Async context manager for LangChain RAG"""
    
    def __init__(self):
        self.rag = PrismWeaveLangChainRAG()
    
    async def __aenter__(self):
        await self.rag.initialize()
        return self.rag
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rag.cleanup()


# Example usage
async def main():
    """Example usage of LangChain RAG"""
    async with LangChainRAGContext() as rag:
        
        # Example 1: Conversational query
        print("=== Conversational Query ===")
        response = await rag.ask_with_conversation("What are TypeScript interfaces?")
        print(f"Q: {response['question']}")
        print(f"A: {response['answer']}")
        print(f"Sources: {response['source_count']}")
        print()
        
        # Follow-up question (uses conversation memory)
        response = await rag.ask_with_conversation("Can you show me an example?")
        print(f"Follow-up Q: {response['question']}")
        print(f"Follow-up A: {response['answer']}")
        print()
        
        # Example 2: Technical query with compression
        print("=== Technical Query ===")
        response = await rag.technical_query("How do I implement async/await in TypeScript?")
        print(f"Technical Q: {response['question']}")
        print(f"Technical A: {response['answer']}")
        print()
        
        # Example 3: Research synthesis
        print("=== Research Synthesis ===")
        response = await rag.research_synthesis("RAG systems")
        print(f"Research: {response['answer']}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
