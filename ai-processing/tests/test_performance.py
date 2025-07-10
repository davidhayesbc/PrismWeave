"""
Performance benchmarks for PrismWeave AI processing components
"""

import pytest
import asyncio
import time
import psutil
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock
from typing import List, Dict, Any
import statistics

import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.utils.config_simplified import Config
from src.models.ollama_client import OllamaClient
from src.processors.langchain_document_processor import LangChainDocumentProcessor
from .test_data import SAMPLE_DOCUMENTS, PERFORMANCE_TEST_DATA


class PerformanceBenchmark:
    """Performance benchmark utility"""
    
    def __init__(self):
        self.results: Dict[str, List[float]] = {}
        self.memory_usage: Dict[str, List[float]] = {}
    
    def start_benchmark(self, test_name: str):
        """Start timing a benchmark"""
        self.start_time = time.perf_counter()
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.test_name = test_name
    
    def end_benchmark(self):
        """End timing and record results"""
        end_time = time.perf_counter()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        duration = end_time - self.start_time
        memory_delta = end_memory - self.start_memory
        
        if self.test_name not in self.results:
            self.results[self.test_name] = []
            self.memory_usage[self.test_name] = []
        
        self.results[self.test_name].append(duration)
        self.memory_usage[self.test_name].append(memory_delta)
        
        return duration, memory_delta
    
    def get_stats(self, test_name: str) -> Dict[str, float]:
        """Get statistics for a test"""
        if test_name not in self.results:
            return {}
        
        times = self.results[test_name]
        memory = self.memory_usage[test_name]
        
        return {
            'time_mean': statistics.mean(times),
            'time_median': statistics.median(times),
            'time_std': statistics.stdev(times) if len(times) > 1 else 0,
            'time_min': min(times),
            'time_max': max(times),
            'memory_mean': statistics.mean(memory),
            'memory_median': statistics.median(memory),
            'memory_std': statistics.stdev(memory) if len(memory) > 1 else 0,
            'runs': len(times)
        }
    
    def print_results(self):
        """Print benchmark results"""
        print("\n" + "="*80)
        print("PERFORMANCE BENCHMARK RESULTS")
        print("="*80)
        
        for test_name in sorted(self.results.keys()):
            stats = self.get_stats(test_name)
            print(f"\n{test_name}:")
            print(f"  Time (seconds):")
            print(f"    Mean: {stats['time_mean']:.3f}s")
            print(f"    Median: {stats['time_median']:.3f}s")
            print(f"    Std Dev: {stats['time_std']:.3f}s")
            print(f"    Min: {stats['time_min']:.3f}s")
            print(f"    Max: {stats['time_max']:.3f}s")
            print(f"  Memory (MB):")
            print(f"    Mean: {stats['memory_mean']:.2f} MB")
            print(f"    Median: {stats['memory_median']:.2f} MB")
            print(f"    Std Dev: {stats['memory_std']:.2f} MB")
            print(f"  Runs: {stats['runs']}")


@pytest.fixture
def benchmark():
    """Performance benchmark fixture"""
    return PerformanceBenchmark()


@pytest.fixture
def performance_config():
    """Configuration optimized for performance testing"""
    config = Config(
        ollama={
            "host": "http://localhost:11434",
            "timeout": 30,
            "models": {
                "large": "test-model",
                "medium": "test-model", 
                "small": "test-model",
                "embedding": "test-embedding"
            }
        },
        processing={
            "max_concurrent": 4,  # Higher concurrency for performance
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "min_chunk_size": 100,
            "summary_timeout": 60,
            "tagging_timeout": 30,
            "categorization_timeout": 15,
            "min_word_count": 50,
            "max_word_count": 100000,  # Higher limit
            "max_summary_length": 500,
            "max_tags": 10
        },
        vector={
            "collection_name": "perf_test_documents",
            "persist_directory": "./perf_test_chroma_db",
            "embedding_function": "sentence-transformers",
            "max_results": 20,  # Higher limit
            "similarity_threshold": 0.7
        },
        log_level="WARNING"  # Reduce logging overhead
    )
    return config


@pytest.fixture
def fast_mock_ollama_client():
    """Fast mock Ollama client for performance testing"""
    client = AsyncMock(spec=OllamaClient)
    
    # Simulate fast responses
    async def fast_generate(*args, **kwargs):
        await asyncio.sleep(0.001)  # Minimal delay
        return {
            "response": "Fast generated response",
            "done": True,
            "total_duration": 1000000,
            "load_duration": 100000,
            "prompt_eval_count": 5,
            "eval_count": 10
        }
    client.generate.side_effect = fast_generate
    
    async def fast_embed(*args, **kwargs):
        await asyncio.sleep(0.001)  # Minimal delay
        text = args[0] if args else kwargs.get('prompt', '')
        embedding = [hash(text + str(i)) % 100 / 100.0 for i in range(384)]
        return {"embedding": embedding}
    client.embed.side_effect = fast_embed
    
    client.health_check.return_value = True
    
    return client


