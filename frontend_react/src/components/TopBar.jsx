import React from 'react';
import { Subtract24Regular } from '@fluentui/react-icons';

export default function TopBar() {
    return (
        <div className="w-full h-10 flex items-center justify-between px-6 pt-6 mb-8">
            <h1 className="text-[color:var(--grey-500)] text-sm font-normal tracking-[0.17px] font-['Roboto']">
                Shopping assistant
            </h1>
            <button
                className="w-10 h-10 flex items-center justify-center rounded-full bg-[var(--common-white-hover)] hover:bg-black/5 transition-colors border-none p-0 cursor-pointer"
                aria-label="Minimize"
            >
                <Subtract24Regular className="text-black" />
            </button>
        </div>
    );
}
