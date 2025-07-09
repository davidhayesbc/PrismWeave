# PrismWeave RAG Integration Setup Guide

This guide shows you how to set up PrismWeave RAG with Ollama and integrate it with Open WebUI and VS Code.

## Prerequisites

1. **Ollama installed and running** on `http://localhost:11434`
2. **Required models pulled** (check your `config.yaml` for model names)
3. **Vector database populated** with your documents
4. **Python environment** with PrismWeave dependencies

## Quick Start

### 1. Install API Server Dependencies

```bash
cd ai-processing
uv pip install -r requirements-api.txt
```

### 2. Start the RAG API Server

```bash
# Option A: Using the launcher script (recommended with uv)
python scripts/start_rag_server.py

# Option B: Direct start
cd ai-processing
python -m src.api.rag_server --host 127.0.0.1 --port 8000

# Option C: With LangChain dependencies auto-install
python scripts/start_rag_server.py --install-langchain
```

The server will start on `http://localhost:8000` with:
- OpenAI-compatible endpoint: `http://localhost:8000/v1/chat/completions` 
- RAG status: `http://localhost:8000/rag/status`
- Health check: `http://localhost:8000/health`

### 3. Verify RAG Setup

```bash
# Check server health
curl http://localhost:8000/health

# Check RAG status
curl http://localhost:8000/rag/status

# Test RAG question
curl -X POST http://localhost:8000/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the best practices for TypeScript development?"}'
```

## Integration Options

### Option 1: Open WebUI Integration

Open WebUI provides a ChatGPT-like interface that can use your RAG server.

1. **Start your RAG server** (see above)

2. **Launch Open WebUI with Docker:**
```bash
cd ai-processing/docker
docker-compose -f docker-compose.open-webui.yml up -d
```

3. **Access Open WebUI:**
   - URL: `http://localhost:3000`
   - Create an account on first visit
   - Your PrismWeave RAG model should be available in the model selector

4. **Configure model settings:**
   - Go to Settings → Models
   - Select "prismweave-rag" 
   - Adjust RAG parameters if needed

### Option 2: VS Code Integration

#### For GitHub Copilot Chat:

VS Code doesn't directly support custom API endpoints, but you can use the RAG server in several ways:

1. **Via Extension API calls** (requires custom extension):
   ```typescript
   // Example API call from VS Code extension
   const response = await fetch('http://localhost:8000/v1/chat/completions', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       model: 'prismweave-rag',
       messages: [{ role: 'user', content: 'Your question here' }]
     })
   });
   ```

2. **Via REST Client extension:**
   - Install "REST Client" extension
   - Create `.http` files to test your RAG endpoints
   - Example in `integrations/test-api.http`

3. **Via Continue extension:**
   - Install the "Continue" VS Code extension
   - Configure it to use your local RAG server
   - Add to your `config.json`:
   ```json
   {
     "models": [{
       "title": "PrismWeave RAG",
       "provider": "openai",
       "model": "prismweave-rag", 
       "apiBase": "http://localhost:8000/v1",
       "apiKey": "prismweave-rag-key"
     }]
   }
   ```

### Option 3: Command Line Interface

Use your existing CLI with enhanced RAG:

```bash
# Ask questions using your CLI (already working)
cd ai-processing
python cli/prismweave.py ask "How do I implement RAG with Ollama?"

# Check vector database health
python cli/prismweave.py vector-health

# Search your documents
python cli/prismweave.py search "TypeScript best practices"
```

## API Endpoints Reference

### OpenAI-Compatible Endpoints

- **POST** `/v1/chat/completions` - Chat completions with RAG
- **GET** `/v1/models` - List available models

### PrismWeave RAG Endpoints

- **GET** `/rag/status` - RAG system status
- **POST** `/rag/config` - Update RAG configuration  
- **POST** `/rag/ask` - Direct RAG question
- **GET** `/health` - Health check

### Example API Usage

```bash
# Chat completion with RAG
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "prismweave-rag",
    "messages": [
      {"role": "user", "content": "Explain TypeScript interfaces"}
    ],
    "context_docs": 5,
    "synthesis_style": "technical"
  }'

# Update RAG configuration
curl -X POST http://localhost:8000/rag/config \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "context_docs": 15,
    "synthesis_style": "comprehensive"
  }'
```

## Configuration

### RAG Server Configuration

Edit `config.yaml` to customize:

```yaml
api:
  host: "127.0.0.1"
  port: 8000
  rag_enabled: true
  
  rag:
    default_context_docs: 10
    default_synthesis_style: "comprehensive"
    enable_source_citations: true

ollama:
  host: http://localhost:11434
  models:
    large: "llama3.1:8b"           # For RAG synthesis
    embedding: "nomic-embed-text"  # For vector search
```

### Model Requirements

Ensure you have these models pulled in Ollama:

```bash
# Pull required models
ollama pull llama3.1:8b
ollama pull phi3:mini  
ollama pull nomic-embed-text
```

## Troubleshooting

### Common Issues

1. **RAG server won't start:**
   ```bash
   # Check if port is in use
   netstat -an | findstr :8000
   
   # Check Python path and dependencies
   python -c "import fastapi, uvicorn; print('Dependencies OK')"
   
   # Or install missing dependencies
   uv pip install fastapi uvicorn
   ```

2. **Vector database not found:**
   ```bash
   # Check vector database status
   python cli/prismweave.py vector-health
   
   # Rebuild if needed
   python cli/prismweave.py process /path/to/docs --add-to-vector
   ```

3. **Ollama connection issues:**
   ```bash
   # Test Ollama directly
   curl http://localhost:11434/api/tags
   
   # Check configured models
   python cli/prismweave.py health
   ```

4. **Empty RAG responses:**
   - Ensure your vector database has documents
   - Check similarity thresholds in config
   - Verify embedding model is working

### Log Analysis

Check logs for detailed error information:
```bash
# Run server with debug logging
python -m src.api.rag_server --log-level debug

# Check specific component health
curl http://localhost:8000/health
```

## Advanced Configuration

### Custom Synthesis Styles

You can customize the RAG synthesis styles by modifying the prompts in `src/rag/rag_synthesizer.py`:

- `brief` - Quick, concise answers
- `comprehensive` - Detailed, well-structured responses  
- `technical` - Implementation-focused with code examples

### Performance Tuning

Adjust these settings in `config.yaml`:

```yaml
processing:
  max_concurrent: 1          # Reduce if Ollama overloads
  chunk_size: 3000          # Larger for more context
  summary_timeout: 180      # Increase for complex docs

vector:
  max_results: 20           # More candidates for RAG
  similarity_threshold: 0.6 # Lower for more diverse context
```

### Security Considerations

For production use:
- Add authentication to the API server
- Use HTTPS with proper certificates
- Restrict CORS origins
- Implement rate limiting

## Next Steps

1. **Populate your vector database** with relevant documents
2. **Test the RAG functionality** with various question types
3. **Customize synthesis styles** for your use cases
4. **Integrate with your preferred client** (Open WebUI, VS Code extensions, etc.)
5. **Monitor performance** and adjust configuration as needed

## Support

For issues and questions:
- Check the troubleshooting section above
- Review logs for detailed error information  
- Test individual components (Ollama, vector DB, RAG synthesis)
- Ensure all dependencies are properly installed
