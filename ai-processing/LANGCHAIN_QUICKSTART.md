# LangChain RAG Quick Start Guide

## Prerequisites

1. **Install LangChain Dependencies**:
```bash
cd ai-processing
uv pip install langchain langchain-community langchain-chroma langchain-ollama
```

2. **Verify Your Current Setup**:
```bash
# Check if basic RAG is working
python -m src.api.rag_server
```

## Step 1: Enable LangChain in Configuration

Edit `config.yaml`:
```yaml
api:
  host: "127.0.0.1"
  port: 8000
  enable_rag: true
  enable_langchain: true  # Add this line
  
rag:
  use_langchain: true            # Enable LangChain by default
  retriever_strategy: "multi_query"  # or "contextual_compression", "parent_document"
  conversation_memory: true
  max_conversation_turns: 10
  context_docs: 8
  synthesis_style: "comprehensive"
  temperature: 0.1
```

## Step 2: Start Enhanced RAG Server

```bash
# Start the server
python src/api/rag_server.py

# You should see:
# INFO: LangChain dependencies available
# INFO: LangChain RAG initialized successfully
# INFO: RAG API Server initialized successfully
```

## Step 3: Test LangChain Features

### Basic Query Test
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "prismweave-rag",
    "messages": [
      {"role": "user", "content": "How do I implement authentication in a web application?"}
    ],
    "temperature": 0.1
  }'
```

### Conversation Memory Test
```bash
# First question
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "prismweave-rag",
    "messages": [
      {"role": "user", "content": "Tell me about OAuth implementation"}
    ]
  }'

# Follow-up question (LangChain will maintain context)
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "prismweave-rag",
    "messages": [
      {"role": "user", "content": "Tell me about OAuth implementation"},
      {"role": "assistant", "content": "[Previous response about OAuth]"},
      {"role": "user", "content": "What are the security risks with this approach?"}
    ]
  }'
```

### Advanced Retrieval Strategy Test
```bash
# Test different retrieval strategies
curl -X POST http://localhost:8000/rag/configure \
  -H "Content-Type: application/json" \
  -d '{
    "use_langchain": true,
    "retriever_strategy": "contextual_compression",
    "conversation_memory": true,
    "context_limit": 10
  }'
```

## Step 4: Compare Standard vs LangChain

### Test Standard RAG
```bash
curl -X POST http://localhost:8000/rag/configure \
  -H "Content-Type: application/json" \
  -d '{
    "use_langchain": false,
    "context_limit": 5,
    "synthesis_style": "comprehensive"
  }'

# Then ask a question
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "prismweave-rag",
    "messages": [
      {"role": "user", "content": "How do I debug API performance issues?"}
    ]
  }'
```

### Test LangChain RAG
```bash
curl -X POST http://localhost:8000/rag/configure \
  -H "Content-Type: application/json" \
  -d '{
    "use_langchain": true,
    "retriever_strategy": "multi_query",
    "conversation_memory": true,
    "context_limit": 8
  }'

# Ask the same question
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "prismweave-rag",
    "messages": [
      {"role": "user", "content": "How do I debug API performance issues?"}
    ]
  }'
```

## Step 5: Open WebUI Integration

1. **Update Docker Compose** to use LangChain-enabled server:
```yaml
# docker-compose.yml
version: '3.8'
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    environment:
      - OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1
      - OPENAI_API_KEY=dummy-key
      - ENABLE_RAG=true
    volumes:
      - open-webui:/app/backend/data
    extra_hosts:
      - "host.docker.internal:host-gateway"

volumes:
  open-webui:
```

2. **Start Open WebUI**:
```bash
docker-compose up -d
```

3. **Configure in Open WebUI**:
   - Go to http://localhost:3000
   - Settings → Connections
   - Add OpenAI Compatible API
   - URL: `http://host.docker.internal:8000/v1`
   - API Key: `dummy-key`
   - Model: `prismweave-rag`

## Step 6: VS Code Integration

Create `.vscode/settings.json` to use your enhanced RAG:
```json
{
  "github.copilot.advanced": {
    "debug.overrideEngine": "openai-compatible",
    "debug.overrideProxyUrl": "http://localhost:8000/v1",
    "debug.overrideProxyAuthorization": "Bearer dummy-key"
  }
}
```

## Step 7: Monitor Performance

### Check RAG Status
```bash
curl http://localhost:8000/rag/status
```

Expected response:
```json
{
  "enabled": true,
  "vector_db_status": "healthy",
  "model_status": "healthy",
  "document_count": 150,
  "langchain_available": true,
  "langchain_enabled": true,
  "retriever_strategy": "multi_query",
  "conversation_memory": true,
  "last_updated": "2025-01-11T10:30:00Z"
}
```

### View Logs
```bash
# Check for LangChain initialization
tail -f logs/rag_server.log | grep -i langchain
```

## Troubleshooting

### LangChain Not Available
```bash
# If you see "LangChain dependencies not available"
uv pip install langchain langchain-community langchain-chroma langchain-ollama

# Restart the server
python src/api/rag_server.py
```

### Memory Issues
```bash
# If conversation memory gets too large, configure limits
curl -X POST http://localhost:8000/rag/configure \
  -H "Content-Type: application/json" \
  -d '{
    "use_langchain": true,
    "conversation_memory": true,
    "max_conversation_turns": 5
  }'
```

### Performance Comparison
```bash
# Test response times
time curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "prismweave-rag", "messages": [{"role": "user", "content": "test query"}]}'
```

## Next Steps

1. **Experiment with Retrieval Strategies**:
   - `"multi_query"` - Best for complex questions
   - `"contextual_compression"` - Best for focused answers
   - `"parent_document"` - Best for code examples

2. **Tune Parameters**:
   - Adjust `context_docs` based on response quality
   - Modify `temperature` for creativity vs accuracy
   - Configure `max_conversation_turns` for memory efficiency

3. **Monitor Usage**:
   - Check `/rag/status` regularly
   - Monitor response times and quality
   - Compare user satisfaction between implementations

4. **Advanced Features**:
   - Add custom retrieval strategies
   - Implement domain-specific prompt templates
   - Create specialized chains for different use cases
