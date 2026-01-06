import React from 'react';

export default function TranscriptOverlay({ assistantText, userText, isKeyboardOpen, onTextSubmit }) {
    const [inputValue, setInputValue] = React.useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (inputValue.trim()) {
            onTextSubmit(inputValue);
            setInputValue('');
        }
    };

    return (
        <div className="flex flex-col w-full px-6 gap-6 transition-all duration-500">
            {/* Assistant Transcript */}
            <div className="min-h-[60px] flex items-end">
                <p className="text-[20px] leading-[1.3] font-medium text-black/90 whitespace-pre-wrap">
                    {assistantText || "Hi,\nWhat can I help you with?"}
                </p>
            </div>

            {/* User Transcript / Input */}
            <div className="min-h-[40px] flex items-start">
                {isKeyboardOpen ? (
                    <form onSubmit={handleSubmit} className="w-full">
                        <input
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            placeholder="Type your request..."
                            className="w-full p-3 rounded-xl bg-gray-100 border-none focus:ring-2 focus:ring-blue-500 outline-none text-base"
                            autoFocus
                        />
                    </form>
                ) : (
                    <p className="text-[16px] text-gray-400 italic">
                        {userText || "..."}
                    </p>
                )}
            </div>
        </div>
    );
}
