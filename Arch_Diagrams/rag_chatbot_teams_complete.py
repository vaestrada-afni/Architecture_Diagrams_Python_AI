"""
RAG Chatbot Architecture - Complete MVP with Teams & Conversation Memory
========================================================================
This diagram shows the full architecture including:
- Microsoft Teams integration via Azure Bot Service
- Conversation memory with Cosmos DB
- Modular component design
- Azure AI Search for hybrid search

Generated with: diagrams library (https://diagrams.mingrammer.com)
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import FunctionApps
from diagrams.azure.database import CosmosDb, CacheForRedis
from diagrams.azure.identity import ManagedIdentities
from diagrams.azure.integration import APIManagement
from diagrams.azure.security import KeyVaults
from diagrams.azure.web import AppServices
from diagrams.azure.analytics import AnalysisServices
from diagrams.azure.devops import ApplicationInsights
from diagrams.azure.storage import BlobStorage
from diagrams.azure.ml import CognitiveServices
from diagrams.onprem.client import Users, Client
from diagrams.saas.chat import Teams
from diagrams.generic.database import SQL
from diagrams.custom import Custom
import os

# Graph attributes for better layout
graph_attr = {
    "fontsize": "24",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.2",
    "fontname": "Arial",
}

node_attr = {
    "fontsize": "11",
    "fontname": "Arial",
}

edge_attr = {
    "fontsize": "10",
    "fontname": "Arial",
}

# Output directory
output_dir = os.path.join(os.path.dirname(__file__), "diagrams")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "rag_chatbot_teams_complete")

with Diagram(
    "RAG Chatbot - Teams Integration with Conversation Memory",
    filename=output_path,
    show=False,
    direction="TB",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
):
    # =========================================================================
    # USER LAYER - Microsoft Teams
    # =========================================================================
    with Cluster("User Interface"):
        users = Users("~50 Users")
        teams = Teams("Microsoft Teams\n(Chat UI)")
        users >> Edge(label="Chat") >> teams

    # =========================================================================
    # BOT FRAMEWORK LAYER - Azure Bot Service (FREE)
    # =========================================================================
    with Cluster("Azure Bot Service (Free Tier)", graph_attr={"bgcolor": "#E8F5E9"}):
        bot_service = AppServices("Bot Service\n• Routes messages\n• Teams channel\n• Auth handling")
    
    teams >> Edge(label="Bot Framework\nProtocol", color="blue") >> bot_service

    # =========================================================================
    # ORCHESTRATION LAYER - Modular Azure Functions
    # =========================================================================
    with Cluster("RAG Orchestrator (Azure Functions)", graph_attr={"bgcolor": "#E3F2FD"}):
        with Cluster("Module 1: Bot Handler"):
            bot_handler = FunctionApps("bot_handler.py\n• Receive messages\n• Format responses\n• Adaptive Cards")
        
        with Cluster("Module 2: Conversation Manager"):
            conv_manager = FunctionApps("chat_history.py\n• Load history\n• Save turns\n• Session mgmt")
        
        with Cluster("Module 3: Query Processor"):
            query_processor = FunctionApps("query_processor.py\n• Query rewriting\n• Context injection\n• Intent detection")
        
        with Cluster("Module 4: Search Client"):
            search_module = FunctionApps("search_client.py\n• Hybrid search\n• Embedding\n• Result ranking")
        
        with Cluster("Module 5: LLM Client"):
            llm_module = FunctionApps("openai_client.py\n• Chat completion\n• Streaming\n• Token mgmt")
        
        with Cluster("Module 6: Citation Handler"):
            citation_module = FunctionApps("citations.py\n• Extract sources\n• Format links\n• Track refs")

    # Connect modules (showing modular flow)
    bot_service >> Edge(label="1. Message", color="green") >> bot_handler
    bot_handler >> Edge(label="2. Load history", style="dashed") >> conv_manager
    conv_manager >> Edge(label="3. Rewrite query", style="dashed") >> query_processor
    query_processor >> Edge(label="4. Search", style="dashed") >> search_module
    search_module >> Edge(label="5. Generate", style="dashed") >> llm_module
    llm_module >> Edge(label="6. Citations", style="dashed") >> citation_module
    citation_module >> Edge(label="7. Save turn", style="dashed") >> conv_manager

    # =========================================================================
    # DATA LAYER - Managed Services
    # =========================================================================
    with Cluster("Azure AI Services", graph_attr={"bgcolor": "#FFF3E0"}):
        with Cluster("Azure AI Search (Basic $75/mo)"):
            ai_search = CognitiveServices("AI Search\n• Hybrid search\n• Semantic ranking\n• Vector index")
        
        with Cluster("Azure OpenAI (~$35/mo)"):
            aoai_chat = CognitiveServices("GPT-5-mini\n• Chat completion\n• Streaming\n• ~$30/mo")
            aoai_embed = CognitiveServices("text-embedding-3-large\n• Query embedding\n• ~$5/mo")

    with Cluster("Conversation Memory", graph_attr={"bgcolor": "#F3E5F5"}):
        cosmos = CosmosDb("Cosmos DB\n(Serverless)\n• Chat history\n• 7-day TTL\n• Per-user sessions")
        redis = CacheForRedis("Redis Cache\n(Optional)\n• Frequent Q&A\n• Session cache")

    # =========================================================================
    # INGESTION LAYER - Document Processing
    # =========================================================================
    with Cluster("Document Ingestion (AI Search Indexer)", graph_attr={"bgcolor": "#EFEBE9"}):
        sharepoint = BlobStorage("SharePoint\nOnline")
        blob = BlobStorage("Blob Storage\n(backup)")
        indexer = CognitiveServices("AI Search Indexer\n• Auto chunking\n• Auto embedding\n• Incremental sync")
    
    sharepoint >> Edge(label="Graph API") >> indexer
    blob >> Edge(label="Optional") >> indexer
    indexer >> Edge(label="Index") >> ai_search
    indexer >> Edge(label="Embed", style="dashed") >> aoai_embed

    # =========================================================================
    # SECURITY LAYER
    # =========================================================================
    with Cluster("Security & Observability", graph_attr={"bgcolor": "#FFEBEE"}):
        entra = ManagedIdentities("Entra ID\n• User SSO\n• Managed Identity")
        keyvault = KeyVaults("Key Vault\n• API keys\n• Secrets")
        appinsights = ApplicationInsights("App Insights\n• Logging\n• Metrics\n• Traces")

    # =========================================================================
    # CONNECTIONS - Data Flow
    # =========================================================================
    # Search and LLM connections
    search_module >> Edge(label="Hybrid Query", color="orange") >> ai_search
    search_module >> Edge(label="Embed query", color="purple") >> aoai_embed
    ai_search >> Edge(label="Top-K chunks", color="orange") >> search_module
    
    llm_module >> Edge(label="Prompt + Context", color="red") >> aoai_chat
    aoai_chat >> Edge(label="Stream response", color="red") >> llm_module
    
    # Conversation memory
    conv_manager >> Edge(label="Read/Write", color="purple") >> cosmos
    conv_manager >> Edge(label="Cache", color="gray", style="dashed") >> redis
    
    # Security
    bot_handler >> Edge(style="dotted", color="gray") >> entra
    bot_handler >> Edge(style="dotted", color="gray") >> keyvault
    bot_handler >> Edge(style="dotted", color="gray") >> appinsights

print("""
======================================================================
✅ Complete RAG Architecture Diagram Generated!
======================================================================

