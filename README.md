# 🤖 AI Enterprise Assistant

> Enterprise-grade AI assistant combining **Retrieval-Augmented Generation (RAG)**, **AI Agent**, **secure Text-to-SQL**, **Document AI/OCR**, **Machine Learning**, and **Business Intelligence** in a unified web application.

AI Enterprise Assistant is a full-stack AI platform designed to demonstrate how modern AI technologies can be integrated into an enterprise environment.

The system combines document-based question answering, autonomous AI agents, structured database analysis, machine learning analytics, document processing, role-based access control, and business intelligence dashboards.

---

## ✨ Key Features

### 🧠 AI & RAG

* Retrieval-Augmented Generation (RAG)
* Hybrid document retrieval
* PostgreSQL Full-Text Search
* Vector similarity search with pgvector
* Reranking and citation support
* Prompt injection protection
* Multiple embedding providers
* Mock LLM mode for development without API keys

### 🤖 AI Agent

The AI Agent can combine multiple tools to solve complex business questions.

Available tools include:

* Document search
* Database query
* Sales analysis
* Growth calculation
* Forecasting
* Anomaly detection
* Report generation
* Calculator

Example:

> "Analyze September sales compared to August and explain the possible causes."

The agent can combine database queries, machine learning analysis, and document retrieval to produce a contextual answer.

---

## 📄 Document Intelligence

The platform supports enterprise document processing including:

* PDF
* DOCX
* XLSX
* CSV
* Images

Document processing pipeline:

```text
Document Upload
      ↓
Parser / OCR
      ↓
Text Cleaning
      ↓
Chunking
      ↓
Embedding
      ↓
Vector Database
      ↓
Hybrid Retrieval
      ↓
RAG / AI Agent
```

The system also includes document-level access control.

---

## 📊 Business Intelligence

The dashboard provides:

* Revenue overview
* Monthly sales analysis
* Branch performance
* Product/category performance
* Sales forecasting
* Anomaly detection
* AI usage monitoring
* Agent execution monitoring

---

## 📈 Machine Learning

The project includes two primary ML components.

### Sales Forecasting

Algorithm:

```text
GradientBoostingRegressor
```

Features include:

* Calendar features
* Lag 1
* Lag 7
* Lag 14
* Rolling statistics

Evaluation metrics:

* MAE
* RMSE
* MAPE
* Naive baseline comparison

### Anomaly Detection

Algorithm:

```text
Isolation Forest
```

The system detects unusual:

* Transaction amounts
* Quantities
* Prices
* Daily sales patterns

---

## 🔐 Security

Security is an important part of the architecture.

### Authentication

* JWT authentication
* Password hashing with bcrypt
* Role-based access control

Supported roles:

```text
ADMIN
MANAGER
EMPLOYEE
```

### SQL Agent Protection

The Text-to-SQL component includes several protections:

* SELECT/CTE only
* Table allowlist
* DDL/DML blocking
* SQL comment blocking
* PostgreSQL system table blocking
* Forced query limits
* Statement timeout
* Optional read-only database connection

### Prompt Injection Protection

Documents are treated as untrusted data.

The system detects and sanitizes common prompt injection patterns such as:

```text
Ignore previous instructions
Abaikan semua instruksi sebelumnya
Reveal the system prompt
Show the API key
```

### File Upload Protection

Uploaded files are protected using:

* Extension allowlist
* Magic-byte validation
* File size limitation
* Randomized file names
* Path traversal protection

### Rate Limiting

API requests are protected using Redis-based rate limiting with an in-memory fallback.

---

## 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │      Browser        │
                         │ React + TypeScript  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       Nginx         │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
          ┌─────────────────┐             ┌─────────────────┐
          │    Frontend     │             │     Backend     │
          │ React / Vite    │             │ FastAPI         │
          └─────────────────┘             └────────┬────────┘
                                                   │
                    ┌──────────────────────────────┼─────────────────────────┐
                    │                              │                         │
                    ▼                              ▼                         ▼
             ┌─────────────┐               ┌─────────────┐          ┌─────────────┐
             │     RAG     │               │ AI Agent    │          │     ML      │
             │ pgvector    │               │ Tool Calling│          │ Forecasting │
             │ FTS + RRF   │               │             │          │ Anomaly     │
             └──────┬──────┘               └──────┬──────┘          └─────────────┘
                    │                             │
                    └──────────────┬──────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │    PostgreSQL       │
                         │      pgvector       │
                         └─────────────────────┘

                         ┌─────────────────────┐
                         │       Redis         │
                         │ Queue / Rate Limit  │
                         └─────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* pgvector
* Redis
* Celery
* Scikit-learn
* PyMuPDF
* python-docx
* OpenPyXL
* Tesseract OCR

### Frontend

* React
* TypeScript
* Vite
* React Router
* Recharts
* React Markdown

### AI

* RAG
* LLM
* Embeddings
* AI Agent
* Function Calling
* Text-to-SQL
* Document AI
* OCR
* Machine Learning

### Infrastructure

