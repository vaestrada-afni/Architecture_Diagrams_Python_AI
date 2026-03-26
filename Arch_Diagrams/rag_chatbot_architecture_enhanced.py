"""
Azure RAG Chatbot Architecture - ENHANCED POC System
Based on RAG Implementation Best Practices (rag-engineer + rag-implementation skills)

Enhancements over original:
1. Hybrid Search (BM25 + Vector) with Reciprocal Rank Fusion
2. Reranking Layer (Cross-Encoder or Azure AI)
3. Semantic Chunking with document structure awareness
4. Multi-Query Retrieval for better recall
5. Parent-Child Document Strategy
6. Caching Layer (Redis) for performance
7. Evaluation Pipeline for quality assurance
8. Citation Tracking for transparency
9. Fallback/Guardrails for robustness
10. Query Analysis/Routing for intent detection
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users

# Azure Compute
from diagrams.azure.compute import FunctionApps, AppServices, ContainerInstances

# Azure AI/ML
from diagrams.azure.ml import AzureOpenAI, CognitiveServices

# Azure Search
from diagrams.azure.aimachinelearning import CognitiveSearch

# Azure Integration
from diagrams.azure.integration import APIManagement

# Azure Storage
from diagrams.azure.storage import BlobStorage, StorageAccounts

# Azure Cache
from diagrams.azure.database import CacheForRedis

# Azure Security & Identity
from diagrams.azure.identity import EntraConnect, ManagedIdentities

# Azure Analytics/Monitoring
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.devops import ApplicationInsights

# Azure Other
from diagrams.azure.other import ContainerAppsEnvironments

# SaaS
from diagrams.saas.chat import Teams

# Graph attributes for clean layout
graph_attr = {
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.2",
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5"
}

# Cluster styles
chat_cluster = {
    "fontsize": "13",
    "bgcolor": "#E8F5E9",
    "style": "rounded",
    "margin": "15"
}

orchestration_cluster = {
    "fontsize": "13",
    "bgcolor": "#E3F2FD",
    "style": "rounded",
    "margin": "15"
}

retrieval_cluster = {
    "fontsize": "13",
    "bgcolor": "#E1F5FE",
    "style": "rounded",
    "margin": "15"
}

generation_cluster = {
    "fontsize": "13",
    "bgcolor": "#F3E5F5",
    "style": "rounded",
    "margin": "15"
}

ingestion_cluster = {
    "fontsize": "13",
    "bgcolor": "#FFF3E0",
    "style": "rounded",
    "margin": "15"
}

evaluation_cluster = {
    "fontsize": "13",
    "bgcolor": "#FCE4EC",
    "style": "rounded",
    "margin": "15"
}

monitoring_cluster = {
    "fontsize": "13",
    "bgcolor": "#FFF9C4",
    "style": "rounded",
    "margin": "15"
}

security_cluster = {
    "fontsize": "13",
    "bgcolor": "#ECEFF1",
    "style": "rounded",
    "margin": "15"
}

caching_cluster = {
    "fontsize": "13",
    "bgcolor": "#E0F7FA",
    "style": "rounded",
    "margin": "15"
}

# Create enhanced diagram
with Diagram(
    "RAG Chatbot Architecture - Enhanced POC\n(Based on RAG Engineering Best Practices)",
    filename="diagrams/rag_chatbot_architecture_enhanced",
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
    
    # ========== API GATEWAY ==========
    apim = APIManagement("API Gateway\n(Rate Limiting,\nAuth)")
    
    # ========== RAG ORCHESTRATION ==========
    with Cluster("RAG Orchestration Layer", graph_attr=orchestration_cluster):
        rag_api = FunctionApps("RAG Orchestrator\n(LangGraph/\nSemantic Kernel)")
        
        # NEW: Query Analysis
        query_analyzer = FunctionApps("Query Analyzer\n(Intent Detection,\nMulti-Query Gen)")
    
    # ========== CACHING LAYER (NEW) ==========
    with Cluster("Caching Layer", graph_attr=caching_cluster):
        semantic_cache = CacheForRedis("Semantic Cache\n(Azure Redis)\nSimilar Queries")
    
    # ========== RETRIEVAL LAYER (ENHANCED) ==========
    with Cluster("Hybrid Retrieval Layer", graph_attr=retrieval_cluster):
        # Vector Search
        weaviate = ContainerAppsEnvironments("Weaviate Vector DB\n(Container Apps)\nDense Retrieval")
        
        # NEW: BM25 Keyword Search
        keyword_search = CognitiveSearch("BM25 Index\n(Weaviate/\nAzure Search)\nSparse Retrieval")
        
        # NEW: Reciprocal Rank Fusion
        rrf_fusion = FunctionApps("RRF Fusion\n(Hybrid Results\nCombination)")
        
        # NEW: Reranking
        reranker = ContainerInstances("Reranker\n(Cross-Encoder/\nCohere Rerank)")
    
    # ========== GENERATION LAYER ==========
    with Cluster("Generation Layer", graph_attr=generation_cluster):
        # Azure OpenAI
        aoai_embeddings = AzureOpenAI("Azure OpenAI\nEmbeddings\n(text-embedding-3)")
        aoai_llm = AzureOpenAI("Azure OpenAI LLM\nGPT-4o/4.1\n(with Citations)")
        
        # NEW: Guardrails
        guardrails = FunctionApps("Guardrails\n(Content Safety,\nGrounding Check)")
    
    # ========== KNOWLEDGE SOURCE ==========
    sharepoint = CognitiveSearch("SharePoint Online\nDocument Libraries")
    
    # ========== INGESTION PIPELINE (ENHANCED) ==========
    with Cluster("Ingestion & Indexing Pipeline", graph_attr=ingestion_cluster):
        ingestion_worker = FunctionApps("Ingestion Worker\n(Delta Sync)")
        blob_staging = BlobStorage("Blob Storage\nStaging")
        text_extractor = ContainerInstances("Document Parser\n(Unstructured.io)\nPDF/DOCX/PPTX")
        
        # ENHANCED: Semantic Chunking
        semantic_chunker = FunctionApps("Semantic Chunker\n(Structure-Aware,\nOverlap, Metadata)")
        
        # NEW: Parent-Child Strategy
        parent_indexer = FunctionApps("Parent-Child\nIndexer\n(Multi-Level)")
    
    # ========== EVALUATION PIPELINE (NEW) ==========
    with Cluster("Evaluation & Quality", graph_attr=evaluation_cluster):
        eval_pipeline = FunctionApps("Eval Pipeline\n(RAGAS Metrics)")
        test_dataset = BlobStorage("Test Dataset\n(50+ Q&A Pairs)")
        feedback_loop = FunctionApps("User Feedback\nCollection")
    
    # ========== SECURITY ==========
    with Cluster("Security & Auth", graph_attr=security_cluster):
        entra_id = EntraConnect("Microsoft\nEntra ID")
        managed_id = ManagedIdentities("Managed\nIdentities")
    
    # ========== MONITORING ==========
    with Cluster("Observability & Tracing", graph_attr=monitoring_cluster):
        app_insights = ApplicationInsights("Application\nInsights\n(Custom Metrics)")
        log_analytics = LogAnalyticsWorkspaces("Log Analytics\n(Query Traces,\nRetrieval Scores)")
    
    # ===== USER FLOW =====
    users >> Edge(label="Chat") >> [teams, web_app]
    teams >> Edge(label="HTTPS") >> apim
    web_app >> Edge(label="HTTPS") >> apim
    apim >> Edge(label="HTTPS") >> rag_api
    
    # ===== RAG ORCHESTRATION FLOW =====
    rag_api >> Edge(label="1. Analyze\nQuery") >> query_analyzer
    
    # ===== CACHING CHECK =====
    query_analyzer >> Edge(label="2. Cache\nLookup", style="dashed") >> semantic_cache
    
    # ===== EMBEDDING & RETRIEVAL =====
    query_analyzer >> Edge(label="3. Embed\nQuery") >> aoai_embeddings
    aoai_embeddings >> Edge(label="4a. Vector\nSearch") >> weaviate
    query_analyzer >> Edge(label="4b. Keyword\nSearch") >> keyword_search
    
    # ===== HYBRID FUSION & RERANKING =====
    weaviate >> Edge(label="Dense\nResults") >> rrf_fusion
    keyword_search >> Edge(label="Sparse\nResults") >> rrf_fusion
    rrf_fusion >> Edge(label="5. Rerank\nTop-K") >> reranker
    
    # ===== GENERATION =====
    reranker >> Edge(label="6. Top-K\nChunks") >> rag_api
    rag_api >> Edge(label="7. Prompt +\nContext") >> aoai_llm
    aoai_llm >> Edge(label="8. Answer +\nCitations") >> guardrails
    guardrails >> Edge(label="9. Validated\nResponse") >> rag_api
    rag_api >> Edge(label="Response") >> apim
    
    # ===== INGESTION FLOW =====
    sharepoint >> Edge(label="Graph API\n(Delta Query)") >> ingestion_worker
    ingestion_worker >> Edge(label="Raw files") >> blob_staging
    ingestion_worker >> Edge(label="Extract") >> text_extractor
    text_extractor >> Edge(label="Structure-aware\nChunks") >> semantic_chunker
    semantic_chunker >> Edge(label="Parent +\nChild Chunks") >> parent_indexer
    parent_indexer >> Edge(label="Embed") >> aoai_embeddings
    aoai_embeddings >> Edge(label="Index Vectors") >> weaviate
    semantic_chunker >> Edge(label="Index Keywords") >> keyword_search
    
    # ===== EVALUATION FLOW =====
    rag_api >> Edge(label="Eval\nRequests", style="dotted", color="purple") >> eval_pipeline
    test_dataset >> Edge(label="Test\nCases", style="dotted") >> eval_pipeline
    eval_pipeline >> Edge(label="Metrics") >> log_analytics
    users >> Edge(label="Feedback", style="dotted", color="green") >> feedback_loop
    feedback_loop >> Edge(label="Quality\nSignals") >> eval_pipeline
    
    # ===== SECURITY =====
    [teams, web_app] >> Edge(label="User Auth", style="dashed", color="gray") >> entra_id
    rag_api >> Edge(label="Managed\nIdentity", style="dashed", color="gray") >> managed_id
    rag_api >> Edge(label="Graph API\nPermissions", style="dashed", color="gray") >> sharepoint
    
    # ===== MONITORING =====
    rag_api >> Edge(label="traces", style="dashed", color="orange") >> app_insights
    reranker >> Edge(label="scores", style="dashed", color="orange") >> app_insights
    weaviate >> Edge(label="metrics", style="dashed", color="orange") >> app_insights
    ingestion_worker >> Edge(label="logs", style="dashed", color="orange") >> app_insights
    eval_pipeline >> Edge(label="quality\nmetrics", style="dashed", color="orange") >> app_insights
    app_insights >> log_analytics

print("=" * 60)
print("✅ ENHANCED RAG Chatbot Architecture Diagram generated!")
print("=" * 60)
print("\n📁 Output files:")
print("   - diagrams/rag_chatbot_architecture_enhanced.png")
print("   - diagrams/rag_chatbot_architecture_enhanced.dot")
print("\n🆕 Key Enhancements over Original:")
print("   1. ✅ Hybrid Search (Vector + BM25 with RRF)")
print("   2. ✅ Reranking Layer (Cross-Encoder)")
print("   3. ✅ Semantic Chunking (Structure-Aware)")
print("   4. ✅ Multi-Query Generation (Query Analyzer)")
print("   5. ✅ Parent-Child Document Strategy")
print("   6. ✅ Semantic Caching (Redis)")
print("   7. ✅ Evaluation Pipeline (RAGAS)")
print("   8. ✅ Citation Tracking (in LLM prompt)")
print("   9. ✅ Guardrails (Content Safety)")
print("  10. ✅ User Feedback Loop")
print("\n📊 Based on: rag-implementation & rag-engineer agent skills")
