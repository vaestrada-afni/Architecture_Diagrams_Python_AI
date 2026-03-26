# RAG Chatbot MVP - Implementation Plan

> **Version:** 1.0  
> **Date:** January 30, 2026  
> **Timeline:** 6 Weeks  
> **Team Size:** 1-2 Developers

---

## Executive Summary

This document provides a **step-by-step implementation plan** for building a RAG Chatbot integrated with Microsoft Teams. The plan emphasizes:
- ✅ **Minimal infrastructure** (fully managed services)
- ✅ **Maximum impact** (enterprise-ready from day 1)
- ✅ **Conversational memory** (multi-turn conversations)
- ✅ **Teams integration** (native chat experience)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Microsoft Teams                                │
│  ┌─────────────┐                                                        │
│  │ Teams App   │◄────── Users chat here                                 │
│  └──────┬──────┘                                                        │
└─────────┼───────────────────────────────────────────────────────────────┘
          │ Bot Framework Protocol
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Azure Bot Service                                 │
│  • Routes messages between Teams and your bot                           │
│  • Handles authentication, channel management                           │
│  • FREE tier available                                                  │
└─────────┬───────────────────────────────────────────────────────────────┘
          │ HTTPS
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Azure Functions (RAG Orchestrator)                    │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ 1. Receive message from Bot Service                              │   │
│  │ 2. Load conversation history (last N messages)                   │   │
│  │ 3. Rewrite query with conversation context                       │   │
│  │ 4. Hybrid search Azure AI Search                                 │   │
│  │ 5. Build prompt with retrieved chunks                            │   │
│  │ 6. Generate response with Azure OpenAI                           │   │
│  │ 7. Save conversation turn to Cosmos DB                           │   │
│  │ 8. Return response with citations                                │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────┬───────────────┬───────────────┬───────────────────────────────┘
          │               │               │
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Azure AI Search │ │  Azure OpenAI   │ │   Cosmos DB     │
│ • Hybrid search │ │ • GPT-5-mini    │ │ • Chat history  │
│ • Semantic rank │ │ • Embeddings    │ │ • Session state │
│ • Vector store  │ │ • Streaming     │ │ • TTL auto-delete│
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## Required Tools & Access

### Azure Resources (Must Have)

| Resource | Purpose | SKU | Est. Cost/mo |
|----------|---------|-----|--------------|
| **Azure Subscription** | All resources | Pay-as-you-go | - |
| **Azure AI Search** | Vector + keyword search | Basic | $75 |
| **Azure OpenAI** | GPT-5-mini + Embeddings | Standard | $30-40 |
| **Azure Functions** | RAG orchestrator | Consumption | $10-30 |
| **Azure Bot Service** | Teams integration | Free (F0) | $0 |
| **Azure Cosmos DB** | Chat history | Serverless | $5-20 |
| **Azure Key Vault** | Secrets management | Standard | $1 |
| **Azure App Insights** | Monitoring | Pay-as-you-go | $10-20 |

**Estimated Total: $130-190/month** ✅

> 💡 **Why so cheap?** GPT-5-mini costs ~$0.15-0.60/1M tokens (vs GPT-4o at $5-15/1M).

### Development Tools (Local Machine)

| Tool | Purpose | Download |
|------|---------|----------|
| **VS Code** | Code editor | https://code.visualstudio.com |
| **Python 3.11+** | Backend development | https://python.org |
| **Azure CLI** | Resource management | `winget install Microsoft.AzureCLI` |
| **Azure Functions Core Tools** | Local function development | `npm install -g azure-functions-core-tools@4` |
| **Bot Framework Emulator** | Local bot testing | https://github.com/microsoft/BotFramework-Emulator |
| **Teams Toolkit (VS Code)** | Teams app development | VS Code extension |
| **Git** | Version control | https://git-scm.com |

### Required Access & Permissions

| Access | Who Grants | For What |
|--------|------------|----------|
| Azure Subscription (Contributor) | Azure Admin | Create resources |
| Azure OpenAI access | Microsoft (apply) | GPT-5, GPT-5-mini, embeddings |
| SharePoint API (Graph) | M365 Admin | Document indexing |
| Teams Admin | M365 Admin | Sideload apps |
| Microsoft Entra ID | IT Admin | App registration |

---

## Conversational Memory (Multi-Turn Chat)

### The Challenge
Without memory, each message is independent:
```
User: "What is our vacation policy?"
Bot: "You get 15 days PTO per year..."

User: "What about for senior employees?"  ← Bot has no idea what "what about" refers to!
Bot: "I don't understand your question."
```

