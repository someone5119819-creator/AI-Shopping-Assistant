# Voice-First AI Shopping Consultant (Gemini Pro Edition)

> **"The Smart Consultant"** — An uncompromisingly guardrailed, voice-enabled AI shopping assistant powered by Google Gemini 3 Pro, ElevenLabs, and reactively synchronized frontend logic.

![Status](https://img.shields.io/badge/Status-Production_Ready-success)
![Brain](https://img.shields.io/badge/Brain-Gemini_3_Pro-blue)
![Voice](https://img.shields.io/badge/Voice-ElevenLabs_Turbo_v2-orange)
![Search](https://img.shields.io/badge/Search-Hybrid_RAG-green)

---

## 📚 Documentation Hub
For a deep dive into specific components, please refer to our high-fidelity technical guides:

*   **[Overall Architecture](./DOCS/OVERVIEW.md)**: Product philosophy and technical stack.
*   **[Backend & Model Logic](./DOCS/BACKEND_MODEL.md)**: State machine, system prompts, and brand guardrails.
*   **[RAG & Hybrid Search](./DOCS/RAG_ENGINE.md)**: Vector DB internals and BM25 ranking.
*   **[Frontend & Visual Sync](./DOCS/FRONTEND_UX.md)**: React architecture, Orb visualizer, and mic sync.
*   **[API Reference](./DOCS/API_REFERENCE.md)**: Endpoint definitions and schema.
*   **[Codebase Index](./DOCS/CODEBASE_INDEX.md)**: Complete file-by-file index of every module, class, function, and endpoint.

---

## 🌟 Executive Summary

This project is not a generic chatbot. It is a specialized **Consultant Agent** built with a strict "Ironclad" architecture designed to replicate the experience of a high-end photography store expert. It features:
1.  **Strict 3-Phase Logic**: It refuses to search until it understands your specific needs ("Investigator" -> "Searcher" -> "Presenter").
2.  **Semantic Firewall**: A custom Python-level interceptor that physically blocks the AI from hallucinating brand names before searching.
3.  **Synchronized Experience**: Frontend logic that "auto-mutes" the mic while thinking and synchronizes product cards with spoken explanations.

---

## 🏗️ Architecture Stack

### Backend (The "Brain")
*   **Core**: Python / Flask
*   **LLM**: **Google Gemini 3 Pro** (Cloud)
    *   *Why?* Superior reasoning capabilities compared to local models, essential for maintaining strict state adherence.
*   **RAG Engine**:
    *   **Vector Store**: `ChromaDB` (Local)
    *   **Embeddings**: `all-MiniLM-L6-v2` (Sentence Transformers)
    *   **Search**: Hybrid (Semantic Vector Cosine Similarity + Keyword BM25)
*   **Voice Generation**: **ElevenLabs API** (Turbo v2 model)
    *   *Voice ID*: `cgSgspJ2msm6clMCkdW9` (Jessica - Professional/Crisp)
    *   *Latency*: Optimized for near real-time responses.

### Frontend (The "Face")
*   **Framework**: React 18 + Vite
*   **Interaction**: Web Speech API (STT) + HTML5 Audio (TTS)
*   **State Management**: Custom `useAssistant.js` hook with Ref-based state tracking to prevent stale closures.
*   **Visuals**: `Three.js` / Canvas-based "Orb" visualizer that reacts to audio frequency (FFT) data.

---

## 🔐 The "Ironclad" Guardrails

We implemented a multi-layered defense system to ensure the AI *never* hallucinates inventory or breaks character:

### 1. The Semantic Firewall (Python Layer)
The AI is strictly explicitly forbidden from "guessing" products.
*   **Mechanism**: A Python function `detect_brand_leak(text)` scans every output in the "Investigator" phase.
*   **Watchlist**: Contains 25+ major brands (Sony, Canon, GoPro, DJI, etc.).
*   **Action**: If the AI slips and mentions "Sony" before searching, the Python backend **intercepts** the message, deletes it, and forces a generic fallback response ("I can check options for you...").

### 2. The 3-Phase State Machine
The backend tracks a strict session state (`session['stage']`) that the AI cannot override:
1.  **State 1: INVESTIGATOR** (Default)
    *   **Goal**: Gather requirements.
    *   **Constraint**: *Cannot* search. *Cannot* mention products.
    *   **User**: "I need a camera." -> **AI**: "For vlogging or cinema?"
2.  **State 2: SEARCHER**
    *   **Goal**: Search the vector database.
    *   **Action**: Triggered only when needs are clear. Hybrid RAG search executes.
3.  **State 3: PRESENTER**
    *   **Goal**: Explain results.
    *   **Constraint**: Can *only* discuss the specific JSON products returned by the search. "Database Reality" rule applies (if it's not in the JSON, it doesn't exist).

---

## ⚡ Key Features & Logic

### 🧠 Hybrid RAG Search
We don't rely on just one search method. We assume the user might use broad concepts OR specific keywords.
*   **Vector Search**: Finds "cinematic look" even if the product doesn't say "cinematic".
*   **Keyword Search**: Finds "A7S III" even if the embeddings are fuzzy.
*   **Fusion**: Results are weighted (50/50) and re-ranked for maximum relevance.

### 🗣️ Synchronized Voice/UI
The frontend `useAssistant.js` hook was heavily engineered for natural conversation:
*   **Auto-Mute**: The microphone physically stops listening (`recognition.stop()`) the millisecond the AI starts "thinking".
*   **Auto-Unmute**: The mic re-opens *only* after the AI audio has finished playing.
*   **Synced Explanation**: The backend generates an "Explanation" message *immediately* after finding products. The frontend plays this audio *exactly* as the visual product cards appear on screen.

---

## 🚀 Installation & Setup

### Prerequisites
*   **Python 3.8+**
*   **Node.js 18+**
*   **Google Gemini API Key** (Get from Google AI Studio)
*   **ElevenLabs API Key**

### 1. Backend Setup
```bash
# Clone
git clone https://github.com/someone5119819-creator/AI-Shopping-Assistant.git
cd AI-Shopping-Assistant

# Virtual Env
python3 -m venv venv
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```

### 2. Configuration (`.env`)
Create a `.env` file in the root:
```ini
FLASK_APP=assistant_api.py
FLASK_ENV=development
GEMINI_API_KEY=AIzaSy...    # Your Google Gemini Key
ELEVENLABS_API_KEY=sk_...   # Your ElevenLabs Key
ELEVENLABS_VOICE_ID=cgSgspJ2msm6clMCkdW9
```

### 3. Data Processing (Optional)
If running for the first time, index the products:
```bash
python data_processor.py
# This creates the ./chroma_db folder with vector embeddings
```

### 4. Running the System
**Terminal 1 (Backend)**:
```bash
source venv/bin/activate
python assistant_api.py
# Running on http://localhost:8001
```

**Terminal 2 (Frontend)**:
```bash
cd frontend_react
npm install
npm run dev
# Running on http://localhost:5173
```

---

## 📂 Project Structure

```text
/
├── config.py               # CONFIG: Centralized env-based configuration
├── shopify_fetcher.py      # ETL: Shopify Admin API product fetcher
├── data_processor.py       # ETL: Product JSON -> searchable documents
├── embeddings.py           # ML: Sentence-transformer embedding generator
├── vector_store.py         # DB: ChromaDB vector storage & search
├── keyword_search.py       # SEARCH: BM25 keyword search engine
├── hybrid_search.py        # SEARCH: Semantic + keyword fusion
├── search.py               # SEARCH: High-level search interface
├── api.py                  # API: FastAPI REST search API (port 8000)
├── assistant_api.py        # CORE: Flask AI assistant (port 8001)
├── setup.py                # SETUP: First-run setup wizard
├── products.json           # DATA: Cached product catalog (~9 MB)
├── requirements.txt        # DEPS: Python dependencies
├── DOCS/                   # DOCS: Technical documentation
│   ├── OVERVIEW.md
│   ├── BACKEND_MODEL.md
│   ├── RAG_ENGINE.md
│   ├── FRONTEND_UX.md
│   ├── API_REFERENCE.md
│   └── CODEBASE_INDEX.md   # NEW: Complete file-by-file codebase index
├── examples/               # EXAMPLES: Usage examples
│   ├── basic_search.py
│   └── rag_query.py
└── frontend_react/         # UI: React Application
    ├── src/
    │   ├── App.jsx             # Main layout & routing
    │   ├── hooks/
    │   │   └── useAssistant.js  # Core hook (voice, chat, cart, TTS)
    │   └── components/
    │       ├── OrbVisualizer.jsx    # Audio-reactive 3D orb
    │       ├── CartDrawer.jsx       # Cart side drawer
    │       ├── CheckoutScreen.jsx   # Checkout modal
    │       └── checkout/            # Inline checkout flow
    └── vite.config.js
```

---

## 📜 Complete Changelog / History
*   **v1.0**: Initial RAG implementation using **Ollama (Llama 3)** locally. Basic search.
*   **v1.1**: Added **Orb Visualizer** and basic TTS.
*   **v1.5**: Implemented **Hybrid Search** (Vector + Keyword) for better accuracy.
*   **v2.0**: The "Consultant Upgrade".
    *   Moved from simple Chatbot to **3-Phase State Machine** (Investigator/Searcher/Presenter).
    *   Added **ElevenLabs** for premium voice.
*   **v2.5**: **Ironclad Guardrails**.
    *   Added Python-level brand interception to stop hallucinations.
    *   Strict "Database Reality" prompt enforcement.
*   **v3.0 (Current)**: **Cloud Migration**.
    *   Migrated LLM to **Google Gemini 3 Pro**.
    *   Implemented frontend Auto-Mute/Unmute synchronization.
