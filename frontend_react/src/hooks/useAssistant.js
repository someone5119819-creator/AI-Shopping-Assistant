import { useState, useEffect, useRef } from 'react';

const API_BASE = 'http://localhost:8001/api/assistant';

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

    const audioContextRef = useRef(null);
    const analyserRef = useRef(null);
    const recognitionRef = useRef(null);
    const microphoneRef = useRef(null);
    const shouldListenRef = useRef(true); // Always listen by default

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

        initRecognition();

        // Cleanup
        return () => {
            shouldListenRef.current = false;
            if (recognitionRef.current) recognitionRef.current.stop();
        };
    }, []);

    // Mic Logic
    const startListening = async () => {
        try {
            const ctx = audioContextRef.current;
            if (ctx.state === 'suspended') await ctx.resume();

            if (!microphoneRef.current) {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const source = ctx.createMediaStreamSource(stream);
                source.connect(analyserRef.current);
                microphoneRef.current = source;
            }

            shouldListenRef.current = true;
            if (recognitionRef.current && !isListening) {
                recognitionRef.current.start();
            }

        } catch (err) {
            console.error('Mic Error:', err);
            setStatus('Mic Access Denied');
        }
    };

    const stopListening = () => {
        shouldListenRef.current = false;
        if (recognitionRef.current) recognitionRef.current.stop();
        setIsListening(false);
        setStatus('Paused');
    };

    const initRecognition = () => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Browser not supported");
            return;
        }
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.continuous = true; // Always On
        recognition.interimResults = true; // For live transcription

        recognition.onstart = () => {
            setIsListening(true);
            setStatus('Listening...');
        };

        recognition.onend = () => {
            // Auto-restart if we should be listening
            if (shouldListenRef.current && !isThinking && !isSpeaking) {
                try {
                    recognition.start();
                } catch (e) {
                    // Ignore if already started
                }
            } else {
                setIsListening(false);
            }
        };

        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            if (interimTranscript) {
                setLiveUserText(interimTranscript);
            }

            if (finalTranscript) {
                setLiveUserText(finalTranscript);
                // Process final command
                sendMessage(finalTranscript);
            }
        };

        recognitionRef.current = recognition;
    };

    // Chat Logic
    const sendMessage = async (text) => {
        addMessage('user', text);
        setIsThinking(true);
        setStatus('Thinking...');
        setLiveUserText(''); // Clear live text

        try {
            const res = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, session_id: sessionId })
            });
            const data = await res.json();

            setIsThinking(false);
            handleResponse(data);
        } catch (err) {
            setIsThinking(false);
            setStatus('Error');
        }
    };

    const handleResponse = (data) => {
        if (data.products && data.products.length > 0) {
            setProducts(data.products);
            setStatus('Products Found');
            const text = "I found these products for you.";
            setLiveAiText(text);
            speak(text);
            addMessage('assistant', `Found ${data.products.length} products.`);
        } else {
            setProducts([]);
            setStatus('Speaking...');
            setLiveAiText(data.message);
            speak(data.message);
            addMessage('assistant', data.message);
        }
    };

    const addMessage = (role, text) => {
        setMessages(prev => [...prev, { role, text }]);
    };

    // TTS
    const speak = (text) => {
        if (!text) return;

        // Pause listening while speaking to avoid echo
        if (recognitionRef.current) recognitionRef.current.stop();

        fetch(`${API_BASE}/tts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        })
            .then(res => res.blob())
            .then(blob => {
                const url = URL.createObjectURL(blob);
                const audio = new Audio(url);
                audio.crossOrigin = "anonymous";

                audio.onplay = () => {
                    setIsSpeaking(true);
                    setStatus('Speaking...');

                    // Connect to analyser
                    const ctx = audioContextRef.current;
                    const source = ctx.createMediaElementSource(audio);
                    source.connect(analyserRef.current);
                    source.connect(ctx.destination);
                };

                audio.onended = () => {
                    setIsSpeaking(false);
                    setLiveAiText(''); // Clear AI text
                    setStatus('Listening...');
                    // Resume listening
                    if (shouldListenRef.current && recognitionRef.current) {
                        try { recognitionRef.current.start(); } catch (e) { }
                    }
                };

                audio.play();
            })
            .catch(err => console.error("TTS Error", err));
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
        analyser: analyserRef.current,
        startListening,
        stopListening,
        sendMessage
    };
};
