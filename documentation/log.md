# Architecture Decision Records (ADRs)

# DevLog: Community AI Assistant — Engineering & Architecture Journey

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

## Entry 02: Looking at a few models
**Timestamp: June 22, 2026**

Started evaluating actual models to plug into the Ollama engine. Realized that frontier models (120B+ parameters) are too heavy for standard dorm server infrastructure, so the focus must remain on the 8B-32B parameter range.

Attempted to test **Racka-4B** (a newly released model from ELTE specifically optimized for Hungarian reasoning). Discovered Ollama's direct Hugging Face integration, but hit errors because Racka is a "Gated Model" requiring explicit academic licensing agreements on Hugging Face.

#### Strategic Pivot:

Instead of fighting with model weights, SSH keys, and general-knowledge testing, I am putting all model selection on pause.

#### TODO: Next Steps

* [x] **Build the Data Pipeline:** Write the Python script to load sample text files, chunk them using `langchain`, embed them, and save them to a local Milvus instance.

* [ ] **Chunking & Vector DB:** Implement LangChain splitters to chunk the Docling output, translate it using a Hungarian-capable embedding model and insert it into Milvus Lite.

* [ ] **Construct the RAG Prompt:** Create the strict system prompt.

* [ ] **Model Evaluation (Delayed):** Once the database works, test open-weights models (Llama 3, Qwen 2.5). (If the open models struggle with Hungarian RAG, log into Hugging Face, formally request academic access to `elte-nlp/Racka-4B` or the quantized model, set up the local SSH token, and test the ELTE model.)

* [ ] **Hugging Face Authorization:** Formally request academic access to `elte-nlp/Racka-4B`, set up the local SSH token, and test the ELTE model.

---

## Entry 03: Building the data pipeline
**Timestamp: June 24, 2026**

Began building the data ingestion pipeline (`ingest.py`) to process the documents, PDFs, and application forms.

#### Implementation Notes:
* **The Parser Upgrade:** Skipped legacy parsers (`PyPDFLoader`, `docx2txt`) entirely and integrated **Docling** (via `langchain-docling`). Docling uses internal AI layout models to preserve document structure, meaning the AI will actually understand tables, headers, and column reading orders instead of seeing scrambled text.
* **The OCR Bypass Strategy:** Encountered a PyTorch configuration error (`torch.PP-OCRv6.det.small`) because Docling was attempting to run an OCR vision model over the PDFs. Since almost all university documents are "born-digital" (exported directly from Word/Docs), I configured `PdfPipelineOptions` to explicitly disable OCR (`do_ocr = False`).
* **Result:** This bypasses the dependency crash, extracts the embedded digital text with 100% spelling accuracy, and runs faster than scanning pixels.

### The Native Vector Pivot & Overcoming Dependency Hell
**Timestamp: June 24, 2026**

* **The Milvus Lite Transition:** Officially discarded the initial ChromaDB concept. Chose **Milvus Lite** to enable seamless local development via a flat `.db` file while preserving identical code compatibility with the enterprise cluster models.

* **The Dependency Conflict:** Ran into severe dependency resolution failures using `uv add`. The root cause was dual-layered:
  1. `uv` attempted to resolve dependencies for future Python versions (>= 3.14), where Milvus binaries don't exist yet. Fixed by explicitly pinning the project bounds in `pyproject.toml` to `requires-python = ">=3.10, <3.14"`.
  2. The bleeding-edge `pymilvus` v3.0.0 release conflicted with LangChain's vector store wrappers, which still expect a v2.x architecture.

* **The Architecture Decision (The "Native" Shift):** Rather than implementing brittle connection hacks or pinning outdated dependencies to force LangChain's wrapper to behave, **I decided to drop the LangChain Milvus wrapper.** I bypassed it by writing the pipeline using the native, modern `MilvusClient` API provided directly by PyMilvus. This eliminates third-party translation layers, guarantees high-performance batch updates, gives me absolute control over schemas and metric indices (using `COSINE`), and allows dynamic unpacking of Docling metadata keys (`**metadata`).

Consolidated the vector database logic into a robust, object-oriented `DatabaseManager` class to cleanly handle connections, insertions, and searches without polluting the execution scripts.

As the pipeline grew, having database connection logic scattered across `build_database.py`, `test_search.py`, and the ingestion scripts became a liability. I executed a complete object-oriented refactor to centralize state management and cleanly decouple the execution scripts from the configuration.

---

#### Architectural Decisions:
* **Centralized Configuration (`config.py`):** Encountered a classic Circular Import error between the build script and the database scripts. I resolved this by extracting all global variables (`DB_PATH`, `DATA_DIR`, `COLLECTION_NAME`, `EMBEDDING_DIM`) into a dedicated `config.py` file. This establishes a single source of truth for the entire application.
* **The `DatabaseManager` Class:** Dropped the procedural scripts and built a unified `DatabaseManager` class to act as the single interface for Milvus.
  * It handles its own embeddings (`HuggingFaceEmbeddings`).
  * It dynamically builds the database schema and sets the `FLAT` index structure for perfect recall.
  * It handles vector insertion and automatically unpacks Docling's dynamic metadata (like source file names).
* **Memory Management (`load_collection`):** Discovered that Milvus vector searches crash if the collection is only resting on the hard drive (status 'released'). I updated the `DatabaseManager`'s `__init__` method to immediately load the collection into RAM upon connection. This ensures lightning-fast similarity searches the moment the FastAPI server boots up.

#### The Final Local Backend Architecture:
The core RAG backend is now reduced to five highly modular files:
1. `data/` *(Raw SSSL PDFs and documents)*
2. `config.py` *(Global environment and path variables)*
3. `ingest.py` *(Docling OCR-bypass extraction)*
4. `db_manager.py` *(The MilvusClient vector engine class)*
5. `build_database.py` *(Execution script to wipe and rebuild the `.db` file)*

---