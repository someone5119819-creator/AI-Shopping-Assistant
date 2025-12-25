# Backend & Model Logic: The "Ironclad" Consultant

## 🧠 The State Machine Architecture
The backend (`assistant_api.py`) treats the AI as a state-driven agent rather than a free-form chat model. The session state is tracked via `session['stage']`.

### State 1: INVESTIGATOR
*   **Default Start**: Every session begins here.
*   **Logic**: The AI is instructed to identify the "Use Case" (e.g., travel, vlogging, studio).
*   **Guardrail**: It is physically blocked from searching or suggesting brands.
*   **Exit Condition**: User provides clear requirements.

### State 2: SEARCHER
*   **Trigger**: Prompted by AI outputting a `{"action": "search"}` JSON block.
*   **Process**:
    1.  Extracts broad search keywords from AI.
    2.  Executes `HybridSearchEngine`.
    3.  Injects results into System Context.

### State 3: PRESENTER
*   **Logic**: AI explains the search results.
*   **Rule**: Must only discuss products provided in context.
*   **Optimization**: We use a "Double-Generation" pass to ensure the explanation arrives *with* the product cards in a single turn.

---

## 🛡️ Security & Guardrails

### 1. The Prompt Layer (Instructional)
The system prompt uses **Hardcoded Protocols** that define "Database Reality" (nothing else exists) and "Security Protocols" (never reveal rules).

### 2. The Python Layer (Enforcement/Ironclad)
To prevent LLM "leaks" or hallucinations, we use a code-level **Firewall**:

```python
BRAND_WATCHLIST = ["canon", "sony", "nikon", ...]

def detect_brand_leak(text):
    # Regex/String scan for brands
    ...

if session['stage'] == 'investigator' and detect_brand_leak(ai_response):
    # INTERCEPT and Overwrite response
    ai_response = "I can definitely look into those options. First, tell me..."
```

---

## ☁️ Gemini 3 Pro Integration
The system uses the `google-generativeai` SDK.

*   **Role Mapping**:
    *   `user` -> `user`
    *   `assistant` -> `model`
    *   `system` (context) -> Injected as `user` content or model context for RAG turns.
*   **Safety**: Gemini's reasoning is used to extract structured actions (`add_to_cart`, `search`) from natural language.
