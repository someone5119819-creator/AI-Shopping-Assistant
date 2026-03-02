# Project Overview: The Smart Shopping Assistant

## 🎯 Project Philosophy
The **Smart Shopping Assistant** is designed to bridge the gap between static e-commerce search and the expertise of a human consultant. Unlike traditional chatbots that simply answer questions, this system is **consultative by design**, prioritized on understanding the user's *context* before offering solutions.

### Core Principles
1.  **Needs-First Interaction**: Never suggest a product without understanding the "Why".
2.  **Ironclad Grounding**: Zero tolerance for hallucinations. If it's not in the database, it doesn't exist.
3.  **Voice-Synchronized UX**: Speech and visuals must operate as a single, cohesive entity.
4.  **Persistent Personalization**: Learn and remember user preferences (Brand, Skill, Style) across sessions.
5.  **Global Accessibility**: Automatic multi-language support (English, Spanish, French, etc.) and PWA mobile readiness.

---

## 🏗️ Technical Stack

### Brain (LLM)
*   **Provider**: Google Gemini Flash (Cloud)
*   **Role**: Orchestration, state management, natural language explanation, and cross-session learning.
*   **Migration History**: Migrated from Ollama → Gemini 3 Pro → Gemini Flash for optimal speed-to-performance ratio and lower latency in voice interactions.

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
2.  **Backend Analysis**: Gemini analyzes intent and **learns from preferences**.
    *   *Phase 1*: Asks clarifying questions (Semantic Firewall active).
    *   *Phase 2*: Triggers JSON-based Search Action (Standard or Aesthetic/Style matched).
3.  **RAG Fetch**: Hybrid search finds 1-2 optimal products from products.json.
4.  **Memory Save**: User preferences (Brand Affinity, Skill Level, Style) are persisted to `shopping_profiles.json`.
5.  **Sync-Response**:
    *   Backend generates explanation (Comparison or Standard) for results.
    *   Frontend receives Product Data + Audio Explanation.
    *   Frontend mutes mic, shows cards, and speaks explanation simultaneously.
