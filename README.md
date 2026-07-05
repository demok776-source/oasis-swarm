# OASIS (Omni-Eternity Layer) 🌌

Welcome to **OASIS** — a state-of-the-art autonomous microservice swarm architecture designed to integrate AI agents, real-time messaging, and vector databases into a unified "Omni-Eternity Layer".

## 🚀 Features

- **Autonomous Agent Swarm**: Features specialized agents (DevOps Agent, Data Agent, etc.) powered by local LLMs (Llama 3) via Ollama.
- **Event-Driven Architecture**: Fully integrated with **Apache Kafka** and **Zookeeper** for asynchronous, high-throughput message passing between modules.
- **Vector Knowledge Base**: Uses **Qdrant** for semantic search and long-term agent memory.
- **Real-time Sync Layer**: Powered by **Redis** Pub/Sub for instant module synchronization.
- **Persistent Storage**: Uses **PostgreSQL** for relational data and historical event logging.
- **Modern UI**: A futuristic Next.js frontend (OASIS v5) simulating the JARVIS Terminal.
- **Containerized**: Everything runs seamlessly out of the box via `docker-compose`.

## 🏗️ Architecture

OASIS consists of several interconnected docker containers:
- `oasis-app-tier`: The FastAPI brain (Triage Agent) routing requests to sub-agents via LangChain.
- `oasis-oasis-v5`: The Next.js React frontend (JARVIS Terminal).
- `oasis-kafka` & `oasis-zookeeper`: The nervous system for background events.
- `oasis-ollama`: Local LLM inference engine running Llama 3.
- `oasis-qdrant`: Vector database for RAG (Retrieval-Augmented Generation).
- `oasis-postgres` & `oasis-redis`: Standard database and caching layers.
- `oasis-grafana`: Monitoring and telemetry dashboard.

## 🛠️ Quick Start

### Prerequisites
- Docker & Docker Compose
- A CPU/GPU capable of running local LLMs (at least 8GB RAM for Llama 3 8B).

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/oasis.git
   cd oasis
   ```

2. Start the Swarm:
   ```bash
   docker-compose up -d --build
   ```

3. Download the Llama 3 Model (if not already downloaded):
   ```bash
   docker exec -it oasis-ollama-1 ollama run llama3
   ```

4. Access the UI:
   - Open your browser and navigate to `http://localhost:3000` to access the JARVIS Terminal.

> **Note:** The first request to the local LLM may take 3-5 minutes on a CPU as the model weights are loaded into memory. Subsequent requests will be much faster.

## 🤝 Contributing
Hackers and developers worldwide are welcome to contribute! You can:
- Add new specialized LangGraph agents to the `app-tier`.
- Connect new modules to the Kafka event bus.
- Improve the frontend UI/UX.

## 📜 License
MIT License. Open source for the world!
