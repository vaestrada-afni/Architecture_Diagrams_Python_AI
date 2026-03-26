"""
Azure RAG Chatbot Architecture - POC System
Weaviate on Azure Container Apps with SharePoint Knowledge Base

Updated with latest Azure icons from diagrams 0.25.1 (Nov 2025)
- Using azure.ml.AzureOpenAI for Azure OpenAI services
- Using azure.aimachinelearning.AIStudio for AI capabilities
- Using azure.identity.EntraConnect for Entra ID
- Using azure.other.ContainerAppsEnvironments for Container Apps
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users

# Azure Compute
from diagrams.azure.compute import FunctionApps, AppServices, ContainerInstances

# Azure AI/ML - Updated with proper Azure OpenAI icon
from diagrams.azure.ml import AzureOpenAI, CognitiveServices
from diagrams.azure.aimachinelearning import AIStudio, CognitiveSearch

# Azure Integration
from diagrams.azure.integration import APIManagement

# Azure Storage
from diagrams.azure.storage import BlobStorage, StorageAccounts

# Azure Security & Identity - Using correct Entra classes
from diagrams.azure.identity import EntraConnect, ManagedIdentities

# Azure Analytics/Monitoring
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.devops import ApplicationInsights

# Azure Other - Container Apps and more
from diagrams.azure.other import ContainerAppsEnvironments

# Azure Web
from diagrams.azure.web import AppServices as WebAppServices

# SaaS
from diagrams.saas.chat import Teams

# Custom for Weaviate (using container representation)
from diagrams.azure.database import CosmosDb  # Proxy for vector DB visual

# Graph attributes for clean layout
graph_attr = {
    "splines": "ortho",
    "nodesep": "1.0",
    "ranksep": "1.5",
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5"
}

# Cluster attributes
user_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#E8F5E9",  # Light Green
    "style": "rounded",
    "margin": "15"
}

rag_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#E3F2FD",  # Light Blue
    "style": "rounded",
    "margin": "15"
}

ingestion_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#FFF3E0",  # Light Orange
    "style": "rounded",
    "margin": "20"
}

monitoring_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#FFF9C4",  # Light Yellow
    "style": "rounded",
    "margin": "15"
}

security_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#F3E5F5",  # Light Purple
    "style": "rounded",
    "margin": "15"
}

# Create diagram
with Diagram(
    "RAG Chatbot Architecture - POC",
    filename="diagrams/rag_chatbot_architecture",
    direction="TB",
    graph_attr=graph_attr,
    outformat=["png", "dot"],
    show=False
):
    
    # Users
    users = Users("Users\n(≈50)")
    
    # Chat Interface Layer
    with Cluster("Chat Interface", graph_attr=user_cluster_attr):
        teams = Teams("Teams Chat")
        web_app = AppServices("Web App\nChat UI")
    
    # Optional API Gateway
    apim = APIManagement("API Gateway\n(optional)\nAzure API Mgmt")
    
    # RAG Orchestration Layer
    with Cluster("RAG Orchestration", graph_attr=rag_cluster_attr):
        rag_api = FunctionApps("RAG Orchestrator\nAzure Functions\n/ App Service")
        
        # Azure OpenAI Services - Using proper AzureOpenAI icon
        aoai_embeddings = AzureOpenAI("Azure OpenAI\nEmbeddings")
        aoai_llm = AzureOpenAI("Azure OpenAI\nLLM\n(GPT-4o/4.1)")
        
        # Weaviate Vector DB on Container Apps
        weaviate = ContainerAppsEnvironments("Weaviate\nVector DB\n(Container Apps\n1 replica)")
    
    # SharePoint Knowledge Base - Using Cognitive Search as proxy
    sharepoint = CognitiveSearch("SharePoint\nOnline\nDocument Libs")
    
    # Ingestion Pipeline
    with Cluster("Ingestion & Indexing Pipeline", graph_attr=ingestion_cluster_attr):
        ingestion_worker = FunctionApps("Ingestion\nWorker\nFunctions/\nContainer Job")
        blob_staging = BlobStorage("Blob Storage\nStaging\n(optional)")
        text_extractor = ContainerInstances("Text Extractor\nUnstructured/\nTika")
        chunker = FunctionApps("Chunker\n+ Metadata")
    
    # Security & Auth - Using EntraConnect for modern Entra ID representation
    with Cluster("Security & Auth", graph_attr=security_cluster_attr):
        entra_id = EntraConnect("Microsoft\nEntra ID")
        managed_id = ManagedIdentities("Managed\nIdentities")
    
    # Monitoring
    with Cluster("Observability", graph_attr=monitoring_cluster_attr):
        app_insights = ApplicationInsights("Application\nInsights")
        log_analytics = LogAnalyticsWorkspaces("Log Analytics\nWorkspace")
    
    # ===== User Flow =====
    users >> Edge(label="Chat") >> [teams, web_app]
    teams >> Edge(label="HTTPS") >> apim
    web_app >> Edge(label="HTTPS") >> apim
    apim >> Edge(label="HTTPS") >> rag_api
    
    # ===== RAG Flow =====
    rag_api >> Edge(label="Embed query") >> aoai_embeddings
    rag_api >> Edge(label="Vector +\nHybrid Search") >> weaviate
    rag_api >> Edge(label="Top-k chunks\n+ prompt") >> aoai_llm
    aoai_llm >> Edge(label="Answer +\ncitations") >> rag_api
    rag_api >> Edge(label="Response") >> apim
    
    # ===== Ingestion Flow =====
    sharepoint >> Edge(label="Graph API") >> ingestion_worker
    ingestion_worker >> Edge(label="Raw files") >> blob_staging
    ingestion_worker >> Edge(label="Extract text\nPDF/DOCX/PPTX") >> text_extractor
    text_extractor >> Edge(label="Chunk +\nmetadata") >> chunker
    chunker >> Edge(label="Embed\nchunks") >> aoai_embeddings
    aoai_embeddings >> Edge(label="Vectors") >> weaviate
    
    # ===== Security & Auth =====
    teams >> Edge(label="User auth", style="dashed") >> entra_id
    web_app >> Edge(label="User auth", style="dashed") >> entra_id
    rag_api >> Edge(label="Managed\nIdentity", style="dashed") >> entra_id
    rag_api >> Edge(label="Graph\npermissions", style="dashed") >> sharepoint
    
    # ===== Monitoring =====
    rag_api >> Edge(label="logs", style="dashed", color="orange") >> app_insights
    weaviate >> Edge(label="logs", style="dashed", color="orange") >> app_insights
    ingestion_worker >> Edge(label="logs", style="dashed", color="orange") >> app_insights
    app_insights >> log_analytics

print("✅ RAG Chatbot Architecture Diagram generated successfully!")
print("📁 Output files:")
print("   - diagrams/rag_chatbot_architecture.png")
print("   - diagrams/rag_chatbot_architecture.dot")

# Try to convert to draw.io format (if graphviz2drawio is available)
try:
    import subprocess
    print("\n🔄 Converting to draw.io format...")
    subprocess.run([
        "graphviz2drawio",
        "diagrams/rag_chatbot_architecture.dot",
        "-o",
        "diagrams/rag_chatbot_architecture.drawio"
    ], check=True)
    print("   - diagrams/rag_chatbot_architecture.drawio")
    print("\n✨ All formats generated successfully!")
except FileNotFoundError:
    print("⚠️  graphviz2drawio not found. Install with: pip install graphviz2drawio")
    print("   (Requires pygraphviz which needs Microsoft Visual C++ Build Tools)")
except Exception as e:
    print(f"⚠️  Draw.io conversion failed: {e}")
    print("   PNG and DOT files are still available.")
