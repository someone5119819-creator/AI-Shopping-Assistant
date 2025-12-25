# Project Overview: The Smart Shopping Assistant

## 🎯 Project Philosophy
The **Smart Shopping Assistant** is designed to bridge the gap between static e-commerce search and the expertise of a human consultant. Unlike traditional chatbots that simply answer questions, this system is **consultative by design**, prioritized on understanding the user's *context* before offering solutions.

### Core Principles
1.  **Needs-First Interaction**: Never suggest a product without understanding the "Why".
2.  **Ironclad Grounding**: Zero tolerance for hallucinations. If it's not in the database, it doesn't exist.
3.  **Voice-Synchronized UX**: Speech and visuals must operate as a single, cohesive entity.

---

## 🏗️ Technical Stack

### Brain (LLM)
*   **Provider**: Google Gemini 3 Pro
*   **Role**: Orchestration, state management, and natural language explanation.
*   **Migration History**: Started on local Ollama (Llama 3/Mistral) for privacy, migrated to Gemini for superior reasoning and complex instruction following.

### Knowledge (RAG)
*   **Engine**: Hybrid RAG (Retrieval-Augmented Generation).
*   **Vector DB**: ChromaDB.
*   **Search**: 50/50 Fusion of Semantic (Vector) and Keyword (BM25) search.
*   **Data**: Shopify Product Catalog (indexed locally).

### Voice (TTS)
*   **Provider**: ElevenLabs (Turbo v2).
*   **Voice**: Jessica (Crisp, Professional).
*   **Sync**: Backend-triggered auto-explanation logic.

### Interface (Web)
*   **Framework**: React 18 + Vite.
*   **STT**: Web Speech API (Always-on mic).
*   **Visuals**: Custom Reactive Orb (FFT analysis).

---

## 🛣️ Data Flow Summary

1.  **User Speech**: Captured via browser mic -> Transcribed to text in real-time.
2.  **Backend Analysis**: Gemini analyzes intent.
    *   *Phase 1*: Asks clarifying questions (Semantic Firewall active).
    *   *Phase 2*: Triggers JSON-based Search Action.
3.  **RAG Fetch**: Hybrid search finds 1-2 optimal products from products.json.
4.  **Sync-Response**:
    *   Backend generates explanation for results.
    *   Frontend receives Product Data + Audio Explanation.
    *   Frontend mutes mic, shows cards, and speaks explanation simultaneously.
