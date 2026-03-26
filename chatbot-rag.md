# POC System Architecture — RAG Chatbot (Weaviate on Azure Container Apps)

Below is a **final POC architecture** that keeps everything Azure-native, avoids AKS, and supports SharePoint as the knowledge base.

## Mermaid architecture diagram

```mermaid
flowchart LR

%% =====================
%% Users + Channels
%% =====================
U[Users (≈50)] -->|Chat| CH[Chat UI
Teams / Web App]
CH -->|HTTPS| APIM[API Gateway (optional)
Azure API Management]
APIM -->|HTTPS| RAG[RAG Orchestrator API
Azure Functions or App Service]

%% =====================
%% Retrieval + Gen
%% =====================
RAG -->|Embed query| AOAIe[Azure OpenAI
Embeddings]
RAG -->|Vector + Hybrid Search| WVT[Weaviate Vector DB
Azure Container Apps
(1 replica, persistent storage)]
RAG -->|Top-k chunks + prompt| AOAIl[Azure OpenAI
LLM (GPT-4o/4.1/etc.)]
AOAIl -->|Answer + citations| RAG
RAG -->|Response| CH

%% =====================
%% Ingestion Pipeline
%% =====================
subgraph ING[Ingestion & Indexing Pipeline]
SP[SharePoint Online
Document Libraries] -->|Graph API| ING1[Ingestion Worker
Azure Functions / Container Job]
ING1 -->|Raw files| BLB[(Azure Blob Storage
Staging - optional)]
ING1 -->|Extract text
PDF/DOCX/PPTX/HTML| EX[Text Extractor
(Unstructured/Tika/etc.)]
EX -->|Chunk + metadata
(title, url, site, dept, effective date)| CHK[Chunker + Metadata]
CHK -->|Embed chunks| AOAIe
AOAIe -->|Vectors| UPS[Upsert Objects
+ metadata]
UPS --> WVT
end

%% =====================
%% Security / Auth
%% =====================
CH -->|User auth| AAD[Microsoft Entra ID]
RAG -->|Managed Identity / App Registration| AAD
RAG -->|Graph permissions| SP

%% =====================
%% Observability
%% =====================
RAG --> LOG[App Insights / Log Analytics]
WVT --> LOG
ING1 --> LOG

%% =====================
%% Notes
%% =====================
classDef opt fill:#f6f6f6,stroke:#999,stroke-dasharray: 4 2;
class APIM,BLB opt;
```

## Component responsibilities

### 1) Chat UI (Teams/Web)

* Collects user messages
* Displays answer + citations

### 2) RAG Orchestrator API (Functions/App Service)

* AuthN/AuthZ (Entra ID)
* Query rewriting (optional)
* Embeds the user query (Azure OpenAI embeddings)
* Retrieves Top‑K chunks from Weaviate
* Constructs grounded prompt + citations
* Calls Azure OpenAI LLM for final answer
* Logs traces (retrieval scores, doc IDs, tokens, latency)

### 3) Weaviate on Azure Container Apps

* Stores chunks + embeddings + metadata
* Provides vector + (optional) hybrid retrieval
* Uses **persistent storage** (Azure Files mount) so the index survives restarts

### 4) Ingestion & Indexing Pipeline

* Pulls SharePoint files via Microsoft Graph
* Extracts text (PDF/DOCX/etc.)
* Chunks content + attaches metadata
* Creates embeddings once per chunk
* Upserts into Weaviate
* Runs on schedule (or delta-based)

### 5) Observability

* App Insights / Log Analytics
* Capture: query, retrieved sources, confidence signals, user feedback

## POC defaults that keep this simple

* **No AKS** (Container Apps single replica)
* Start with **public ingress restricted by IP** or **internal ingress** if required
* Keep scope: **1 SharePoint site/library** first
* Add evaluation: 20–50 questions with expected source docs

## Minimal production upgrades (after POC)

* Private networking (VNet + internal ingress)
* Secrets in Key Vault
* CI/CD pipeline
* Multiple replicas + rolling upgrades (or move to AKS if needed)
* Backups for Weaviate persisted data
