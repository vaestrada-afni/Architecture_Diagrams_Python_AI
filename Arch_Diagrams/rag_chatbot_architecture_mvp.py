"""
Azure RAG Chatbot Architecture - MVP (Azure-Native)
Using Azure AI Search for Vector Database (Simplified, Enterprise-Ready)

Why Azure AI Search over Weaviate:
1. Integrated Vectorization - automatic chunking + embedding
2. Built-in Hybrid Search - vector + keyword combined
3. Semantic Ranking - AI reranking included
4. SharePoint Indexer - native connector via Graph API
5. Portal Wizard - "Import and vectorize data" in clicks
6. Fully Managed - no container infrastructure
7. Enterprise Ready - compliance, SLAs, support
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users

# Azure Compute
from diagrams.azure.compute import FunctionApps, AppServices

# Azure AI/ML
from diagrams.azure.ml import AzureOpenAI
from diagrams.azure.aimachinelearning import CognitiveSearch

# Azure Integration
from diagrams.azure.integration import APIManagement

# Azure Storage
from diagrams.azure.storage import BlobStorage

# Azure Cache
from diagrams.azure.database import CacheForRedis

# Azure Security & Identity
from diagrams.azure.identity import EntraConnect, ManagedIdentities

# Azure Analytics/Monitoring
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.devops import ApplicationInsights

# SaaS
from diagrams.saas.chat import Teams

# Graph attributes
graph_attr = {
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.0",
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5"
}

# Cluster styles
chat_cluster = {"fontsize": "13", "bgcolor": "#E8F5E9", "style": "rounded", "margin": "15"}
orchestration_cluster = {"fontsize": "13", "bgcolor": "#E3F2FD", "style": "rounded", "margin": "15"}
retrieval_cluster = {"fontsize": "13", "bgcolor": "#E1F5FE", "style": "rounded", "margin": "15"}
ingestion_cluster = {"fontsize": "13", "bgcolor": "#FFF3E0", "style": "rounded", "margin": "15"}
monitoring_cluster = {"fontsize": "13", "bgcolor": "#FFF9C4", "style": "rounded", "margin": "15"}
security_cluster = {"fontsize": "13", "bgcolor": "#ECEFF1", "style": "rounded", "margin": "15"}

# Create diagram
with Diagram(
    "RAG Chatbot Architecture - MVP\n(Azure-Native with Azure AI Search)",
    filename="diagrams/rag_chatbot_architecture_mvp",
    direction="TB",
    graph_attr=graph_attr,
    outformat=["png", "dot"],
    show=False
):
    
    # ========== USERS ==========
    users = Users("Users\n(≈50)")
    
    # ========== CHAT INTERFACE ==========
    with Cluster("Chat Interface", graph_attr=chat_cluster):
        teams = Teams("Teams Chat")
        web_app = AppServices("Web App\nChat UI")
    
    # ========== API GATEWAY (Optional for MVP) ==========
    apim = APIManagement("API Gateway\n(Optional)")
    
    # ========== RAG ORCHESTRATION ==========
    with Cluster("RAG Orchestration", graph_attr=orchestration_cluster):
        rag_api = FunctionApps("RAG Orchestrator\n(Azure Functions)\nLangChain/\nSemantic Kernel")
        
        # Cache for performance
        cache = CacheForRedis("Query Cache\n(Redis)\nOptional")
    
    # ========== AZURE AI SEARCH (THE KEY SIMPLIFICATION) ==========
    with Cluster("Azure AI Search\n(Managed Vector DB)", graph_attr=retrieval_cluster):
        ai_search = CognitiveSearch("Azure AI Search\n• Hybrid Search\n• Semantic Ranking\n• Integrated Vectors")
    
    # ========== AZURE OPENAI ==========
    aoai_embeddings = AzureOpenAI("Azure OpenAI\nEmbeddings\n(text-embedding-3)")
    aoai_llm = AzureOpenAI("Azure OpenAI\nGPT-4o / 4.1")
    
    # ========== SHAREPOINT (KNOWLEDGE SOURCE) ==========
    sharepoint = CognitiveSearch("SharePoint Online\nDocument Libraries")
    
    # ========== INGESTION (SIMPLIFIED - AI SEARCH HANDLES IT) ==========
    with Cluster("Ingestion Pipeline\n(Built into AI Search)", graph_attr=ingestion_cluster):
        indexer = FunctionApps("AI Search Indexer\n(Auto Chunking)\n(Auto Vectorization)")
        blob_staging = BlobStorage("Blob Storage\n(Optional Staging)")
    
    # ========== SECURITY ==========
    with Cluster("Security & Auth", graph_attr=security_cluster):
        entra_id = EntraConnect("Microsoft\nEntra ID")
        managed_id = ManagedIdentities("Managed\nIdentities")
    
    # ========== MONITORING ==========
    with Cluster("Observability", graph_attr=monitoring_cluster):
        app_insights = ApplicationInsights("Application\nInsights")
        log_analytics = LogAnalyticsWorkspaces("Log Analytics")
    
    # ===== USER FLOW =====
    users >> Edge(label="Chat") >> [teams, web_app]
    teams >> Edge(label="HTTPS") >> apim
    web_app >> Edge(label="HTTPS") >> apim
    apim >> Edge(label="Request") >> rag_api
    
    # ===== RAG FLOW (SIMPLIFIED) =====
    rag_api >> Edge(label="1. Cache\nCheck", style="dashed") >> cache
    rag_api >> Edge(label="2. Hybrid Search\n+ Semantic Rank") >> ai_search
    ai_search >> Edge(label="3. Top-K\nChunks") >> rag_api
    rag_api >> Edge(label="4. Prompt +\nContext") >> aoai_llm
    aoai_llm >> Edge(label="5. Answer +\nCitations") >> rag_api
    rag_api >> Edge(label="Response") >> apim
    
    # ===== INGESTION FLOW (SIMPLIFIED) =====
    sharepoint >> Edge(label="Graph API\n(via Indexer)") >> indexer
    blob_staging >> Edge(label="Blob\nIndexer") >> indexer
    indexer >> Edge(label="Auto\nChunk") >> ai_search
    indexer >> Edge(label="Auto\nEmbed") >> aoai_embeddings
    aoai_embeddings >> Edge(label="Vectors") >> ai_search
    
    # ===== SECURITY =====
    [teams, web_app] >> Edge(label="User Auth", style="dashed", color="gray") >> entra_id
    rag_api >> Edge(label="Managed\nIdentity", style="dashed", color="gray") >> managed_id
    ai_search >> Edge(label="RBAC", style="dashed", color="gray") >> managed_id
    
    # ===== MONITORING =====
    rag_api >> Edge(label="traces", style="dashed", color="orange") >> app_insights
    ai_search >> Edge(label="metrics", style="dashed", color="orange") >> app_insights
    indexer >> Edge(label="logs", style="dashed", color="orange") >> app_insights
    app_insights >> log_analytics

print("=" * 70)
print("✅ MVP RAG Architecture Diagram (Azure-Native) generated!")
print("=" * 70)
print("\n📁 Output files:")
print("   - diagrams/rag_chatbot_architecture_mvp.png")
print("   - diagrams/rag_chatbot_architecture_mvp.dot")
print("\n🎯 Key Simplifications vs. Weaviate Architecture:")
print("   1. ❌ No Container Apps infrastructure")
print("   2. ❌ No custom hybrid search implementation")
print("   3. ❌ No manual reranking setup")
print("   4. ❌ No separate BM25 index")
print("   5. ❌ No custom chunking code")
print("   6. ✅ All handled by Azure AI Search!")
print("\n💰 Estimated Monthly Cost (Basic Tier): ~$400-600/month")
print("   - Azure AI Search (Basic): $75")
print("   - Azure OpenAI (GPT-4o + Embeddings): $200-400")
print("   - Azure Functions (Consumption): $10-30")
print("   - Redis Cache (Basic C0): $16")
print("   - App Insights: $10-20")
print("   - App Service (B1): $13")