### The Solution: Sliding Window + Query Rewriting

We'll implement a **3-layer conversation memory** system:

```
┌────────────────────────────────────────────────────────────────┐
│ Layer 1: Sliding Window (Last 5-10 messages)                   │
│ • Passed directly to LLM as conversation history               │
│ • Provides immediate context for follow-up questions           │
│ • Stored in Cosmos DB per conversation_id                      │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│ Layer 2: Query Rewriting with Context                          │
│ • LLM rewrites ambiguous queries using conversation history    │
│ • "What about senior employees?" → "What is the vacation       │
│   policy for senior employees?"                                │
│ • Better search results, more relevant answers                 │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│ Layer 3: Conversation Summary (Optional, for long sessions)    │
│ • Summarize older messages to save tokens                      │
│ • "User asked about PTO, then about senior benefits..."        │
│ • Enables unlimited conversation length                        │
└────────────────────────────────────────────────────────────────┘
```

### Implementation: Cosmos DB for Chat History

```python
# Cosmos DB container structure
{
    "id": "msg_12345",
    "conversation_id": "conv_abc123",  # Partition key
    "user_id": "user@company.com",
    "timestamp": "2026-01-30T10:30:00Z",
    "role": "user",  # or "assistant"
    "content": "What is our vacation policy?",
    "citations": [],  # For assistant messages
    "ttl": 604800  # Auto-delete after 7 days
}
```

```python
# Get conversation history
def get_chat_history(container, conversation_id: str, limit: int = 10):
    """Retrieve last N messages for context."""
    query = """
        SELECT TOP @limit *
        FROM c
        WHERE c.conversation_id = @conv_id
        ORDER BY c.timestamp DESC
    """
    results = container.query_items(
        query=query,
        parameters=[
            {"name": "@limit", "value": limit},
            {"name": "@conv_id", "value": conversation_id}
        ],
        partition_key=conversation_id
    )
    return list(reversed(list(results)))  # Oldest first
```

### Query Rewriting (The Magic ✨)

```python
async def rewrite_query_with_context(
    user_query: str,
    chat_history: list[dict]
) -> str:
    """Rewrite ambiguous queries using conversation context."""
    
    if not chat_history:
        return user_query  # No history, use original query
    
    # Build history string
    history_text = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in chat_history[-5:]  # Last 5 messages
    ])
    
    rewrite_prompt = f"""Given the conversation history below, rewrite the user's 
latest query to be standalone and unambiguous. If the query is already clear, 
return it unchanged.

CONVERSATION HISTORY:
{history_text}

LATEST USER QUERY: {user_query}

REWRITTEN QUERY (standalone, no pronouns like "it", "that", "this"):"""

    response = await openai_client.chat.completions.create(
        model="gpt-5-mini",  # Use mini for speed/cost
        messages=[{"role": "user", "content": rewrite_prompt}],
        max_tokens=200,
        temperature=0
    )
    
    return response.choices[0].message.content.strip()
```

### Example Flow

```
Turn 1:
  User: "What is our vacation policy?"
  → Search: "vacation policy" 
  → Answer: "You get 15 days PTO per year..."

Turn 2:
  User: "What about for senior employees?"
  → Rewrite: "What is the vacation policy for senior employees?"
  → Search: "vacation policy senior employees"
  → Answer: "Senior employees (5+ years) get 20 days PTO..."

Turn 3:
  User: "Can I carry over unused days?"
  → Rewrite: "Can senior employees carry over unused vacation days?"
  → Search: "carry over unused vacation days senior employees"
  → Answer: "Yes, you can carry over up to 5 unused PTO days..."
```

---

## Teams Integration (Azure Bot Service)

### Why Azure Bot Service?

| Option | Effort | Teams Integration | Recommendation |
|--------|--------|-------------------|----------------|
| Custom webhook | High | Manual | ❌ Not recommended |
| Power Virtual Agents | Low | Native | ⚠️ Limited control |
| **Azure Bot Service** | Medium | **Native** | ✅ **Best choice** |

### How It Works

```
1. User sends message in Teams
         ↓
2. Teams → Bot Framework Service (Microsoft hosted)
         ↓
3. Bot Framework → Your Azure Function (messaging endpoint)
         ↓
4. Your Function processes RAG, returns response
         ↓
5. Bot Framework → Teams → User sees response
```

### Implementation Steps

#### Step 1: Create Azure Bot Service

