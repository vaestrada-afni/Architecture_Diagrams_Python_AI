# Azure Resource Request - RAG Chatbot MVP

> **Project:** RAG Chatbot POC  
> **Requested By:** [Your Name]  
> **Date:** February 2, 2026  
> **Estimated Monthly Cost:** $130-185

---

## Required Azure Resources

### 1. Azure AI Search
| Property | Value |
|----------|-------|
| **Service Name** | `rag-chatbot-search` (suggested) |
| **SKU** | Basic |
| **Region** | East US (or nearest) |
| **Replicas** | 1 |
| **Partitions** | 1 |
| **Semantic Search** | Enabled (Standard) |
| **Estimated Cost** | ~$75/month |

---

### 2. Azure OpenAI Service
| Property | Value |
|----------|-------|
| **Service Name** | `rag-chatbot-openai` (suggested) |
| **SKU** | Standard S0 |
| **Region** | East US (or region with GPT-5 availability) |
| **Estimated Cost** | ~$30-40/month (usage-based) |

#### Model Deployments Needed

| Model | Deployment Name | TPM Quota | Purpose |
|-------|-----------------|-----------|---------|
| **gpt-5-mini** | `gpt-5-mini` | 60,000 | Primary chat completion |
| **text-embedding-3-large** | `text-embedding-3-large` | 120,000 | Document & query embeddings |
| gpt-5 (optional) | `gpt-5` | 30,000 | Complex queries fallback |

> ⚠️ **Note:** Azure OpenAI requires approval. If not already approved, submit request at: https://aka.ms/oai/access

---

### 3. Azure Cosmos DB
| Property | Value |
|----------|-------|
| **Service Name** | `rag-chatbot-cosmos` (suggested) |
| **API** | NoSQL (Core) |
| **Capacity Mode** | **Serverless** |
| **Region** | East US |
| **Database Name** | `ragchatbot` |
| **Container Name** | `conversations` |
| **Partition Key** | `/conversation_id` |
| **Estimated Cost** | ~$5-20/month |

---

### 4. Azure Functions
| Property | Value |
|----------|-------|
| **Function App Name** | `rag-chatbot-func` (suggested) |
| **Plan** | **Consumption (Serverless)** |
| **Runtime** | Python 3.11 |
| **Region** | East US |
| **OS** | Linux |
| **Estimated Cost** | ~$10-30/month |

---

### 5. Azure Bot Service
| Property | Value |
|----------|-------|
| **Bot Name** | `rag-chatbot-bot` (suggested) |
| **SKU** | **F0 (Free)** |
| **Type** | Multi-Tenant |
| **Messaging Endpoint** | Will be configured after Function App deployment |
| **Channels** | Microsoft Teams |
| **Estimated Cost** | **$0 (Free)** |

---

### 6. Azure Key Vault
| Property | Value |
|----------|-------|
| **Vault Name** | `rag-chatbot-kv` (suggested) |
| **SKU** | Standard |
| **Region** | East US |
| **Estimated Cost** | ~$1/month |

---

### 7. Azure Application Insights
| Property | Value |
|----------|-------|
| **Name** | `rag-chatbot-insights` (suggested) |
| **Region** | East US |
| **Workspace** | Create new Log Analytics workspace |
| **Estimated Cost** | ~$10-20/month |

---

### 8. Azure Storage Account
| Property | Value |
|----------|-------|
| **Name** | `ragchatbotstorage` (suggested) |
| **Performance** | Standard |
| **Redundancy** | LRS (Locally Redundant) |
| **Access Tier** | Hot |
| **Purpose** | Function App storage + document backup |
| **Estimated Cost** | ~$5-10/month |

---

## Access & Permissions Required

### For Me (Developer)

| Resource | Role/Permission Needed |
|----------|------------------------|
| Resource Group | **Contributor** |
| Azure AI Search | Search Service Contributor |
| Azure OpenAI | Cognitive Services OpenAI User |
| Cosmos DB | Cosmos DB Account Reader + Data Contributor |
| Function App | Website Contributor |
| Key Vault | Key Vault Secrets User |
| Application Insights | Monitoring Contributor |
| Storage Account | Storage Blob Data Contributor |

### For the Application (Managed Identity)

Please enable **System-Assigned Managed Identity** on the Function App, then grant:

| Resource | Role for Managed Identity |
|----------|---------------------------|
| Azure AI Search | Search Index Data Contributor |
| Azure OpenAI | Cognitive Services OpenAI User |
| Cosmos DB | Cosmos DB Built-in Data Contributor |
| Key Vault | Key Vault Secrets User |
| Storage Account | Storage Blob Data Reader |

---

## Additional Requests

### 1. Microsoft Entra ID App Registration
| Property | Value |
|----------|-------|
| **App Name** | `rag-chatbot-app` |
| **Supported Account Types** | Single tenant |
| **Redirect URI** | Not required initially |
| **Purpose** | Bot Service authentication |

