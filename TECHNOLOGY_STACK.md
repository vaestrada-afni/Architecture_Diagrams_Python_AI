# Technology Stack & Dependencies

> **Version:** 1.0  
> **Date:** January 30, 2026  
> **Architecture:** Modular Microservices

---

## Executive Summary

This document outlines the technology choices for the RAG Chatbot MVP. We prioritize:
- ✅ **Azure-native SDKs** over third-party frameworks
- ✅ **Modular design** for easy debugging and maintenance
- ✅ **Minimal dependencies** to reduce complexity
- ✅ **Future-proof** model selection

---

## Framework Decision: Why NOT LangChain/LlamaIndex?

### The Question
> "Should we use LangChain, LlamaIndex, Semantic Kernel, or raw Azure SDKs?"

### Our Recommendation: **Azure SDKs (Direct)**

| Framework | Pros | Cons | Verdict |
|-----------|------|------|---------|
| **LangChain** | Popular, many examples | Abstraction overhead, frequent breaking changes, hard to debug | ❌ Not for MVP |
| **LlamaIndex** | Great for complex RAG | Overkill for simple use case, learning curve | ❌ Not for MVP |
| **Semantic Kernel** | Microsoft-backed, good for agents | Still evolving, more complex than needed | ⚠️ Consider for v2 |
| **Azure SDKs (Direct)** | Full control, minimal abstraction, easy to debug | More code to write | ✅ **Recommended** |

### Why Azure SDKs Win for MVP

1. **Debuggability**: When something breaks, you know exactly where to look
2. **No Magic**: Every API call is explicit and visible
3. **Stability**: Azure SDKs have stable, versioned APIs
4. **Documentation**: Excellent Microsoft docs for each SDK
5. **Simplicity**: Our RAG flow is straightforward, no framework needed

### When to Reconsider

| Scenario | Consider |
|----------|----------|
| Complex multi-agent workflows | → Semantic Kernel |
| Many data source connectors | → LlamaIndex |
| Rapid prototyping with many LLM providers | → LangChain |
| Production RAG on Azure | → **Azure SDKs** ✅ |

---

## Azure OpenAI Model Selection

### Available Models (January 2026)

| Model | Use Case | Speed | Cost | Context | Recommended |
|-------|----------|-------|------|---------|-------------|
| **GPT-5-mini** | Primary chat | Very Fast | $0.15/1M input, $0.60/1M output | 128K | ✅ **Default** |
| **GPT-5** | Complex reasoning | Fast | $2/1M input, $8/1M output | 200K | ✅ For complex queries |
| GPT-4o | Legacy/fallback | Fast | $5/1M input, $15/1M output | 128K | ⚠️ Expensive |
| GPT-4.1 | Legacy | Medium | $2/1M input, $8/1M output | 1M | ⚠️ Use GPT-5 instead |
| o1 | Deep reasoning | Slow | $15/1M input, $60/1M output | 200K | ❌ Overkill |
| **text-embedding-3-large** | Document & query embedding | Fast | $0.13/1M tokens | N/A | ✅ Required |

### Our Model Configuration

```python
# config.py - Model Configuration

MODELS = {
    # Primary chat completion (user-facing responses)
    "chat": {
        "deployment": "gpt-5-mini",      # Fast, cheap, high quality
        "model": "gpt-5-mini",
        "temperature": 0.3,              # Lower = more consistent
        "max_tokens": 1000,
        "streaming": True
    },
    
    # Query rewriting (internal, not user-facing)
    "rewrite": {
        "deployment": "gpt-5-mini",      # Same model, it's cheap enough
        "model": "gpt-5-mini",
        "temperature": 0,                # Deterministic
        "max_tokens": 200
    },
    
    # Complex queries (optional routing)
    "complex": {
        "deployment": "gpt-5",           # Full GPT-5 for hard questions
        "model": "gpt-5",
        "temperature": 0.2,
        "max_tokens": 2000
    },
    
    # Embeddings (document and query)
    "embedding": {
        "deployment": "text-embedding-3-large",
        "model": "text-embedding-3-large",
        "dimensions": 3072               # Full dimensions for best quality
    }
}
```

### Model Upgrade Path

```
Current (2026):
  Chat: GPT-5-mini (primary) + GPT-5 (complex)
  Embed: text-embedding-3-large

Cost Comparison (45,000 queries/month):
  GPT-4o:     ~$787/month  ❌
  GPT-5:      ~$405/month
  GPT-5-mini: ~$30/month   ✅ (This is what we use!)

Future:
  When GPT-6 releases → Just update deployment name
```