```bash
# Create Bot Service (Free tier)
az bot create \
  --resource-group rg-rag-chatbot \
  --name rag-chatbot-bot \
  --kind azurebot \
  --sku F0 \
  --app-type MultiTenant \
  --location global
```

#### Step 2: Configure Messaging Endpoint

```bash
# Point to your Azure Function
az bot update \
  --resource-group rg-rag-chatbot \
  --name rag-chatbot-bot \
  --endpoint "https://your-function-app.azurewebsites.net/api/messages"
```

#### Step 3: Enable Teams Channel

```bash
# Enable Teams channel
az bot channel create \
  --resource-group rg-rag-chatbot \
  --name rag-chatbot-bot \
  --channel-name MsTeamsChannel
```

#### Step 4: Azure Function Bot Handler

```python
# function_app.py
import azure.functions as func
from botbuilder.core import BotFrameworkAdapter, TurnContext
from botbuilder.schema import Activity

app = func.FunctionApp()

# Bot adapter
adapter = BotFrameworkAdapter({
    "app_id": os.environ["BOT_APP_ID"],
    "app_password": os.environ["BOT_APP_PASSWORD"]
})

@app.function_name("messages")
@app.route(route="messages", methods=["POST"])
async def messages(req: func.HttpRequest) -> func.HttpResponse:
    """Handle incoming Bot Framework messages."""
    
    body = req.get_json()
    activity = Activity().deserialize(body)
    
    async def turn_handler(turn_context: TurnContext):
        # Get conversation ID (for chat history)
        conversation_id = turn_context.activity.conversation.id
        user_id = turn_context.activity.from_property.id
        user_message = turn_context.activity.text
        
        # 1. Load chat history
        history = await get_chat_history(conversation_id)
        
        # 2. Rewrite query with context
        rewritten_query = await rewrite_query_with_context(user_message, history)
        
        # 3. RAG pipeline
        response = await rag_query(rewritten_query, history)
        
        # 4. Save to chat history
        await save_chat_turn(conversation_id, user_id, user_message, response)
        
        # 5. Send response with citations
        await turn_context.send_activity(
            Activity(
                type="message",
                text=response["answer"],
                attachments=format_citations_as_cards(response["sources"])
            )
        )
    
    await adapter.process_activity(req, "", turn_handler)
    return func.HttpResponse(status_code=200)
```

#### Step 5: Create Teams App Package

Create a `manifest.json` for your Teams app:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.17/MicrosoftTeams.schema.json",
  "manifestVersion": "1.17",
  "version": "1.0.0",
  "id": "{{BOT_APP_ID}}",
  "name": {
    "short": "RAG Chatbot",
    "full": "RAG Chatbot - Document Q&A"
  },
  "description": {
    "short": "Ask questions about company documents",
    "full": "A chatbot that answers questions using your SharePoint documents with citations."
  },
  "icons": {
    "outline": "outline.png",
    "color": "color.png"
  },
  "accentColor": "#0078D4",
  "bots": [
    {
      "botId": "{{BOT_APP_ID}}",
      "scopes": ["personal", "team", "groupChat"],
      "supportsFiles": false,
      "isNotificationOnly": false,
      "commandLists": [
        {
          "scopes": ["personal"],
          "commands": [
            {
              "title": "help",
              "description": "Get help using the chatbot"
            },
            {
              "title": "clear",
              "description": "Clear conversation history"
            }
          ]
        }
      ]
    }
  ],
  "permissions": ["identity", "messageTeamMembers"],
  "validDomains": ["your-function-app.azurewebsites.net"]
}
```

#### Step 6: Deploy to Teams

```bash
# Package the app
zip -r rag-chatbot.zip manifest.json color.png outline.png

