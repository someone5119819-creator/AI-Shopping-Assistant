import React from 'react';
import { Camera } from 'lucide-react';

export default function CameraViewport({ isActive, videoRef }) {
    if (!isActive) return null;

    return (
        <div className="w-full aspect-[3/4] bg-black rounded-3xl overflow-hidden relative mb-4 animate-in fade-in zoom-in duration-300">
            {/* Live Video Feed */}
            <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
            />

            {/* Overlay UI */}
            <div className="absolute top-4 right-4 bg-black/40 backdrop-blur-md px-3 py-1 rounded-full flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                <span className="text-white text-xs font-medium">Live Vision</span>
            </div>

            {/* Scan overlay lines (decorative) */}
            <div className="absolute inset-x-8 top-1/2 h-48 -translate-y-1/2 border-2 border-white/20 rounded-xl pointer-events-none">
                <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-white" />
                <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-white" />
                <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-white" />
                <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-white" />
            </div>
        </div>
    );
}