> The Bot Service will need an App ID and Secret. Please provide these securely via Key Vault.

### 2. Microsoft Teams Admin Approval
| Request | Details |
|---------|---------|
| **Custom App Sideloading** | Enable for development/testing |
| **Teams App Catalog** | Access to upload custom apps |
| **Bot Registration** | Approval to add bot to Teams |

### 3. SharePoint Access (For Document Indexing)
| Request | Details |
|---------|---------|
| **SharePoint Site** | Read access to document libraries |
| **Microsoft Graph API** | `Sites.Read.All` permission |
| **Service Principal** | For Azure AI Search indexer |

---

## Resource Group

Please create all resources in a single Resource Group:

| Property | Value |
|----------|-------|
| **Name** | `rg-rag-chatbot` (suggested) |
| **Region** | East US |
| **Tags** | `project: rag-chatbot`, `environment: dev` |

---

## Cost Summary

| Resource | Monthly Cost |
|----------|--------------|
| Azure AI Search (Basic) | $75 |
| Azure OpenAI (GPT-5-mini + Embeddings) | $30-40 |
| Azure Cosmos DB (Serverless) | $5-20 |
| Azure Functions (Consumption) | $10-30 |
| Azure Bot Service (Free) | $0 |
| Azure Key Vault | $1 |
| Application Insights | $10-20 |
| Storage Account | $5-10 |
| **TOTAL** | **$136-196/month** |

---

## ServiceNow IT Request Template

### Short Description (Title)
```
Request for Azure Resources - RAG Chatbot POC (8 services)
```

### Full Description (Details)
```
REQUEST TYPE: New Azure Resources
PROJECT: RAG Chatbot POC with Microsoft Teams Integration
ESTIMATED COST: $136-196/month

I am requesting approval and provisioning of the following Azure resources for a Retrieval-Augmented Generation (RAG) chatbot proof of concept that will be integrated with Microsoft Teams:

AZURE RESOURCES NEEDED:
1. Azure AI Search (Basic tier) - Vector search and hybrid search capabilities
2. Azure OpenAI Service (Standard S0) - GPT-5-mini and text-embedding-3-large model deployments
3. Azure Cosmos DB (NoSQL, Serverless) - Conversation history storage
4. Azure Functions (Consumption plan, Python 3.11) - RAG orchestration logic
5. Azure Bot Service (F0 Free tier) - Microsoft Teams integration
6. Azure Key Vault (Standard) - Secure credential storage
7. Azure Application Insights (with Log Analytics workspace) - Monitoring and diagnostics
8. Azure Storage Account (Standard LRS) - Function app storage and document backup

ADDITIONAL REQUIREMENTS:
- Microsoft Entra ID App Registration for bot authentication
- System-Assigned Managed Identity on Function App
- Contributor role access to Resource Group for development
- Microsoft Teams admin approval for custom app sideloading

RESOURCE GROUP:
- Name: rg-rag-chatbot
- Region: East US (or nearest available)

TIMELINE:
Development will take approximately 6 weeks after resources are provisioned.

BUSINESS JUSTIFICATION:
This chatbot will provide employees with intelligent, context-aware answers by retrieving information from our internal knowledge base, reducing response time and improving productivity.

Please see attached detailed specifications: AZURE_RESOURCE_REQUEST.md

Contact: [Your Name/Email]
```

---

## Quick Service List for Approval

**Copy/paste this list for quick approval:**

1. **Azure AI Search** (Basic tier)
2. **Azure OpenAI Service** (Standard S0 with GPT-5-mini + text-embedding-3-large models)
3. **Azure Cosmos DB** (NoSQL, Serverless)
4. **Azure Functions** (Consumption plan, Python 3.11)
5. **Azure Bot Service** (F0 Free tier)
6. **Azure Key Vault** (Standard)
7. **Azure Application Insights** (with Log Analytics workspace)
8. **Azure Storage Account** (Standard LRS)

**Additional Requirements:**
- Microsoft Entra ID App Registration (for bot authentication)
- Managed Identity enabled on Function App
- Developer access (Contributor role) to all resources
- Microsoft Teams admin approval for custom app sideloading

---

## Timeline

Once resources are provisioned, please provide:

1. ✅ Resource Group access (Contributor role)
2. ✅ Azure OpenAI endpoint and deployed model names
3. ✅ Bot App ID and Secret (stored in Key Vault)
4. ✅ SharePoint site URL for document indexing
5. ✅ Teams Admin approval for custom app sideloading

**Estimated development time after provisioning:** 6 weeks

---

## Questions?

Contact: [Your Email]

---

## Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Solutions Engineer | | | |
| IT Security | | | |
| Manager | | | |
