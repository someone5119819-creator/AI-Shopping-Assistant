import { useState, useEffect, useRef } from 'react';

const API_BASE = 'http://localhost:8001/api/assistant';
const WS_BASE = 'ws://localhost:8002';  // NEW: WebSocket for Live API

export const useAssistant = () => {
    const [sessionId, setSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [products, setProducts] = useState([]);

    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [isThinking, setIsThinking] = useState(false);
    const [status, setStatus] = useState('Initializing...');

    // Live Transcript State
    const [liveUserText, setLiveUserText] = useState('');
    const [liveAiText, setLiveAiText] = useState('');

    const [isCameraOpen, setIsCameraOpen] = useState(false);

    // Refs
    const audioContextRef = useRef(null);
    const analyserRef = useRef(null);
    const shouldListenRef = useRef(true);
    const isThinkingRef = useRef(false);
    const isSpeakingRef = useRef(false);

    // NEW: Gemini Live API WebSocket
    const liveWSRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const microphoneRef = useRef(null);
    const audioQueueRef = useRef([]);

    // Initialize Session
    useEffect(() => {
        fetch(`${API_BASE}/session/new`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                setSessionId(data.session_id);
                setStatus('Ready');
                addMessage('assistant', "Hi! I'm your AI shopping assistant.");
            })
            .catch(err => {
                console.error(err);
                setStatus('Connection Failed');
            });

        // Audio Context Setup
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        const ctx = new AudioContext();
        audioContextRef.current = ctx;
        const analyser = ctx.createAnalyser();
        analyser.fftSize = 256;
        analyserRef.current = analyser;

        // Cleanup
        return () => {
            shouldListenRef.current = false;
            if (liveWSRef.current) liveWSRef.current.close();
        };
    }, []);

    // NEW: Connect to Gemini Live API via WebSocket
    const connectLiveAPI = async () => {
        if (!sessionId) return;

        const ws = new WebSocket(`${WS_BASE}/${sessionId}`);
        liveWSRef.current = ws;

        ws.onopen = () => {
            console.log('[Live API] Connected');
            setStatus('Live API Connected');
            startAudioStreaming();
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'audio') {
                // Play audio from Gemini (PCM16)
                playGeminiAudio(data.data);
            } else if (data.type === 'transcript') {
                // Update live transcript
                if (data.role === 'user') {
                    setLiveUserText(data.text);
                    addMessage('user', data.text);
                    setLiveUserText('');  // Clear after adding
                } else if (data.role === 'assistant') {
                    setLiveAiText(data.text);
                    addMessage('assistant', data.text);
                }
            } else if (data.type === 'products') {
                // Update products
                setProducts(data.data);
            }
        };

        ws.onerror = (error) => {
            console.error('[Live API] Error:', error);
            setStatus('Live API Error');
        };

        ws.onclose = () => {
            console.log('[Live API] Disconnected');
            setStatus('Disconnected');
            stopAudioStreaming();
        };
    };

    // NEW: Start capturing audio using Web Audio API for PCM16
    const startAudioStreaming = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 16000  // Gemini expects 16kHz
                }
            });

            console.log('[Audio] Got microphone access');

            const audioCtx = audioContextRef.current;
            const source = audioCtx.createMediaStreamSource(stream);

            // Create ScriptProcessor for raw PCM capture
            const bufferSize = 4096;
            const processor = audioCtx.createScriptProcessor(bufferSize, 1, 1);

            processor.onaudioprocess = (e) => {
                if (liveWSRef.current?.readyState !== WebSocket.OPEN) {
                    return;
                }

                // Get raw PCM float32 samples
                const inputData = e.inputBuffer.getChannelData(0);

                // Convert float32 (-1 to 1) to int16 PCM
                const pcm16 = new Int16Array(inputData.length);
                for (let i = 0; i < inputData.length; i++) {
                    const s = Math.max(-1, Math.min(1, inputData[i]));
                    pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                }

                // Convert to base64
                const base64 = btoa(
                    String.fromCharCode.apply(null, new Uint8Array(pcm16.buffer))
                );

                console.log(`[Audio] Sending PCM16: ${pcm16.length} samples, ${base64.length} chars`);

                // Send to WebSocket
                liveWSRef.current.send(JSON.stringify({
                    type: 'audio',
                    data: base64
                }));
            };

            // Connect audio graph
            source.connect(processor);
            processor.connect(audioCtx.destination);

            // Store processor for cleanup
            mediaRecorderRef.current = processor;
            microphoneRef.current = source;

            console.log('[Audio] Started PCM16 capture');
            setIsListening(true);
            setStatus('Listening...');

        } catch (err) {
            console.error('[Audio] Mic Error:', err);
            setStatus('Mic Access Denied');
        }
    };

    // NEW: Stop audio streaming
    const stopAudioStreaming = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.disconnect();
            mediaRecorderRef.current = null;
        }
        if (microphoneRef.current) {
            microphoneRef.current.disconnect();
            microphoneRef.current = null;
        }
        setIsListening(false);
    };

    // NEW: Play audio from Gemini (PCM16 base64)
    const playGeminiAudio = (base64Audio) => {
        setIsSpeaking(true);
        isSpeakingRef.current = true;
        setStatus('Speaking...');

        // Decode base64 to PCM16
        const binaryString = atob(base64Audio);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        // Convert PCM16 to AudioBuffer (24kHz from Gemini)
        const audioCtx = audioContextRef.current;
        const sampleRate = 24000;
        const audioBuffer = audioCtx.createBuffer(1, bytes.length / 2, sampleRate);
        const channelData = audioBuffer.getChannelData(0);

        // Convert Int16 to Float32
        const dataView = new DataView(bytes.buffer);
        for (let i = 0; i < channelData.length; i++) {
            channelData[i] = dataView.getInt16(i * 2, true) / 32768.0;
        }

        // Play
        const source = audioCtx.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(analyserRef.current);
        source.connect(audioCtx.destination);

        source.onended = () => {
            setIsSpeaking(false);
            isSpeakingRef.current = false;
            setStatus('Listening...');
        };

        source.start(0);
    };

    // Toggle Microphone (Live API)
    const toggleMic = () => {
        if (isListening) {
            stopAudioStreaming();
            if (liveWSRef.current) liveWSRef.current.close();
        } else {
            connectLiveAPI();
        }
    };

    // Legacy text-based sendMessage (fallback / backward compatibility)
    const sendMessage = async (text, isHidden = false) => {
        if (!isHidden) addMessage('user', text);
        setIsThinking(true);
        isThinkingRef.current = true;
        setStatus('Thinking...');
        setLiveUserText('');

        try {
            const res = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, session_id: sessionId })
            });
            const data = await res.json();

            setIsThinking(false);
            isThinkingRef.current = false;
            handleResponse(data);
        } catch (err) {
            setIsThinking(false);
            isThinkingRef.current = false;
            setStatus('Error');
        }
    };

    // Analyze Image Logic (unchanged)
    const analyzeImage = async (imageBlob) => {
        setIsThinking(true);
        isThinkingRef.current = true;
        setStatus('Analyzing...');

        const formData = new FormData();
        formData.append('file', imageBlob, 'capture.jpg');
        formData.append('session_id', sessionId);

        try {
            const res = await fetch(`${API_BASE}/vision`, {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            setIsThinking(false);
            isThinkingRef.current = false;
            setIsCameraOpen(false);
            handleResponse(data);
        } catch (err) {
            console.error("Vision Error", err);
            setIsThinking(false);
            isThinkingRef.current = false;
            setStatus('Error');
        }
    };

    // Silent Scan logic (unchanged)
    const scanImage = async (imageBlob) => {
        const formData = new FormData();
        formData.append('file', imageBlob, 'scan.jpg');

        try {
            const res = await fetch(`${API_BASE}/scan`, {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            return data;
        } catch (err) {
            console.error("Scan Error", err);
            return { objects: [] };
        }
    };

    const handleResponse = (data) => {
        if (data.action === 'open_camera') {
            setIsCameraOpen(true);
            setStatus('Camera Ready');
        }

        if (data.products && data.products.length > 0) {
            setProducts(data.products);
            setStatus('Products Found');
            addMessage('assistant', data.message);
        } else {
            setProducts([]);
            setStatus('Speaking...');
            addMessage('assistant', data.message);
        }
    };

    const addMessage = (role, text) => {
        setMessages(prev => [...prev, { role, text }]);
    };

    const startListening = toggleMic;  // Alias for backward compatibility
    const stopListening = toggleMic;

    const handleSubmit = (e) => {
        e.preventDefault();
        // Legacy handler...
    };

    return {
        sessionId,
        messages,
        products,
        isListening,
        isSpeaking,
        isThinking,
        status,
        liveUserText,
        liveAiText,
        isCameraOpen,
        setIsCameraOpen,
        analyzeImage,
        scanImage,
        analyser: analyserRef.current,
        startListening,
        stopListening,
        sendMessage,
        toggleMic  // Exported for UI
    };
};
