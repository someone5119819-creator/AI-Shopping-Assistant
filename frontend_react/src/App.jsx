import React, { useState, useEffect, useRef } from 'react';
import TopBar from './components/TopBar';
import ActionBar from './components/ActionBar';
import SiriOrb from './components/SiriOrb';
import TranscriptOverlay from './components/TranscriptOverlay';
import ProductResults from './components/ProductResults';
import CameraViewport from './components/CameraViewport';
import { useAssistant } from './hooks/useAssistant';

function App() {
  const {
    status,
    isListening,
    isThinking,
    isSpeaking,
    liveUserText,
    liveAiText,
    products,
    isCameraOpen,
    startListening,
    stopListening,
    sendMessage
  } = useAssistant();

  const [hasInteracted, setHasInteracted] = useState(false);
  const [isKeyboardOpen, setIsKeyboardOpen] = useState(false);
  const videoRef = useRef(null);

  // Determine orbital status
  const orbStatus = isThinking ? 'thinking'
    : isSpeaking ? 'speaking'
      : isListening ? 'listening'
        : 'idle';

  // Handle Interactions
  const handleMicClick = () => {
    setHasInteracted(true);
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const handleKeyboardClick = () => {
    setHasInteracted(true);
    setIsKeyboardOpen(!isKeyboardOpen);
  };

  const handleTextSubmit = (text) => {
    sendMessage(text);
    setIsKeyboardOpen(false);
    setHasInteracted(true); // Ensure we go to active state on text submit too
  };

  // Camera Logic (Placeholder integration)
  useEffect(() => {
    if (isCameraOpen && videoRef.current) {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
          videoRef.current.srcObject = stream;
        })
        .catch(err => console.error("Camera access denied:", err));
    }
  }, [isCameraOpen]);


  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)] font-['Roboto'] flex flex-col relative overflow-hidden">
      <TopBar />

      <main className="flex-1 flex flex-col relative px-4 w-full max-w-md mx-auto pb-24 h-full">

        {/* IDLE VIEW */}
        {!hasInteracted && (
          <div className="flex-1 flex flex-col justify-center items-start pb-20 animate-in fade-in duration-700">
            <div className="w-full mb-8 flex justify-center">
              {/* Optional: Add a subtle ambient orb here if desired, or keep clean as per 'One-time header' */}
              <div className="w-64 h-64 rounded-full bg-gradient-to-tr from-blue-50 to-purple-50 blur-3xl opacity-50 absolute" />
            </div>
            <h1 className="text-4xl font-light text-black/80 leading-tight tracking-tight z-10">
              Hi,<br />
              <span className="text-black font-medium">What can I help you with?</span>
            </h1>
          </div>
        )}

        {/* ACTIVE VIEW */}
        {hasInteracted && (
          <div className="flex-1 flex flex-col gap-4 animate-in slide-in-from-bottom-10 duration-500 h-full">

            {/* 1. Dynamic Orb (Top) */}
            <div className="flex justify-start pt-2 shrink-0">
              <SiriOrb status={orbStatus} />
            </div>

            {/* 2. Assistant Transcript (Below Orb) */}
            <div className="min-h-[40px] shrink-0">
              <p className="text-2xl font-normal text-black/90 leading-snug whitespace-pre-wrap">
                {liveAiText || (isThinking ? "..." : (status === 'Speaking...' ? "" : ""))}
              </p>
            </div>

            {/* 3. Dynamic Content Area (Camera or Products) */}
            {/* Flex-1 allows this to take available space */}
            <div className="flex-1 flex flex-col justify-end gap-4 min-h-0">
              {/* Camera Viewport */}
              <CameraViewport isActive={isCameraOpen} videoRef={videoRef} />

              {/* Product Results (Collapsible Section) */}
              <ProductResults products={products} />
            </div>

            {/* 4. User Transcript / Input (Bottom) */}
            <div className={`mt-auto shrink-0 transition-all duration-300 ${isKeyboardOpen ? 'pb-2' : 'pb-4'}`}>
              <TranscriptOverlay
                userText={liveUserText}
                isKeyboardOpen={isKeyboardOpen}
                onTextSubmit={handleTextSubmit}
              />
            </div>
          </div>
        )}

      </main>

      {/* Floating Action Bar */}
      <div className="fixed bottom-0 left-0 w-full bg-gradient-to-t from-white via-white to-transparent pb-4 pt-10 px-4 z-50">
        <div className="max-w-md mx-auto">
          <ActionBar
            isListening={isListening}
            onMicClick={handleMicClick}
            onKeyboardClick={handleKeyboardClick}
            onEndCall={() => window.location.reload()}
          />
        </div>
      </div>

    </div>
  );
}

export default App;
