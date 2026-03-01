# 🛒 AI Shopping Assistant

> Talk to an AI shopping expert that helps you find the perfect camera or audio gear — using your voice.

![Status](https://img.shields.io/badge/Status-Production_Ready-success)
![Brain](https://img.shields.io/badge/Brain-Gemini_3_Pro-blue)
![Voice](https://img.shields.io/badge/Voice-ElevenLabs_Turbo_v2-orange)
![Search](https://img.shields.io/badge/Search-Hybrid_RAG-green)

---

## 💡 What Does This Do?

This is a **voice-powered AI shopping assistant** that acts like a real store expert for camera and audio equipment. You can:

- 🎤 **Talk to it** — Ask questions using your microphone, just like talking to a salesperson
- 🔍 **Smart Search** — It searches through a product catalog to find exactly what you need
- 🗣️ **It Talks Back** — The assistant responds with a natural-sounding human voice
- 🛒 **Buy Stuff** — Add products to your cart and check out, all through conversation
- 📷 **Show It Things** — Point your camera at gear you already own, and it'll identify it

**Example conversation:**
> **You:** "I need a good camera for YouTube vlogs"
> **AI:** "Great! Are you filming mostly indoors or outdoors? And what's your budget range?"
> **You:** "Mostly indoors, under $2000"
> **AI:** "I found two great options for you..." *(shows product cards with details)*

---

## 🚀 Getting Started (Step by Step)

### What You'll Need Before Starting

| What | Where to Get It | Why |
|------|----------------|-----|
| **Python 3.8 or newer** | [python.org/downloads](https://python.org/downloads) | Runs the backend server |
| **Node.js 18 or newer** | [nodejs.org](https://nodejs.org) | Runs the frontend website |
| **Google Gemini API Key** | [aistudio.google.com](https://aistudio.google.com) | The AI brain (free tier available) |
| **ElevenLabs API Key** | [elevenlabs.io](https://elevenlabs.io) | Makes the AI voice sound human |

> [!TIP]
> **Not sure if you have Python/Node installed?** Open your Terminal (Mac) or Command Prompt (Windows) and type `python3 --version` and `node --version`. If you see version numbers, you're good!

---

### Step 1: Download the Project

Open your Terminal and run these commands one at a time:

```bash
# Download the project files from GitHub
git clone https://github.com/someone5119819-creator/AI-Shopping-Assistant.git

# Go into the project folder
cd AI-Shopping-Assistant
```

---

### Step 2: Set Up the Backend (Python)

```bash
# Create an isolated Python environment (keeps things clean)
python3 -m venv venv

# Activate the environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install all required packages (this may take a minute)
pip install -r requirements.txt
```

> [!NOTE]
> You'll know the environment is active when you see `(venv)` at the start of your terminal line.

---

### Step 3: Add Your API Keys

1. Find the file called `.env.example` in the project folder
2. Make a copy and rename it to `.env`
3. Open `.env` in any text editor and fill in your keys:

```ini
# Replace the placeholder values with your actual keys:
GEMINI_API_KEY=paste_your_gemini_key_here
ELEVENLABS_API_KEY=paste_your_elevenlabs_key_here
ELEVENLABS_VOICE_ID=cgSgspJ2msm6clMCkdW9
```

> [!IMPORTANT]
> **Never share your `.env` file or commit it to GitHub.** It contains your private API keys.

---

### Step 4: Set Up the Frontend (React)

Open a **new** terminal window:

```bash
# Go into the frontend folder
cd frontend_react

# Install frontend packages (this may take a minute)
npm install
```

---

### Step 5: Run the App! 🎉

The easiest way to start everything (all 4 servers) is using the custom command:

```bash
# Start all servers (Search API, Assistant API, Hybrid UI, and React UI)
fuck u fukka
```

**Now open your browser and go to: [http://localhost:5173](http://localhost:5173)** 🚀

<details>
<summary><strong>Alternative: Manual Method (Multi-Terminal)</strong></summary>

If you prefer to see logs in real-time or run things manually, you need **two terminal windows**:

**Terminal 1 — Start the AI Backend:**
```bash
# Make sure you're in the main project folder
source venv/bin/activate
python assistant_api.py
```
You should see: `Running on http://localhost:8001`

**Terminal 2 — Start the Website:**
```bash
cd frontend_react
npm run dev
```
You should see: `Local: http://localhost:5173`
</details>

---

## 🛑 Stop the App

To stop all servers instantly, use the custom shutdown command:

```bash
i fucked u fukka
```

> [!TIP]
> This command kills all processes on ports 8000, 8001, 8080, and 5173, ensuring a clean exit.

---

## 🎯 How It Works (Simple Version)

The assistant follows a strict 3-step process, just like a real store consultant:

| Step | What It Does | Example |
|------|-------------|---------|
| **1. Ask Questions** | Understands what you actually need | *"What will you use it for? What's your budget?"* |
| **2. Search** | Searches the product database | *Finds matching products from inventory* |
| **3. Recommend** | Shows you only real products it found | *"Here are two options that match..."* |

**Why this matters:** Unlike regular chatbots, this assistant **never makes up products**. It can only recommend items that actually exist in the store's inventory.

---

## ❓ Troubleshooting / FAQ

<details>
<summary><strong>🔴 "ModuleNotFoundError" or "command not found: pip"</strong></summary>

Make sure you've activated the virtual environment first:
```bash
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows
```
Then try `pip install -r requirements.txt` again.
</details>

<details>
<summary><strong>🔴 The mic isn't working</strong></summary>

- Make sure your browser has microphone permission (check the lock icon in the URL bar)
- Use **Chrome** or **Edge** — Safari has limited voice support
- Check that your system microphone is working in System Settings
</details>

<details>
<summary><strong>🔴 "GEMINI_API_KEY is required" error</strong></summary>

Make sure you:
1. Renamed `.env.example` to `.env`
2. Pasted your actual API key (not the placeholder text)
3. Restarted the backend server after editing `.env`
</details>

<details>
<summary><strong>🔴 Frontend shows "connection refused"</strong></summary>

The backend server must be running first. Check Terminal 1 and make sure you see "Running on http://localhost:8001".
</details>

---

## 🏗️ Technical Deep Dive

<details>
<summary><strong>Click to expand — Architecture & Tech Stack</strong></summary>

### Backend (The "Brain")
- **Core**: Python / Flask
- **LLM**: Google Gemini 3 Pro (Cloud) — chosen for superior reasoning and strict state adherence
- **RAG Engine**:
  - **Vector Store**: ChromaDB (Local)
  - **Embeddings**: `all-MiniLM-L6-v2` (Sentence Transformers)
  - **Search**: Hybrid (Semantic Vector Cosine Similarity + Keyword BM25)
- **Voice**: ElevenLabs API (Turbo v2 model)

### Frontend (The "Face")
- **Framework**: React 18 + Vite
- **Voice Input**: Web Speech API (STT)
- **Voice Output**: HTML5 Audio (TTS via ElevenLabs)
- **Visuals**: Canvas-based "Orb" visualizer that reacts to audio

### Guardrails
1. **Brand Firewall** — Python-level interception prevents the AI from mentioning brands before searching (25+ brand watchlist)
2. **3-Phase State Machine** — Backend enforces Investigator → Searcher → Presenter flow
3. **Database Reality** — AI can only discuss products that exist in search results

</details>

<details>
<summary><strong>Click to expand — Project Structure</strong></summary>

```text
/
├── config.py               # Centralized configuration
├── shopify_fetcher.py      # Shopify API product fetcher
├── data_processor.py       # Product data → searchable documents
├── embeddings.py           # Text → vector embedding generator
├── vector_store.py         # ChromaDB vector storage & search
├── keyword_search.py       # BM25 keyword search engine
├── hybrid_search.py        # Semantic + keyword search fusion
├── search.py               # High-level search interface
├── api.py                  # FastAPI search API (port 8000)
├── assistant_api.py        # Flask AI assistant (port 8001)
├── run_all.sh              # CUSTOM: Startup script (fuck u fukka)
├── kill_all.sh             # CUSTOM: Shutdown script (i fucked u fukka)
├── setup.py                # First-run setup wizard
├── products.json           # Product catalog data (~9 MB)
├── requirements.txt        # Python dependencies
├── DOCS/                   # Technical documentation
│   ├── OVERVIEW.md
│   ├── BACKEND_MODEL.md
│   ├── RAG_ENGINE.md
│   ├── FRONTEND_UX.md
│   ├── API_REFERENCE.md
│   └── CODEBASE_INDEX.md   # Complete codebase index
├── examples/               # Usage examples
│   ├── basic_search.py
│   └── rag_query.py
└── frontend_react/         # React frontend
    ├── src/
    │   ├── App.jsx
    │   ├── hooks/
    │   │   └── useAssistant.js
    │   └── components/
    │       ├── OrbVisualizer.jsx
    │       ├── CartDrawer.jsx
    │       ├── CheckoutScreen.jsx
    │       └── checkout/
    └── vite.config.js
```

</details>

---

## 📚 Documentation Hub

For developers who want to understand the internals:

| Guide | What's Inside |
|-------|--------------|
| [Overall Architecture](./DOCS/OVERVIEW.md) | Product philosophy and technical stack |
| [Backend & Model Logic](./DOCS/BACKEND_MODEL.md) | State machine, system prompts, guardrails |
| [RAG & Hybrid Search](./DOCS/RAG_ENGINE.md) | Vector DB internals and BM25 ranking |
| [Frontend & Visual Sync](./DOCS/FRONTEND_UX.md) | React architecture, Orb visualizer, mic sync |
| [API Reference](./DOCS/API_REFERENCE.md) | Endpoint definitions and schema |
| [Codebase Index](./DOCS/CODEBASE_INDEX.md) | Every module, class, function, and endpoint |

---

## 📜 Version History

| Version | What Changed |
|---------|-------------|
| **v5.0** (Beta) | **Vision & AR Integration**. Implemented Image Based Search with Camera UI, Live AR Object Detection & Realtime Optimization, and experimental Gemini Live API. |
| **v4.5** | **New Assistant UI**. Enhanced assistant styling with refined orb animations, scaling support, and Active UI redesign. |
| **v4.0** (Current) | **E-Commerce Integration**. Added robust Cart functionality, Conversational Checkout Flow with inline UI, and complete Shopify checkout integration. |
| **v3.5** | **Custom Automation**. Added `fuck u fukka` and `i fucked u fukka` commands for easy service management. |
| **v3.2** | **UI Overhaul**. Refined Orb Visualizer to Canvas, updated UI layout with Dynamic Content area, and improved Transcript sync. |
| **v3.0** | **Cloud Migration**. Migrated to **Google Gemini 3 Pro**, added auto-mute/unmute sync |
| **v2.5** | Added "Ironclad" guardrails — brand interception + database reality |
| **v2.0** | 3-phase state machine + ElevenLabs premium voice |
| **v1.5** | Hybrid search (vector + keyword) for better accuracy |
| **v1.1** | Added Orb Visualizer and basic TTS |
| **v1.0** | Initial RAG with Ollama (Llama 3) |
