# Project ECHO (v2) - Swarm Intelligence Framework

Project ECHO is a high-performance, multi-agent orchestration framework designed for real-time deep research and development automation. It utilizes a swarm-based architecture where specialized agents (Supervisor, Developer, Researcher, Critic) collaborate through a Unified Agent Communication Protocol (UACP) to solve complex user objectives.

## 🚀 Key Features

- **Real-Time Streaming (SSE/UACP)**: Instant, token-by-token and state-by-state streaming from the backend to the frontend.
- **Multi-Agent Hub**: A specialized UI for monitoring and filtering the swarm's internal reasoning process.
- **Semantic Memory Integration**: Utilizing an `IntelligenceLayer` to store and retrieve past task outcomes and research insights.
- **Local & Cloud Model Routing**: Dynamic routing between local GGUF models (e.g., Llama 3.1 8B) and high-performance cloud APIs (e.g., DeepSeek R1).
- **Self-Correcting Swarm**: A Critic Agent evaluates outputs in real-time, triggering recursive iterations if hallucinations or low confidence are detected.

## 🛠️ Components

### Backend (`/api`, `/ai-orchestrator`)

- **FastAPI Core**: High-throughput SSE endpoint for agent execution.
- **AgentManager**: Orchestrates the multi-agent execution loop and streams states.
- **IntelligenceLayer**: Vector and structured memory persistence.
- **Specialist Agents**:
  - `DevAgent`: Plans and implements code solutions.
  - `ResearchAgent`: Performs recursive deep research using search tools.
  - `CriticAgent`: Validates outputs for accuracy and hallucinations.

### Frontend (`/ai-ui`)

- **React/Vite Core**: Modern, performant UI with glassmorphism aesthetics.
- **Agent Toggle Bar**: Allows users to filter specific agent contributions in the chat stream.
- **Memory Traces**: Visual indicators of when the system utilizes its long-term memory.
- **Structured Data Cards**: Parsing technical JSON agent outputs into readable UI elements.

## 📦 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Local LLM models (GGUF format) in `/ai-orchestrator/models/`

### Launching the System

Use the bundled batch script to launch both the backend and frontend simultaneously:

```bash
launch_echo.bat
```

## 📈 Accomplishments (Phase 37)

- [x] Converted `/query` to Server-Sent Events (SSE).
- [x] Implemented `AgentManager.run_stream` for real-time orchestration.
- [x] Refined `DevAgent` and `ResearchAgent` for UACP compliance.
- [x] Added Agent visibility toggles to the UI.
- [x] Implemented rich card rendering for Critic/Dev outputs.
- [x] Fixed `MemoryAdapter` and `SystemTelemetry` regressions.

---
*Built with ❤️ by Project ECHO Development Swarm.*