---

## Modular Architecture

### Design Principle: **Single Responsibility**

Each module does ONE thing well and can be:
- ✅ Tested independently
- ✅ Replaced without affecting others
- ✅ Debugged in isolation
- ✅ Scaled if needed

### Module Breakdown

```
src/
├── functions/
│   ├── function_app.py          # Entry point (routing only)
│   │
│   ├── modules/
│   │   ├── __init__.py
│   │   │
│   │   ├── bot_handler.py       # Module 1: Bot Framework
│   │   │   └── Handles: Message receive/send, Adaptive Cards
│   │   │   └── Dependencies: botbuilder-core
│   │   │   └── Can break: Only Teams messaging
│   │   │
│   │   ├── chat_history.py      # Module 2: Conversation Memory
│   │   │   └── Handles: Load/save history, session management
│   │   │   └── Dependencies: azure-cosmos
│   │   │   └── Can break: Only memory (RAG still works without it)
│   │   │
│   │   ├── query_processor.py   # Module 3: Query Processing
│   │   │   └── Handles: Query rewriting, context injection
│   │   │   └── Dependencies: openai (for rewrite)
│   │   │   └── Can break: Fallback to original query
│   │   │
│   │   ├── search_client.py     # Module 4: Search
│   │   │   └── Handles: Hybrid search, embedding, ranking
│   │   │   └── Dependencies: azure-search-documents, openai
│   │   │   └── Can break: Search fails (graceful error)
│   │   │
│   │   ├── openai_client.py     # Module 5: LLM
│   │   │   └── Handles: Chat completion, streaming
│   │   │   └── Dependencies: openai
│   │   │   └── Can break: Generation fails (graceful error)
│   │   │
│   │   └── citations.py         # Module 6: Citations
│   │       └── Handles: Extract sources, format links
│   │       └── Dependencies: None (pure Python)
│   │       └── Can break: No citations (answer still works)
│   │
│   └── utils/
│       ├── config.py            # Configuration management
│       ├── logging.py           # Structured logging
│       └── errors.py            # Error handling
```

### Dependency Injection Pattern

```python
# function_app.py - Entry point with dependency injection

from modules.bot_handler import BotHandler
from modules.chat_history import ChatHistoryManager
from modules.query_processor import QueryProcessor
from modules.search_client import SearchClient
from modules.openai_client import OpenAIClient
from modules.citations import CitationHandler

class RAGOrchestrator:
    """
    Main orchestrator that composes all modules.
    Each module can be mocked for testing.
    """
    
    def __init__(
        self,
        chat_history: ChatHistoryManager = None,
        query_processor: QueryProcessor = None,
        search_client: SearchClient = None,
        openai_client: OpenAIClient = None,
        citation_handler: CitationHandler = None
    ):
        # Dependency injection - can pass mocks for testing
        self.chat_history = chat_history or ChatHistoryManager()
        self.query_processor = query_processor or QueryProcessor()
        self.search_client = search_client or SearchClient()
        self.openai_client = openai_client or OpenAIClient()
        self.citation_handler = citation_handler or CitationHandler()
    
    async def process_message(
        self,
        user_message: str,
        conversation_id: str,
        user_id: str
    ) -> dict:
        """
        Main RAG flow - each step uses a separate module.
        If one module fails, others continue.
        """
        
        # Step 1: Load conversation history
        try:
            history = await self.chat_history.get_history(conversation_id)
        except Exception as e:
            logger.warning(f"Chat history unavailable: {e}")
            history = []  # Continue without history
        
        # Step 2: Rewrite query with context
        try:
            search_query = await self.query_processor.rewrite(
                user_message, history
            )
        except Exception as e:
            logger.warning(f"Query rewriting failed: {e}")
            search_query = user_message  # Use original query
        
        # Step 3: Search for relevant documents
        try:
            search_results = await self.search_client.hybrid_search(
                search_query
            )
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "answer": "I'm having trouble searching the documents. Please try again.",
                "sources": [],
                "error": str(e)
            }
        
        # Step 4: Generate response
        try:
            response = await self.openai_client.generate(
                user_message=user_message,
                context=search_results,
                history=history
            )
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {
                "answer": "I'm having trouble generating a response. Please try again.",
                "sources": [],
                "error": str(e)
            }
        
        # Step 5: Extract citations
        try:
            citations = self.citation_handler.extract(
                response, search_results
            )
        except Exception as e:
            logger.warning(f"Citation extraction failed: {e}")
            citations = []  # Continue without citations
        
        # Step 6: Save conversation turn
        try:
            await self.chat_history.save_turn(
                conversation_id=conversation_id,
                user_id=user_id,
                user_message=user_message,
                assistant_message=response,
                citations=citations
            )
        except Exception as e:
            logger.warning(f"Failed to save history: {e}")
            # Continue - not critical
        
        return {
            "answer": response,
            "sources": citations,
            "rewritten_query": search_query
        }
```

