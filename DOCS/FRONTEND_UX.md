# Frontend UX & Synchronization: The Responsive Face

## ⚛️ The `useAssistant` Architecture
The `useAssistant.js` hook is a complex state orchestrator that translates AI intents into hardware actions (mic/speakers) and visual updates.

### 🔄 The Synchronization Lifecycle
To create a "fluid" conversation, the frontend uses a strict Ref-based state machine to prevent stale closure bugs:

1.  **Thinking Phase**:
    *   Mic is explicitly stopped: `recognition.stop()`.
    *   Status set to "Thinking...".
    *   `isThinkingRef` set to `true`.
2.  **Speaking Phase**:
    *   AI response (Audio Blob) received.
    *   Audio visualizer (Orb) begins FFT analysis.
    *   `isSpeakingRef` set to `true`.
3.  **Listening Phase**:
    *   `audio.onended` triggers.
    *   `isSpeakingRef` set to `false`.
    *   Mic is explicitly restarted: `recognition.start()`.

---

## 🎨 Visual Components

### 1. The Reactive Orb (`OrbVisualizer.jsx`)
*   **Technology**: Canvas API + AudioContext.
*   **Logic**:
    *   Connects to the global `audioContextRef`.
    *   Uses an `AnalyserNode` to pull real-time frequency data.
    *   **States**:
        *   *Idle*: Slow, breathing pulse.
        *   *Thinking*: Rapid, rotating spin.
        *   *Speaking**: Violent, reactive expansion matched to volume peaks.

### 2. Live Transcription
*   **User Side**: Real-time "ink" as the user speaks using `interimResults`.
*   **AI Side**: Shows the text being spoken by the TTS engine.

### 3. Smart Card Rendering
*   When Gemini returns `products`, the `ProductCard` component iterates over the list.
*   These are rendered **before** the audio explanation finishes, allowing the user to browse while the AI explains.