📁 Output: diagrams/rag_chatbot_teams_complete.png

🏗️ MODULAR ARCHITECTURE (6 Independent Modules):
   ┌─────────────────────────────────────────────────────────────┐
   │ Module 1: bot_handler.py      - Bot Framework integration  │
   │ Module 2: chat_history.py     - Conversation memory        │
   │ Module 3: query_processor.py  - Query rewriting            │
   │ Module 4: search_client.py    - Azure AI Search            │
   │ Module 5: openai_client.py    - Azure OpenAI               │
   │ Module 6: citations.py        - Source tracking            │
   └─────────────────────────────────────────────────────────────┘

🔧 Each module can be:
   • Tested independently (unit tests)
   • Replaced without affecting others
   • Debugged in isolation
   • Scaled separately if needed

💰 Estimated Monthly Cost: $150-250 (with GPT-5-mini!)
   • AI Search (Basic): $75
   • Azure OpenAI (GPT-5-mini): ~$30
   • Azure OpenAI (Embeddings): ~$5
   • Cosmos DB (Serverless): $5-20
   • Functions (Consumption): $10-30
   • Bot Service: FREE

📊 Cost Breakdown (45,000 queries/month):
   • GPT-4o would cost: ~$787/month ❌
   • GPT-5-mini costs:  ~$30/month  ✅
   • Savings: 96% cheaper!
""")