### Failure Isolation

| Module Fails | Impact | Fallback |
|--------------|--------|----------|
| Chat History | No conversation memory | Continue without history |
| Query Rewriting | Worse search results | Use original query |
| Search | ❌ Critical | Return error message |
| LLM Generation | ❌ Critical | Return error message |
| Citations | No source links | Answer still works |
| Bot Handler | ❌ Critical | Teams shows error |

### Testing Each Module Independently

```python
# tests/test_search_client.py - Unit test example

import pytest
from modules.search_client import SearchClient
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_hybrid_search_returns_results():
    """Test search module in isolation."""
    
    # Mock the Azure SDK
    with patch('modules.search_client.SearchClient') as mock:
        mock.search.return_value = [
            {"title": "PTO Policy", "content": "15 days...", "score": 0.95}
        ]
        
        client = SearchClient()
        results = await client.hybrid_search("vacation policy")
        
        assert len(results) > 0
        assert results[0]["title"] == "PTO Policy"

@pytest.mark.asyncio
async def test_search_handles_empty_results():
    """Test graceful handling of no results."""
    
    with patch('modules.search_client.SearchClient') as mock:
        mock.search.return_value = []
        
        client = SearchClient()
        results = await client.hybrid_search("xyzzy nonexistent")
        
        assert results == []
```

---

## Complete Dependencies (requirements.txt)

```txt
# =============================================================================
# Core Azure SDKs - These are the main dependencies
# =============================================================================
azure-functions>=1.17.0              # Azure Functions runtime
azure-identity>=1.15.0               # Managed Identity auth
azure-search-documents>=11.4.0       # Azure AI Search client
azure-cosmos>=4.5.0                  # Cosmos DB for chat history
azure-keyvault-secrets>=4.7.0        # Key Vault for secrets

# =============================================================================
# OpenAI - Using official SDK (not Azure-specific wrapper)
# =============================================================================
openai>=1.12.0                       # OpenAI Python SDK (works with Azure)

# =============================================================================
# Bot Framework - For Teams integration
# =============================================================================
botbuilder-core>=4.15.0              # Bot Framework core
botbuilder-integration-aiohttp>=4.15.0  # Async HTTP integration

# =============================================================================
# Utilities
# =============================================================================
python-dotenv>=1.0.0                 # Environment variable loading
pydantic>=2.5.0                      # Data validation
aiohttp>=3.9.0                       # Async HTTP client

# =============================================================================
# Observability
# =============================================================================
azure-monitor-opentelemetry>=1.2.0   # Azure Monitor integration
opencensus-ext-azure>=1.1.0          # Application Insights

# =============================================================================
# Development & Testing
# =============================================================================
pytest>=7.4.0                        # Testing framework
pytest-asyncio>=0.21.0               # Async test support
pytest-cov>=4.1.0                    # Code coverage
black>=23.0.0                        # Code formatting
mypy>=1.7.0                          # Type checking

# =============================================================================
# OPTIONAL - Only if you want framework abstraction later
# =============================================================================
# semantic-kernel>=1.0.0             # Microsoft's AI orchestration framework
# langchain>=0.1.0                   # LangChain (not recommended for MVP)
# llama-index>=0.10.0                # LlamaIndex (not recommended for MVP)
```

### Dependency Comparison

| What We Use | Alternative | Why Our Choice |
|-------------|-------------|----------------|
| `openai` SDK | `langchain.llms` | Direct control, easier debugging |
| `azure-search-documents` | `langchain.vectorstores` | Native features, no abstraction |
| `azure-cosmos` | `langchain.memory` | Full Cosmos DB features |
| `botbuilder-core` | Custom webhooks | Official Teams support |
| Pure Python | `langchain.chains` | Transparency, no magic |

