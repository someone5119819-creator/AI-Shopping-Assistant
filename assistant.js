// AI Shopping Assistant - OpenAI Style Voice Interface
// Handles generic "Orb" visualization and voice interactions

const API_BASE = 'http://localhost:8001/api/assistant';
let sessionId = null;
let recognition = null;
let isListening = false;
let isSpeaking = false;
let isThinking = false;

// Audio Context & Visualizer
let audioContext = null;
let analyser = null;
let microphone = null;
let visualizerCanvas = null;
let visualizerCtx = null;
let animationId = null;

// The Orb
const orb = {
    radius: 50,
    color1: '142, 142, 147', // Gray default
    color2: '28, 28, 30',
    phase: 0,
    amplitude: 0
};

document.addEventListener('DOMContentLoaded', async () => {
    await initializeSession();
    initializeVisualizer();
    initializeSpeechRecognition();

    // Auto-start listening if permission allows (user gesture usually required first)
    // For now, we wait for user to click mic
    updateStatus('Tap microphone to speak');
});

// --- VISUALIZER ENGINE --- //
function initializeVisualizer() {
    visualizerCanvas = document.getElementById('visualizer');
    visualizerCtx = visualizerCanvas.getContext('2d');

    // High DPI Canvas
    const dpr = window.devicePixelRatio || 1;
    const rect = visualizerCanvas.getBoundingClientRect();
    visualizerCanvas.width = rect.width * dpr;
    visualizerCanvas.height = rect.height * dpr;
    visualizerCtx.scale(dpr, dpr);

    animateOrb();
}

function ensureAudioContext() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
    }
    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }
}

async function connectMicrophone() {
    try {
        ensureAudioContext();
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        microphone = audioContext.createMediaStreamSource(stream);
        microphone.connect(analyser);
        return true;
    } catch (err) {
        console.error('Mic access denied:', err);
        alert('Microphone access is required for this experience.');
        return false;
    }
}

function connectAudioSource(audioElement) {
    ensureAudioContext();
    // Disconnect mic temporarily if needed, or mix. 
    // Here we create a new source for the audio element.
    const source = audioContext.createMediaElementSource(audioElement);
    source.connect(analyser);
    source.connect(audioContext.destination); // Play to speakers
}

function animateOrb() {
    const width = visualizerCanvas.width / (window.devicePixelRatio || 1);
    const height = visualizerCanvas.height / (window.devicePixelRatio || 1);
    const centerX = width / 2;
    const centerY = height / 2;

    visualizerCtx.clearRect(0, 0, width, height);

    // Get Audio Data
    let frequency = 0;
    if (analyser && (isListening || isSpeaking)) {
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(dataArray);

        // Calculate average volume/frequency
        const sum = dataArray.reduce((a, b) => a + b, 0);
        frequency = sum / dataArray.length;
    }

    // Orb State Logic
    if (isThinking) {
        orb.color1 = '255, 255, 255'; // White flash
        orb.radius = 40 + Math.sin(Date.now() / 100) * 5; // Fast pulse
    } else if (isListening) {
        orb.color1 = '255, 255, 255'; // White/Blue active
        // Expand based on voice volume
        const targetRadius = 60 + (frequency / 3);
        orb.radius += (targetRadius - orb.radius) * 0.2; // Smooth transition
    } else if (isSpeaking) {
        orb.color1 = '59, 130, 246'; // Blue
        const targetRadius = 50 + (frequency / 2);
        orb.radius += (targetRadius - orb.radius) * 0.2;
    } else {
        // Idle
        orb.color1 = '30, 30, 30'; // Dark Gray
        orb.radius = 30 + Math.sin(Date.now() / 2000) * 2; // Slow breathe
    }

    // Draw Orb (Glowing Circle)
    const gradient = visualizerCtx.createRadialGradient(centerX, centerY, 0, centerX, centerY, orb.radius * 2);
    gradient.addColorStop(0, `rgba(${orb.color1}, 1)`);
    gradient.addColorStop(0.5, `rgba(${orb.color1}, 0.4)`);
    gradient.addColorStop(1, `rgba(${orb.color1}, 0)`);

    visualizerCtx.fillStyle = gradient;
    visualizerCtx.beginPath();
    visualizerCtx.arc(centerX, centerY, orb.radius * 2, 0, Math.PI * 2);
    visualizerCtx.fill();

    // Core
    visualizerCtx.fillStyle = `rgba(255, 255, 255, ${isThinking ? 0.9 : 0.8})`;
    visualizerCtx.beginPath();
    visualizerCtx.arc(centerX, centerY, isThinking ? 10 : orb.radius * 0.3, 0, Math.PI * 2);
    visualizerCtx.fill();

    animationId = requestAnimationFrame(animateOrb);
}


