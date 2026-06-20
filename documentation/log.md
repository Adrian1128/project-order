# Architecture Decision Records (ADRs)

# DevLog: SSSL Community AI Assistant — Engineering & Architecture Journey

## Entry 01: The Foundation & The Blueprint
**Timestamp: June 19, 2026**

Starting the project today. The goal is to build an intelligent assistant for the SSSL community in the dorms to help first-year students navigate university life, regulations, and event logistics.

I need to make sure the architecture is clean from day one so that if I want to swap out the SSSL data for another context later, I don't have to rewrite the entire application. The data itself is at the bottom of my priority queue right now. Establishing the pipeline and engineering workflow is what matters most.

#### Architectural Decisions:
* **The Stack Split:** I decided to split the project into two completely decoupled directories: `/frontend` and `/backend`. No mixing of Python and JavaScript dependencies.
* **The Dual Package Manager Setup:**
  * For the frontend, I’m running **Next.js** and **React**. I chose **pnpm** because it's incredibly fast and efficient with disk space.
  * For the backend, I’m using **FastAPI**. Instead of standard `pip`, I opted for **uv**. It’s a modern, Rust-based tool that installs heavy Machine Learning binaries almost instantly.
* **The Language Choice:** I briefly considered doing a unified TypeScript stack with Next.js and NestJS. However, since my long-term goal is to dive deep into Machine Learning and MLOps, keeping the backend natively in **Python** is non-negotiable. Forcing data science libraries into TypeScript wrappers would add unnecessary friction.

---

### Connecting the Plumbing
**Timestamp: June 19, 2026**

#### Implementation Notes:
* **CORS Configuration:** Manually configured `CORSMiddleware` in FastAPI. Since Next.js runs on port 3000 and FastAPI on port 8000, the browser's Same-Origin Policy will block requests unless the backend explicitly whitelists port 3000.
* **The Network Bridge:** Wrote a simple boilerplate connection. The frontend captures input using a strictly typed React form event (`React.FormEvent`), passes it to a browser `fetch` request, and the backend verifies the data payload structure using a Pydantic model before sending a mock reply back. The plumbing works.

---

### The AI & Data Strategy

Mapping out Phase 1 of the AI implementation. I need to choose how the model gets its knowledge.

#### Strategic Choices:
* **RAG over Fine-Tuning:** I am explicitly choosing **Retrieval-Augmented Generation (RAG)** over Parameter-Efficient Fine-Tuning (LoRA). The model needs to answer strict, factual questions about dorm rules and event dates. Fine-tuning modifies the model's behavior/tone but is highly prone to hallucinating facts. RAG allows the model to act as an open-book reasoning engine, fetching exact snippets from a verified database.
* **The Toolkit:** I am adding `langchain` as the orchestrator to glue the pieces together, and `sentence-transformers` for creating the mathematical embeddings of the text.
* **The Database:** I'm starting with **ChromaDB** for rapid local prototyping since it runs as a lightweight file on my hard drive without requiring complex infrastructure today.

---

### The Production & MLOps Roadmap

Looking ahead at how to transform this local prototype into a massive portfolio piece. Once the core RAG loop is working, I will layer on a modern MLOps stack using **Docker Desktop** to containerize the environments.

#### Future Stack Layout:
* **Data Versioning:** Git is awful at tracking PDFs and datasets, so I will integrate **DVC (Data Version Control)** to version-control the text files.
* **Orchestration & Experimentation:** I will use **Prefect** to automate data ingestion pipelines and **MLflow** to track prompt engineering iterations and embedding models.
* **Production Observability:** For true production-grade monitoring, I will likely migrate from ChromaDB to **Milvus** because it natively exports metrics. I will hook this up to **Prometheus** to scrape performance data and **Grafana** to build dashboards tracking metrics.

---

### Deployment Strategy & Model Engine

Designing the application to be completely infrastructure-agnostic so it can be developed locally but seamlessly handed off to the Schönherz dev team for server deployment later.

#### Strategic Choices:
* **The "Local Now, Server Later" Architecture:** Decided to separate the execution engine from the model weights.
* **The Engine (Ollama):** I am using **Ollama** as the local execution runner. It exposes a local API that LangChain can talk to instantly. When it is time to deploy to the dorm's servers, I can just wrap Ollama in a Docker container without changing any of my Python backend code.

---

## TODO: Model Evaluation List
*Need to test these (and/or other) models locally to see which handles Hungarian language RAG best:*

* [ ] **Llama 3 (8B):** Meta's lightweight model. Highly capable of following strict RAG instructions, but need to test if it defaults back to English when confused.
* [ ] **Qwen 2.5 (7B):** Alibaba's open-source model. Excellent multilingual benchmarks; might write more natural-sounding Hungarian than Llama.
* [ ] **Aya 23 (8B):** Cohere's open-weights model designed explicitly for global language performance. High potential for local Hungarian inference.