---

## Configuration Management

```python
# config.py - Centralized configuration

import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    All configuration in one place.
    Change settings without touching code.
    """
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str  # Or use managed identity
    AZURE_OPENAI_API_VERSION: str = "2024-06-01"
    
    # Model deployments (change these to upgrade models)
    CHAT_MODEL_DEPLOYMENT: str = "gpt-4o"           # Primary chat
    REWRITE_MODEL_DEPLOYMENT: str = "gpt-4o-mini"   # Query rewriting
    EMBEDDING_DEPLOYMENT: str = "text-embedding-3-large"
    
    # Azure AI Search
    AZURE_SEARCH_ENDPOINT: str
    AZURE_SEARCH_INDEX: str = "documents"
    AZURE_SEARCH_SEMANTIC_CONFIG: str = "default"
    
    # Cosmos DB
    COSMOS_ENDPOINT: str
    COSMOS_DATABASE: str = "ragchatbot"
    COSMOS_CONTAINER: str = "conversations"
    CHAT_HISTORY_TTL: int = 604800  # 7 days in seconds
    
    # Bot Service
    BOT_APP_ID: str
    BOT_APP_PASSWORD: str
    
    # Feature flags (enable/disable modules)
    ENABLE_CHAT_HISTORY: bool = True
    ENABLE_QUERY_REWRITING: bool = True
    ENABLE_SEMANTIC_RANKING: bool = True
    ENABLE_STREAMING: bool = True
    
    # Retrieval settings
    SEARCH_TOP_K: int = 5
    HISTORY_WINDOW: int = 10
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Model Upgrade Process

To upgrade from GPT-4o to GPT-5 (when available):

```bash
# 1. Deploy new model in Azure OpenAI Studio
#    Create deployment named "gpt-5"

# 2. Update environment variable
export CHAT_MODEL_DEPLOYMENT="gpt-5"

# 3. Test locally
python -m pytest tests/

# 4. Deploy to Azure
func azure functionapp publish rag-chatbot-func

# That's it! No code changes needed.
```

---

## Architecture Diagram Reference

The complete architecture is in:
- **Diagram file:** [rag_chatbot_teams_complete.py](Arch_Diagrams/rag_chatbot_teams_complete.py)
- **Output:** [diagrams/rag_chatbot_teams_complete.png](Arch_Diagrams/diagrams/rag_chatbot_teams_complete.png)

### Visual: Modular Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FUNCTION APP                                    │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         function_app.py (Router)                       │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                     │                                        │
│         ┌───────────────────────────┼───────────────────────────┐           │
│         │                           │                           │           │
│         ▼                           ▼                           ▼           │
│  ┌─────────────┐             ┌─────────────┐             ┌─────────────┐   │
│  │   Module 1  │             │   Module 2  │             │   Module 3  │   │
│  │ Bot Handler │────────────▶│Chat History │────────────▶│Query Process│   │
│  │             │             │             │             │             │   │
│  │ botbuilder  │             │azure-cosmos │             │  openai     │   │
│  └─────────────┘             └─────────────┘             └─────────────┘   │
│                                                                  │           │
│         ┌───────────────────────────┬───────────────────────────┘           │
│         │                           │                                        │
│         ▼                           ▼                                        │
│  ┌─────────────┐             ┌─────────────┐             ┌─────────────┐   │
│  │   Module 4  │             │   Module 5  │             │   Module 6  │   │
│  │   Search    │────────────▶│   LLM Gen   │────────────▶│  Citations  │   │
│  │             │             │             │             │             │   │
│  │azure-search │             │  openai     │             │ pure python │   │
│  └─────────────┘             └─────────────┘             └─────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

✅ Each module has its own dependency
✅ Each module can be tested alone
✅ Each module can fail independently (with fallback)
✅ Replace any module without affecting others
```

---

## Summary

| Question | Answer |
|----------|--------|
| **Framework?** | Azure SDKs directly (no LangChain/LlamaIndex) |
| **Why?** | Simpler, more debuggable, full control |
| **LLM Model?** | GPT-4o (primary), GPT-4o-mini (query rewrite) |
| **Can upgrade to GPT-5?** | Yes - change 1 config value |
| **Modular?** | Yes - 6 independent modules |
| **Can fix one part without breaking others?** | Yes - each module isolated |
| **Dependencies?** | ~15 packages, all official Azure/Microsoft |