* Docker
* Docker Compose
* Nginx

---

## 🚀 Quick Start

### Requirements

Make sure you have:

* Docker
* Docker Compose
* Git

Clone the repository:

```bash
git clone https://github.com/adiprabujayanegara01/ai-enterprise-assistant.git
cd ai-enterprise-assistant
```

Create environment configuration:

```bash
cp .env.example .env
```

For Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Start the application:

```bash
docker compose up --build
```

Open:

```text
http://localhost:8080
```

API documentation:

```text
http://localhost:8080/docs
```

---

## 🔑 LLM Configuration

The project supports a demo mode that does not require an external API key.

### Mock Mode

```env
LLM_PROVIDER=mock
```

This mode is suitable for:

* Development
* Portfolio demonstration
* Testing the RAG pipeline
* Testing the AI Agent architecture

### OpenAI-Compatible Provider

To use an external LLM:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=your_model
```

**Never commit your `.env` file or API key to GitHub.**

---

## 🔎 RAG Pipeline

The RAG pipeline follows:

```text
Upload Document
       ↓
Document Parsing / OCR
       ↓
Text Cleaning
       ↓
Chunking
       ↓
Embedding
       ↓
PostgreSQL + pgvector
       ↓
Hybrid Search
       ↓
Reranking
       ↓
Context Construction
       ↓
LLM
       ↓
Answer + Citation
```

---

## 🧪 Testing

Run backend tests:

```bash
docker compose exec backend pytest -q
```

The test suite covers:

* SQL security
* Calculator safety
* Document chunking
* Prompt injection sanitization
* Embedding consistency
* Date parsing
* Growth calculation

---

## 📁 Project Structure

```text
ai-enterprise-assistant/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── services/
│   │   ├── tools/
│   │   ├── utils/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── seed.py
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── types/
│   ├── package.json
│   └── Dockerfile
│
├── ml/
│   ├── forecasting/
│   ├── anomaly_detection/
│   └── notebooks/
│
├── docker/
│   ├── nginx/
│   └── postgres/
│
├── scripts/
│
├── documents/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## 📚 Example Use Cases

### 1. Enterprise Knowledge Assistant

Users can ask questions about internal policies and procedures.

Example:

> What is the reimbursement submission deadline?

The system retrieves relevant documents and provides an answer with citations.

### 2. Business Analysis

Managers can ask:

> What was the total sales by branch in August?

The AI Agent can generate and execute a controlled SQL query.

### 3. Sales Investigation

Example:

> Analyze the September sales decline and explain possible causes.

The agent can combine:

```text
SQL
+
Machine Learning
+
Document Retrieval
+
Business Context
```

### 4. Document Intelligence

Users can upload business documents and allow the system to:

* Extract text
* Perform OCR
* Index content
* Search information
* Answer questions
* Extract structured information

---

## 📊 Sample Data

The repository uses **synthetic sales data** for demonstration purposes.

The dataset does not represent real company transactions.

Sample data is generated during database seeding and includes:

* Multiple branches
* Multiple product categories
* Daily sales
* Artificial anomalies
* A simulated September sales decline

---

## 🔒 Security Notice

This project is intended as a portfolio and educational reference implementation.

Before deploying to production:

* Replace all default credentials
* Generate a strong JWT secret
* Configure a dedicated read-only database user
* Configure secure CORS origins
* Store secrets in a secure secret manager
* Enable HTTPS
* Review authentication and authorization policies
* Configure production rate limits
* Review file upload security
* Review database permissions
* Disable demo seed data where appropriate
* Perform security testing and dependency scanning

Never commit:

```text
.env
API keys
JWT secrets
database passwords
private certificates
production credentials
user data
```

---

## ⚠️ Current Limitations

This project is primarily intended for demonstration and portfolio purposes.

Current limitations include:

* Mock LLM is not equivalent to a production LLM
* Local hashing embeddings have lower semantic quality
* Sales data is synthetic
* SQL Agent currently uses a controlled table allowlist
* RBAC is implemented with a limited number of roles
* Production deployment hardening is still required
* End-to-end production testing depends on the deployment environment

---

## 🔮 Future Improvements

Potential improvements include:

* Advanced RAG evaluation with RAGAS
* Better embedding models
* Hybrid reranking with dedicated reranker models
* More enterprise document formats
* Multi-agent orchestration
* Advanced permission management
* SSO / OAuth2
* Observability with OpenTelemetry
* Prometheus and Grafana integration
* Advanced ML model monitoring
* Human-in-the-loop agent approval
* Production-grade secret management
* Automated CI/CD security scanning

---

## 👨‍💻 Project Purpose

This project was created as a portfolio project to demonstrate practical implementation of:

* Artificial Intelligence
* Generative AI
* Retrieval-Augmented Generation
* Large Language Models
* AI Agents
* Machine Learning
* Document Intelligence
* Business Intelligence
* Full-Stack Web Development
* Secure AI Application Architecture

---

## 📄 License

See the `LICENSE` file for licensing information.