// --- SPEECH & LOGIC --- //

function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isListening = true;
            ensureAudioContext(); // Resume context if suspended
            updateStatus("Listening...");
            document.getElementById('micBtn').classList.add('listening');
        };

        recognition.onend = () => {
            if (isListening) { // If it stopped naturally, not manually
                isListening = false;
                // Don't reset status if we are thinking (handled in onresult)
            }
            document.getElementById('micBtn').classList.remove('listening');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            processUserMessage(transcript);
        };

        recognition.onerror = (e) => {
            console.error("Speech error", e);
            isListening = false;
            updateStatus("Tap microphone to speak");
        };

    } else {
        alert("Speech recognition not supported.");
    }
}

async function toggleMic() {
    if (isListening) {
        recognition.stop();
        isListening = false;
        updateStatus("Tap microphone to speak");
    } else {
        const granted = await connectMicrophone();
        if (granted) {
            recognition.start();
        }
    }
}

async function processUserMessage(text) {
    isListening = false;
    isThinking = true;
    updateStatus("Thinking...");

    // Send to backend
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                session_id: sessionId
            })
        });

        const data = await response.json();
        isThinking = false;

        handleAIResponse(data);

    } catch (error) {
        isThinking = false;
        updateStatus("Connection Error");
        console.error(error);
    }
}

function handleAIResponse(data) {
    if (data.products && data.products.length > 0) {
        // Show product overlay
        renderProducts(data.products);
        const overlay = document.getElementById('contentOverlay');
        overlay.classList.add('active');

        // Short Voice Response
        updateStatus("Products Found");
        speak("I found some products for you."); // Or data.message if brief

    } else {
        // Voice only interaction
        document.getElementById('contentOverlay').classList.remove('active');
        updateStatus("Speaking...");
        speak(data.message);
    }
}

// --- AUDIO PLAYBACK --- //

function speak(text) {
    if (!text) return;

    // ElevenLabs Proxy
    fetch('http://localhost:8001/api/assistant/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text })
    })
        .then(res => res.blob())
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const audio = new Audio();
            audio.src = url;
            audio.crossOrigin = "anonymous"; // Important for AudioContext

            // Wait for load to connect source
            audio.addEventListener('canplay', () => {
                connectAudioSource(audio);
                audio.play();
            });

            audio.onplay = () => { isSpeaking = true; updateStatus("Speaking..."); };
            audio.onended = () => { isSpeaking = false; updateStatus("Tap microphone to speak"); };

        })
        .catch(err => console.error("TTS Error", err));
}

// --- UI UTILS --- //

function updateStatus(text) {
    const el = document.getElementById('statusText');
    el.textContent = text;
    el.classList.add('visible');
}

function renderProducts(products) {
    const overlay = document.getElementById('contentOverlay');
    overlay.innerHTML = ''; // Clear

    const grid = document.createElement('div');
    grid.className = 'products-grid';

    products.forEach(p => {
        const meta = p.metadata || {};
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <img src="${meta.image_url || ''}" class="product-image" onerror="this.style.display='none'">
            <div class="product-info">
                <div class="product-title">${meta.title}</div>
                <div class="product-price">₹${meta.price || 0}</div>
            </div>
        `;
        grid.appendChild(card);
    });

    overlay.appendChild(grid);
}

// Session & Init
async function initializeSession() {
    try {
        const res = await fetch(`${API_BASE}/session/new`, { method: 'POST' });
        const data = await res.json();
        sessionId = data.session_id;
    } catch (e) { console.error("Session Init Fail", e); }
}

function toggleTextInput() {
    const overlay = document.getElementById('inputOverlay');
    overlay.classList.toggle('active');
    if (overlay.classList.contains('active')) {
        document.getElementById('textInput').focus();
    }
}

function handleKeyPress(e) {
    if (e.key === 'Enter') {
        const input = document.getElementById('textInput');
        processUserMessage(input.value);
        input.value = '';
        toggleTextInput(); // Hide after send
    }
}

function endSession() {
    if (confirm("End Session?")) location.reload();
}

function closeWindow() {
    window.close(); // Only works if opened by script, but good for demo
}
