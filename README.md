# AI Shopping Assistant - "The Smart Consultant"

A sophisticated, RAG-powered voice shopping assistant that mimics a high-end photography & audio equipment consultant. It features real-time voice interaction, strict needs analysis, and curated recommendations.

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Tech Stack](https://img.shields.io/badge/Stack-React%20%7C%20Flask%20%7C%20RAG-blue)

## 🌟 Key Features

### 1. "Smart Consultant" Logic
Unlike generic chatbots, this assistant follows a strict 3-phase consulting process:
- **Phase 1: Needs Analysis**: Pauses to ask clarifying questions for broad requests (e.g., "I need a camera" -> "Vlogging or Cinema?").
- **Phase 2: Deep Search**: Uses Hybrid Search (Keyword + Semantic) to find products in the local ChromaDB.
- **Phase 3: Curated Presentation**: filters results to present **ONLY the top 1-2 best options** with personalized reasoning.

### 2. Strict Behavioral Guardrails
- **Absolute Whitelist**: Discusses **ONLY** Cameras, Lenses, Audio, and Lighting.
- **Explicit Blacklist**: Immediately refuses to discuss Software, Code Editors, Computers, or General knowledge.
- **Zero Hallucination**: Strict "Database Grounding" means it never recommends products not in stock.

### 3. Voice-First Interface
- **Always-On Mic**: Continuous listening for seamless conversation.
- **Live Transcript**: Real-time display of user speech and AI responses.
- **Orb Visualizer**: Reactive audio visualizer for AI speech.
- **ElevenLabs TTS**: High-quality, lifelike voice output.

## 🏗️ Architecture

### Frontend (`/frontend_react`)
- **Framework**: React 18 + Vite
- **UI Library**: Material UI (MUI)
- **State**: Custom `useAssistant` hook for managing WebSockets, Audio, and UI state.

### Backend (`/`)
- **API**: Flask
- **LLM**: Ollama (Llama 3 / Mistral)
- **RAG Engine**:
  - **DB**: ChromaDB (Vector Store)
  - **Embeddings**: `all-MiniLM-L6-v2` (Sentence Transformers)
  - **Search**: Hybrid (BM25 + Cosine Similarity)
- **TTS**: ElevenLabs API

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- Node.js 18+
- [Ollama](https://ollama.ai/) running locally
- ElevenLabs API Key

### 1. Clone & Install Backend
```bash
git clone https://github.com/someone5119819-creator/AI-Shopping-Assistant.git
cd AI-Shopping-Assistant

# Create Virtual Env
python3 -m venv venv
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root:
```ini
FLASK_APP=assistant_api.py
FLASK_ENV=development
OLLAMA_HOST=http://localhost:11434
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=your_voice_id
```

### 3. Install Frontend
```bash
cd frontend_react
npm install
```

### 4. Run the System
**Terminal 1 (Backend)**:
```bash
source venv/bin/activate
python assistant_api.py
# Runs on http://localhost:8001
```

**Terminal 2 (Frontend)**:
```bash
cd frontend_react
npm run dev
# Runs on http://localhost:5174
```

## 📖 Usage Guide

1. **Open the App**: Navigate to `http://localhost:5174`.
2. **Click "Start Assistant"**: Grant microphone permissions.
3. **Speak Naturally**:
   - *"I need a camera for vlogging."* (AI will ask clarifying questions)
   - *"Do you have the Sony A7?"* (AI will search and confirm)
   - *"Write me a python script"* (AI will refuse - strict constraint)

## 📂 Project Structure

```
├── assistant_api.py        # Main Flask Application & System Prompt
├── api.py                  # Initial RAG API (Legacy/Reference)
├── data_processor.py       # ETL script for Shopify products -> ChromaDB
├── hybrid_search.py        # Search Logic (Semantic + Keyword)
├── frontend_react/         # React Application Source
└── requirements.txt        # Python Dependencies
```

## 🛡️ License
MIT
