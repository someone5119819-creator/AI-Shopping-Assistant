import React from 'react';
import { Keyboard24Regular, Mic24Regular, CallEnd24Filled } from '@fluentui/react-icons';

export default function ActionBar({ onMicClick, onKeyboardClick, onEndCall, isListening }) {
    return (
        <div className="flex items-center justify-between w-full h-[50px] px-6 pb-6 mt-auto">
            {/* Keyboard Toggle */}
            <button
                onClick={onKeyboardClick}
                className="w-[50px] h-[50px] flex items-center justify-center rounded-full bg-[#f5f5f5] hover:bg-[#e0e0e0] border-none transition-colors"
                aria-label="Open Keyboard"
            >
                <Keyboard24Regular className="text-black" />
            </button>

            {/* Mic Button (Central) */}
            <button
                onClick={onMicClick}
                className={`w-[50px] h-[50px] flex items-center justify-center rounded-full border-none transition-all duration-300 ${isListening
                        ? 'bg-red-100 text-red-500 scale-110'
                        : 'bg-[#f5f5f5] hover:bg-[#e0e0e0] text-black'
                    }`}
                aria-label={isListening ? "Stop Listening" : "Start Listening"}
            >
                <Mic24Regular />
            </button>

            {/* End Call */}
            <button
                onClick={onEndCall}
                className="w-[50px] h-[50px] flex items-center justify-center rounded-full bg-[#f5f5f5] hover:bg-[#ffcccc] border-none transition-colors group"
                aria-label="End Session"
            >
                <CallEnd24Filled className="text-black group-hover:text-red-500" />
            </button>
        </div>
    );
}
