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

    const [isCameraOpen, setIsCameraOpen] = useState(false);
    const [isCartOpen, setIsCartOpen] = useState(false);
    const [selectedProducts, setSelectedProducts] = useState([]);

    // Checkout state
    const [checkoutStage, setCheckoutStage] = useState(null);
    // null | 'review' | 'address' | 'payment' | 'success'

    // Simple cart state
    const [cartItems, setCartItems] = useState([]);
    const [cartCount, setCartCount] = useState(0);

    // ... existing refs ...
    const audioContextRef = useRef(null);
    const analyserRef = useRef(null);
    const recognitionRef = useRef(null);
    const microphoneRef = useRef(null);
    const shouldListenRef = useRef(true); // Always listen by default
    const isThinkingRef = useRef(false);
    const isSpeakingRef = useRef(false);
    const scrollRef = useRef(null); // Ref for product container

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
            // Auto-restart if we should be listening and NOT thinking/speaking
            if (shouldListenRef.current && !isThinkingRef.current && !isSpeakingRef.current) {
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
        isThinkingRef.current = true; // Sync Ref
        setStatus('Thinking...');
        setLiveUserText(''); // Clear live text

        // STOP MIC explicitly
        if (recognitionRef.current) recognitionRef.current.stop();

        try {
            const res = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, session_id: sessionId })
            });
            const data = await res.json();

            setIsThinking(false);
            isThinkingRef.current = false; // Sync Ref
            handleResponse(data);
        } catch (err) {
            setIsThinking(false);
            isThinkingRef.current = false; // Sync Ref
            setStatus('Error');
            // Restart mic on error
            if (shouldListenRef.current && recognitionRef.current) recognitionRef.current.start();
        }
    };

    // Analyze Image Logic
    const analyzeImage = async (imageBlob) => {
        setIsThinking(true);
        isThinkingRef.current = true;
        setStatus('Analyzing...');

        // Stop Mic during analysis
        if (recognitionRef.current) recognitionRef.current.stop();

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
            setIsCameraOpen(false); // Close camera on success
            handleResponse(data);
        } catch (err) {
            console.error("Vision Error", err);
            setIsThinking(false);
            isThinkingRef.current = false;
            setStatus('Error');
            // Restart Mic
            if (shouldListenRef.current && recognitionRef.current) recognitionRef.current.start();
        }
    };

    const handleResponse = (data) => {
        // Handle Camera Action
        if (data.action === 'open_camera') {
            setIsCameraOpen(true);
            setStatus('Camera Ready');
        }

        if (data.action === 'start_checkout' || data.action === 'checkout') {
            if (cartItems.length > 0) {
                setCheckoutStage('review');
                setStatus('Checkout');
            }
        }

        // Navigation: Open Cart
        if (data.action === 'open_cart') {
            setIsCartOpen(true);
            setStatus('Cart Opened');
        }

        // Navigation: Scroll Down
        if (data.action === 'scroll_down') {
            if (scrollRef.current) {
                scrollRef.current.scrollBy({ top: 300, behavior: 'smooth' });
            }
        }

        if (data.products && data.products.length > 0) {
            setProducts(data.products);
            setStatus('Products Found');
            speak(data.message);
            addMessage('assistant', data.message);
        } else {
            setProducts([]);
            setStatus('Speaking...');
            speak(data.message);
            addMessage('assistant', data.message);
        }
    };

    const addMessage = (role, text) => {
        setMessages(prev => [...prev, { role, text }]);
    };

    // TTS
    const typeWriterRef = useRef(null);

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

                // Clear any previous typewriter
                if (typeWriterRef.current) clearInterval(typeWriterRef.current);
                setLiveAiText(''); // Start empty

                audio.onplay = () => {
                    setIsSpeaking(true);
                    isSpeakingRef.current = true;
                    setStatus('Speaking...');

                    // Connect to analyser
                    const ctx = audioContextRef.current;
                    const source = ctx.createMediaElementSource(audio);
                    source.connect(analyserRef.current);
                    source.connect(ctx.destination);

                    // Typewriter Effect - use substring to avoid character corruption
                    let i = 0;
                    const speed = 50; // ms per char

                    typeWriterRef.current = setInterval(() => {
                        if (i < text.length) {
                            i++;
                            setLiveAiText(text.substring(0, i)); // Use substring instead of concatenation
                        } else {
                            clearInterval(typeWriterRef.current);
                        }
                    }, speed);
                };

                audio.onended = () => {
                    if (typeWriterRef.current) clearInterval(typeWriterRef.current);
                    setIsSpeaking(false);
                    isSpeakingRef.current = false; // Sync Ref
                    // Do NOT clear liveAiText here (let user read it). 
                    // Or clear it after delay? 
                    // User request implies syncing output *appearance*. 
                    // Usually we keep it until next turn.

                    // setLiveAiText(''); // COMMENTED OUT: Let it persist until next turn or new speak

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

    const selectProduct = async (productId, action = 'add') => {
        try {
            const res = await fetch(`${API_BASE}/select_product`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    product_id: productId,
                    action
                })
            });

            const data = await res.json();

            if (data.status === 'success') {
                setSelectedProducts(data.selected_products);
                console.log(`[SELECTION] ${action === 'add' ? 'Added' : 'Removed'} product:`, productId);
            }
        } catch (err) {
            console.error('Error selecting product:', err);
        }
    };

    // ===== SIMPLE CART FUNCTIONS =====
    const addToCart = async (product) => {
        if (!sessionId) return;
        try {
            const res = await fetch(`${API_BASE}/cart/add`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    id: product.id,
                    title: product.title,
                    image: product.image
                })
            });
            const data = await res.json();
            if (data.success) {
                setCartCount(data.cart_count);
            }
        } catch (err) {
            console.error('Cart add error:', err);
        }
    };

    const viewCart = async () => {
        if (!sessionId) return;
        try {
            const res = await fetch(`${API_BASE}/cart?session_id=${sessionId}`);
            const data = await res.json();
            setCartItems(data.items || []);
            setCartCount(data.count || 0);
        } catch (err) {
            console.error('Cart view error:', err);
        }
    };

    const clearCart = async () => {
        if (!sessionId) return;
        try {
            const res = await fetch(`${API_BASE}/cart/clear`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });
            const data = await res.json();
            if (data.success) {
                setCartItems([]);
                setCartCount(0);
            }
        } catch (err) {
            console.error('Cart clear error:', err);
        }
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
        isCartOpen,
        setIsCartOpen,
        analyzeImage,
        selectedProducts,
        selectProduct,
        cartItems,
        cartCount,
        addToCart,
        viewCart,
        clearCart,
        checkoutStage,
        setCheckoutStage,
        scrollRef,
        analyser: analyserRef.current,
        startListening,
        stopListening,
        sendMessage
    };
};