class TestConfigPerformance:
    """Test configuration system performance"""
    
    def test_config_loading_performance(self, benchmark):
        """Benchmark configuration loading"""
        # Create test config file
        import yaml
        config_data = {
            "ollama": {"host": "http://localhost:11434", "timeout": 30},
            "processing": {"chunk_size": 1000, "max_concurrent": 3},
            "vector": {"collection_name": "test"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_file = f.name
        
        try:
            # Benchmark multiple loads
            for i in range(10):
                benchmark.start_benchmark(f"config_loading_run_{i}")
                config = Config.load_from_file(config_file)
                benchmark.end_benchmark()
                assert config is not None
            
            # Test statistics
            stats = benchmark.get_stats("config_loading_run_0")
            print(f"Config loading time: {stats['time_mean']:.4f}s")
            
            # Should load quickly (< 100ms)
            assert stats['time_mean'] < 0.1
            
        finally:
            Path(config_file).unlink()
    
    def test_config_validation_performance(self, benchmark, performance_config):
        """Benchmark configuration validation"""
        for i in range(5):
            benchmark.start_benchmark(f"config_validation_run_{i}")
            
            # Validate all config sections
            assert performance_config.ollama.host.startswith("http")
            assert performance_config.processing.chunk_size > 0
            assert performance_config.vector.collection_name
            
            benchmark.end_benchmark()
        
        stats = benchmark.get_stats("config_validation_run_0")
        print(f"Config validation time: {stats['time_mean']:.6f}s")
        
        # Validation should be very fast (< 1ms)
        assert stats['time_mean'] < 0.001


class TestOllamaClientPerformance:
    """Test Ollama client performance"""
    
    @pytest.mark.asyncio
    async def test_generation_performance(self, benchmark, performance_config, fast_mock_ollama_client):
        """Benchmark text generation performance"""
        
        test_prompts = [
            "Summarize this document",
            "Extract key topics from this text",
            "Generate tags for this content",
            "Categorize this document",
            "Analyze the sentiment of this text"
        ]
        
        for i, prompt in enumerate(test_prompts):
            benchmark.start_benchmark(f"generation_run_{i}")
            
            response = await fast_mock_ollama_client.generate(
                model="test-model",
                prompt=prompt,
                max_tokens=100
            )
            
            benchmark.end_benchmark()
            
            assert response is not None
            assert "response" in response
        
        # Check average performance
        stats = benchmark.get_stats("generation_run_0")
        print(f"Generation time: {stats['time_mean']:.4f}s")
        
        # With mocked client, should be very fast
        assert stats['time_mean'] < 0.1
    
    @pytest.mark.asyncio
    async def test_embedding_performance(self, benchmark, performance_config, fast_mock_ollama_client):
        """Benchmark embedding generation performance"""
        
        test_texts = [
            "Short text for embedding",
            "Medium length text that contains more content for embedding generation testing",
            "This is a longer text sample that will be used to test the performance of embedding generation with more substantial content that might be typical in document processing scenarios",
            "Very short",
            "Another medium-length piece of text for comprehensive embedding performance testing"
        ]
        
        for i, text in enumerate(test_texts):
            benchmark.start_benchmark(f"embedding_run_{i}")
            
            response = await fast_mock_ollama_client.embed(
                model="test-embedding",
                prompt=text
            )
            
            benchmark.end_benchmark()
            
            assert response is not None
            assert "embedding" in response
            assert len(response["embedding"]) > 0
        
        stats = benchmark.get_stats("embedding_run_0")
        print(f"Embedding time: {stats['time_mean']:.4f}s")
        
        # Should be fast with mocked client
        assert stats['time_mean'] < 0.1
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_performance(self, benchmark, performance_config, fast_mock_ollama_client):
        """Benchmark concurrent Ollama operations"""
        
        async def mixed_operations():
            """Mix of generation and embedding operations"""
            tasks = []
            
            # Add generation tasks
            for i in range(3):
                tasks.append(fast_mock_ollama_client.generate(
                    model="test-model",
                    prompt=f"Test prompt {i}",
                    max_tokens=50
                ))
            
            # Add embedding tasks
            for i in range(3):
                tasks.append(fast_mock_ollama_client.embed(
                    model="test-embedding",
                    prompt=f"Test text for embedding {i}"
                ))
            
            return await asyncio.gather(*tasks)
        
        # Benchmark concurrent operations
        for i in range(3):
            benchmark.start_benchmark(f"concurrent_ops_run_{i}")
            
            results = await mixed_operations()
            
            benchmark.end_benchmark()
            
            assert len(results) == 6  # 3 generations + 3 embeddings
        
        stats = benchmark.get_stats("concurrent_ops_run_0")
        print(f"Concurrent operations time: {stats['time_mean']:.4f}s")
        
        # Concurrent operations should benefit from parallelism
        assert stats['time_mean'] < 0.5


class TestDocumentProcessorPerformance:
    """Test document processor performance"""
    
    @pytest.mark.asyncio
    async def test_small_document_processing(self, benchmark, performance_config, fast_mock_ollama_client):
        """Benchmark small document processing"""
        processor = LangChainDocumentProcessor(
            config=performance_config,
            ollama_client=fast_mock_ollama_client
        )
        
        # Small documents
        small_docs = [
            SAMPLE_DOCUMENTS["simple_markdown"]["content"],
            "# Quick Test\n\nShort content for testing.",
            "Small piece of text with minimal content.",
            "Another small document sample.",
            "Brief text for performance testing."
        ]
        
        for i, content in enumerate(small_docs):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(content)
                doc_file = f.name
            
            try:
                benchmark.start_benchmark(f"small_doc_run_{i}")
                
                result = await processor.process_document(doc_file)
                
                benchmark.end_benchmark()
                
                assert result is not None
                assert result.metadata.word_count > 0
                
            finally:
                Path(doc_file).unlink()
        
        stats = benchmark.get_stats("small_doc_run_0")
        print(f"Small document processing time: {stats['time_mean']:.3f}s")
        
        # Small documents should process quickly
        assert stats['time_mean'] < 5.0
    
    @pytest.mark.asyncio
    async def test_medium_document_processing(self, benchmark, performance_config, fast_mock_ollama_client):
        """Benchmark medium document processing"""
        processor = LangChainDocumentProcessor(
            config=performance_config,
            ollama_client=fast_mock_ollama_client
        )
        
        # Medium-sized documents
        medium_docs = [
            SAMPLE_DOCUMENTS["complex_markdown"]["content"],
            SAMPLE_DOCUMENTS["python_code"]["content"],
            SAMPLE_DOCUMENTS["javascript_code"]["content"]
        ]
        
        for i, content in enumerate(medium_docs):
            suffix = '.md' if i == 0 else ('.py' if i == 1 else '.js')
            
            with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
                f.write(content)
                doc_file = f.name
            
            try:
                benchmark.start_benchmark(f"medium_doc_run_{i}")
                
                result = await processor.process_document(doc_file)
                
                benchmark.end_benchmark()
                
                assert result is not None
                assert len(result.chunks) > 0
                
            finally:
                Path(doc_file).unlink()
        
        stats = benchmark.get_stats("medium_doc_run_0")
        print(f"Medium document processing time: {stats['time_mean']:.3f}s")
        
        # Medium documents should still process reasonably quickly
        assert stats['time_mean'] < 15.0
    
    @pytest.mark.asyncio
    async def test_large_document_processing(self, benchmark, performance_config, fast_mock_ollama_client):
        """Benchmark large document processing"""
        processor = LangChainDocumentProcessor(
            config=performance_config,
            ollama_client=fast_mock_ollama_client
        )
        
        # Create large document
        large_content = "# Large Performance Test Document\n\n"
        large_content += "This is a paragraph for testing. " * 100
        large_content += "\n\n## Section 1\n\n"
        large_content += "Section content with more text. " * 150
        large_content += "\n\n## Section 2\n\n" 
        large_content += "More section content for comprehensive testing. " * 200
        large_content += "\n\n## Code Section\n\n```python\n"
        large_content += "def test_function():\n    return 'test'\n" * 50
        large_content += "\n```\n\n"
        large_content += "Final section with concluding text. " * 100
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(large_content)
            large_file = f.name
        
        try:
            # Run multiple times for consistent benchmarking
            for i in range(3):
                benchmark.start_benchmark(f"large_doc_run_{i}")
                
                result = await processor.process_document(large_file)
                
                benchmark.end_benchmark()
                
                assert result is not None
                assert len(result.chunks) > 5  # Should create multiple chunks
                assert result.metadata.word_count > 1000
            
            stats = benchmark.get_stats("large_doc_run_0")
            print(f"Large document processing time: {stats['time_mean']:.3f}s")
            print(f"Large document memory usage: {stats['memory_mean']:.2f} MB")
            
            # Large documents may take longer but should still be reasonable
            assert stats['time_mean'] < 60.0  # 1 minute max
            assert stats['memory_mean'] < 200.0  # 200 MB max
            
        finally:
            Path(large_file).unlink()
    
    @pytest.mark.asyncio
    async def test_batch_processing_performance(self, benchmark, performance_config, fast_mock_ollama_client):
        """Benchmark batch document processing"""
        processor = LangChainDocumentProcessor(
            config=performance_config,
            ollama_client=fast_mock_ollama_client
        )
        
        # Create multiple test files
        test_files = []
        try:
            for i in range(5):
                content = f"# Test Document {i}\n\nContent for document {i}. " * (10 + i * 5)
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                    f.write(content)
                    test_files.append(f.name)
            
            # Benchmark batch processing
            benchmark.start_benchmark("batch_processing")
            
            # Process all files concurrently
            tasks = [processor.process_document(file_path) for file_path in test_files]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            benchmark.end_benchmark()
            
            # Verify results
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) >= 4  # Most should succeed
            
            stats = benchmark.get_stats("batch_processing")
            print(f"Batch processing time ({len(test_files)} files): {stats['time_mean']:.3f}s")
            print(f"Average time per file: {stats['time_mean']/len(test_files):.3f}s")
            
            # Batch processing should be efficient
            assert stats['time_mean'] < 30.0  # 30 seconds max for 5 files
            
        finally:
            for file_path in test_files:
                Path(file_path).unlink()


class TestMemoryUsagePerformance:
    """Test memory usage patterns"""
    
    @pytest.mark.asyncio
    async def test_memory_efficiency(self, benchmark, performance_config, fast_mock_ollama_client):
        """Test memory usage efficiency"""
        import gc
        
        processor = LangChainDocumentProcessor(
            config=performance_config,
            ollama_client=fast_mock_ollama_client
        )
        
        # Create moderately large document
        content = "# Memory Test Document\n\n" + "Test content paragraph. " * 500
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            test_file = f.name
        
        try:
            # Measure memory before processing
            gc.collect()
            initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Process document multiple times
            for i in range(5):
                benchmark.start_benchmark(f"memory_test_run_{i}")
                
                result = await processor.process_document(test_file)
                
                benchmark.end_benchmark()
                
                assert result is not None
                
                # Force garbage collection
                gc.collect()
            
            # Measure memory after processing
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_increase = final_memory - initial_memory
            
            print(f"Memory increase after 5 processing runs: {memory_increase:.2f} MB")
            
            # Memory increase should be reasonable (less than 100 MB)
            assert memory_increase < 100.0
            
            stats = benchmark.get_stats("memory_test_run_0")
            print(f"Average memory delta per run: {stats['memory_mean']:.2f} MB")
            
        finally:
            Path(test_file).unlink()
    
    @pytest.mark.asyncio
    async def test_memory_cleanup(self, benchmark, performance_config, fast_mock_ollama_client):
        """Test that memory is properly cleaned up"""
        import gc
        
        processor = LangChainDocumentProcessor(
            config=performance_config,
            ollama_client=fast_mock_ollama_client
        )
        
        # Create test document
        content = "# Cleanup Test\n\n" + "Content for cleanup testing. " * 200
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            test_file = f.name
        
        try:
            memory_samples = []
            
            for i in range(10):
                # Process document
                result = await processor.process_document(test_file)
                assert result is not None
                
                # Clear references
                del result
                
                # Force garbage collection
                gc.collect()
                
                # Sample memory
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)
            
            # Memory usage should stabilize (not continuously increase)
            memory_trend = memory_samples[-3:] # Last 3 samples
            memory_variance = max(memory_trend) - min(memory_trend)
            
            print(f"Memory variance in last 3 runs: {memory_variance:.2f} MB")
            print(f"Memory samples: {[f'{m:.1f}' for m in memory_samples]}")
            
            # Memory variance should be small (< 50 MB)
            assert memory_variance < 50.0
            
        finally:
            Path(test_file).unlink()


def test_run_all_benchmarks(benchmark, performance_config, fast_mock_ollama_client):
    """Run all performance benchmarks and print summary"""
    # This test will run all the benchmarks and provide a summary
    # Individual test methods will populate the benchmark results
    pass


if __name__ == "__main__":
    # Run benchmarks with verbose output
    pytest.main([__file__, "-v", "-s"])
