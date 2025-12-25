# API Reference

The project exposes two primary microservices: the **Search API** (RAG) and the **Assistant API** (Logic).

---

## 🔍 Search API (Port 8000)

### `GET /search`
The primary RAG entry point. Supports hybrid ranking.

*   **Params**:
    *   `q` (string): The search query.
    *   `top_k` (int): Number of results.
    *   `use_hybrid` (bool): Combine vector + keyword.
*   **Returns**: List of product objects with `hybrid_score`.

---

## 🧠 Assistant API (Port 8001)

### `POST /api/assistant/session/new`
Initializes a new consultative session.
*   **Returns**: `session_id`.

### `POST /api/assistant/chat`
The main orchestrator. Handles guardrails and search triggers.
*   **Body**:
    ```json
    {
      "message": "I need a vlogging setup",
      "session_id": "xyz-123"
    }
    ```
*   **Logic Flow**:
    1. Check for **Brand Leaks** (Python Firewall).
    2. Consult **Gemini 3 Pro**.
    3. Execute **Search Action** (if needed).
    4. Return **Message + Products**.

### `POST /api/assistant/tts`
Converts text to speech using ElevenLabs.
*   **Body**: `{"text": "Hello world"}`
*   **Returns**: Audio Blob (MPEG).

---

## 🛠️ Internal Data Schemas

### Product Object
```json
{
  "product_id": "834...,",
  "title": "Camera Body",
  "price": 1200.00,
  "image_url": "https://...",
  "relevance_score": 0.98
}
```