# Sideload via Teams Admin Center or directly in Teams
# Go to Teams → Apps → Manage your apps → Upload custom app
```

---

## 6-Week Implementation Timeline

### Week 1: Infrastructure Setup

| Day | Task | Output |
|-----|------|--------|
| 1 | Create Azure resource group, Key Vault | Resource group ready |
| 2 | Deploy Azure AI Search (Basic tier) | Search service running |
| 3 | Deploy Azure OpenAI, request quota | GPT-5-mini + embeddings available |
| 4 | Deploy Azure Cosmos DB (Serverless) | Database for chat history |
| 5 | Deploy Azure Functions (Python) | Empty function app |

**Deliverable:** All Azure infrastructure provisioned

### Week 2: Document Ingestion

| Day | Task | Output |
|-----|------|--------|
| 1 | Configure SharePoint indexer in AI Search | Connector ready |
| 2 | Create AI Search skillset (chunking + embedding) | Skillset configured |
| 3 | Create AI Search index with vector fields | Index schema ready |
| 4 | Run indexer on SharePoint library | Documents indexed |
| 5 | Test search queries in Azure Portal | Search working |

**Deliverable:** Documents searchable with hybrid search

### Week 3: RAG Orchestrator

| Day | Task | Output |
|-----|------|--------|
| 1 | Implement basic RAG function (search + generate) | MVP RAG working |
| 2 | Add hybrid search with semantic ranking | Better retrieval |
| 3 | Implement citation extraction | Sources tracked |
| 4 | Add system prompt and guardrails | Safe responses |
| 5 | Local testing with sample questions | RAG validated |

**Deliverable:** RAG pipeline working locally

### Week 4: Conversation Memory

| Day | Task | Output |
|-----|------|--------|
| 1 | Design Cosmos DB schema for chat history | Schema ready |
| 2 | Implement save/load chat history | Storage working |
| 3 | Implement query rewriting with context | Multi-turn working |
| 4 | Add sliding window (last 10 messages) | Context window |
| 5 | Test multi-turn conversations | Memory validated |

**Deliverable:** Conversational memory working

### Week 5: Teams Integration

| Day | Task | Output |
|-----|------|--------|
| 1 | Create Azure Bot Service | Bot registered |
| 2 | Implement Bot Framework handler in Functions | Messages processed |
| 3 | Enable Teams channel | Teams connected |
| 4 | Create Teams app manifest | App package ready |
| 5 | Sideload and test in Teams | Bot in Teams |

**Deliverable:** Chatbot working in Microsoft Teams

### Week 6: Testing & Polish

| Day | Task | Output |
|-----|------|--------|
| 1 | Create 50 test Q&A pairs | Test dataset |
| 2 | Run automated evaluation (precision, faithfulness) | Metrics baseline |
| 3 | User acceptance testing (5-10 users) | Feedback collected |
| 4 | Bug fixes and prompt tuning | Issues resolved |
| 5 | Documentation and handover | Docs complete |

**Deliverable:** Production-ready MVP

---

## Complete RAG Flow with Memory

```python
# Full RAG orchestration with conversation memory
async def rag_with_memory(
    user_message: str,
    conversation_id: str,
    user_id: str
) -> dict:
    """
    Complete RAG flow with conversation memory.
    
    1. Load conversation history
    2. Rewrite query with context
    3. Hybrid search with semantic ranking
    4. Generate response with citations
    5. Save turn to history
    """
    
    # 1. Load conversation history (last 10 messages)
    chat_history = await cosmos_client.get_chat_history(
        conversation_id=conversation_id,
        limit=10
    )
    
    # 2. Rewrite query if we have history
    if chat_history:
        search_query = await rewrite_query_with_context(
            user_query=user_message,
            chat_history=chat_history
        )
    else:
        search_query = user_message
    
    # 3. Hybrid search with semantic ranking
    search_results = search_client.search(
        search_text=search_query,
        vector_queries=[
            VectorizedQuery(
                vector=await get_embedding(search_query),
                k_nearest_neighbors=10,
                fields="contentVector"
            )
        ],
        query_type="semantic",
        semantic_configuration_name="default",
        top=5,
        select=["title", "content", "sourceUrl", "chunk_id"]
    )
    
    # 4. Build context from search results
    chunks = list(search_results)
    context = "\n\n".join([
        f"[Source {i+1}: {c['title']}]\n{c['content']}"
        for i, c in enumerate(chunks)
    ])
    
    # 5. Build messages for chat completion
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]
    
    # Add conversation history
    for msg in chat_history[-5:]:  # Last 5 turns
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current turn with context
    messages.append({
        "role": "user",
        "content": f"""Use the following sources to answer the question. 
Cite sources using [Source N] format.

SOURCES:
{context}

QUESTION: {user_message}

ANSWER:"""
    })
    
    # 6. Generate response
    response = await openai_client.chat.completions.create(
        model="gpt-5-mini",  # Fast, cheap, high quality
        messages=messages,
        temperature=0.3,
        max_tokens=1000,
        stream=True  # Enable streaming for Teams
    )
    
    answer = ""
    async for chunk in response:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content
    
    # 7. Extract citations
    citations = [
        {
            "title": c["title"],
            "url": c["sourceUrl"],
            "chunk_id": c["chunk_id"]
        }
        for c in chunks
    ]
    
    # 8. Save conversation turn
    await cosmos_client.save_turn(
        conversation_id=conversation_id,
        user_id=user_id,
        user_message=user_message,
        assistant_message=answer,
        citations=citations
    )
    
    return {
        "answer": answer,
        "sources": citations,
        "rewritten_query": search_query
    }
