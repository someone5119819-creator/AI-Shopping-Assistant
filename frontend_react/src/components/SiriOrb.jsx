import React from 'react';
import Orb from '@/components/smoothui/siri-orb';

export default function SiriOrb({ status = 'idle' }) {
    // Map status to display text
    const statusText = {
        idle: '',
        listening: 'Listening...',
        thinking: 'Thinking...',
        speaking: 'Speaking...',
        processing: 'Processing...'
    }[status] || '';

    return (
        <div className="flex flex-col items-center justify-center gap-4 transition-all duration-500">
            <div className="relative w-[120px] h-[120px]">
                <Orb
                    className="w-full h-full"
                    size="120px"
                />
            </div>

            {/* Dynamic Status Text */}
            <div className={`h-6 text-[length:var(--typography-body2,14px)] text-[color:var(--grey-500)] tracking-[0.17px] font-medium transition-opacity duration-300 ${status === 'idle' ? 'opacity-0' : 'opacity-100'}`}>
                {statusText}
            </div>
        </div>
    );
}