```

---

## System Prompt (Optimized for RAG)

```python
SYSTEM_PROMPT = """You are a helpful assistant that answers questions about company documents.

RULES:
1. ONLY use information from the provided sources to answer questions.
2. If the sources don't contain the answer, say "I couldn't find information about that in the available documents."
3. ALWAYS cite your sources using [Source N] format after each claim.
4. Be concise but complete.
5. If asked about something unrelated to the documents, politely redirect to document-related topics.
6. Never make up information not in the sources.
7. Maintain a professional, helpful tone.

CITATION FORMAT:
- Use [Source 1], [Source 2], etc. inline after each fact
- At the end, list the source titles for reference

CONVERSATION CONTEXT:
- You may reference previous messages in this conversation
- If the user asks a follow-up question, use context from previous turns"""
```

---

## Project Structure

```
rag-chatbot/
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD pipeline
├── infra/
│   ├── main.bicep             # Infrastructure as Code
│   ├── ai-search.bicep        # AI Search resources
│   ├── openai.bicep           # Azure OpenAI
│   ├── cosmos.bicep           # Cosmos DB
│   └── bot.bicep              # Bot Service
├── src/
│   └── functions/
│       ├── function_app.py    # Azure Functions entry point
│       ├── rag_orchestrator.py # RAG pipeline
│       ├── chat_history.py    # Cosmos DB operations
│       ├── search_client.py   # AI Search operations
│       ├── openai_client.py   # Azure OpenAI operations
│       └── bot_handler.py     # Bot Framework handler
├── teams-app/
│   ├── manifest.json          # Teams app manifest
│   ├── color.png              # App icon (192x192)
│   └── outline.png            # App icon (32x32)
├── tests/
│   ├── test_rag.py            # Unit tests
│   ├── test_search.py         # Search tests
│   └── eval_dataset.json      # Evaluation Q&A pairs
├── docs/
│   ├── ARCHITECTURE.md        # Architecture docs
│   ├── DEPLOYMENT.md          # Deployment guide
│   └── TROUBLESHOOTING.md     # Common issues
├── requirements.txt           # Python dependencies
├── host.json                  # Functions config
├── local.settings.json        # Local dev settings
└── README.md                  # Project overview
```

---

## Key Dependencies

```txt
# requirements.txt
azure-functions>=1.17.0
azure-identity>=1.15.0
azure-search-documents>=11.4.0
azure-cosmos>=4.5.0
openai>=1.12.0
botbuilder-core>=4.15.0
botbuilder-integration-aiohttp>=4.15.0
python-dotenv>=1.0.0
```

---

## Cost Summary

| Resource | Monthly Cost |
|----------|-------------|
| Azure AI Search (Basic) | $75 |
| Azure OpenAI (GPT-5-mini + Embeddings) | $30-40 |
| Azure Functions (Consumption) | $10-30 |
| Azure Cosmos DB (Serverless) | $5-20 |
| Azure Bot Service (Free) | $0 |
| Azure App Insights | $10-20 |
| **TOTAL** | **$130-185/month** |

> 💡 **Cost Comparison (45,000 queries/month):**
> - GPT-4o: ~$787/month ❌
> - GPT-5-mini: ~$30/month ✅
> - **Savings: 96%**

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Retrieval Accuracy | ≥85% | Correct doc in top-3 |
| Answer Faithfulness | ≥95% | Grounded in sources |
| Response Time | <5s | P95 latency |
| Multi-turn Success | ≥80% | Follow-up questions work |
| User Satisfaction | ≥4.0/5 | Survey |

---

## Next Steps

1. **Get Azure access** - Request subscription and OpenAI quota
2. **Set up dev environment** - Install VS Code, Python, Azure CLI
3. **Clone starter repo** - Use Azure Samples template
4. **Start Week 1** - Provision infrastructure

### Recommended Starter Template

Use the official Microsoft sample as a foundation:
```bash
git clone https://github.com/Azure-Samples/azure-search-openai-demo
cd azure-search-openai-demo
azd up
```

This template includes:
- ✅ Azure AI Search integration
- ✅ Azure OpenAI integration
- ✅ Chat history with Cosmos DB
- ✅ React frontend (can be hidden for Teams-only)
- ✅ Infrastructure as Code (Bicep)
- ✅ CI/CD pipelines

Then add Teams integration following Week 5 tasks.
