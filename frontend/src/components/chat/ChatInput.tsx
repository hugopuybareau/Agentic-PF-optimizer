import { RefObject } from 'react';
import { useTranslation } from 'react-i18next';

interface ChatInputProps {
    inputValue: string;
    onInputChange: (value: string) => void;
    onSendMessage: () => void;
    onFileUpload: () => void;
    isStreaming: boolean;
    fileInputRef: RefObject<HTMLInputElement>;
}

export function ChatInput({
    inputValue,
    onInputChange,
    onSendMessage,
    onFileUpload,
    isStreaming,
    fileInputRef,
}: ChatInputProps) {
    const { t } = useTranslation();

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && !e.shiftKey && !isStreaming) {
            onSendMessage();
        }
    };

    return (
        <div className="card-silver rounded-lg">
            <div className="p-4">
                <div className="flex space-x-4">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => onInputChange(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={t('chat.placeholder')}
                        className="flex-1 bg-transparent border-none outline-none text-nav placeholder:text-muted-foreground relative z-10"
                    />

                    <div className="flex items-center space-x-2 relative z-10">
                        {/* File Upload */}
                        <button
                            onClick={onFileUpload}
                            className="p-2 hover:bg-accent rounded-lg transition-colors"
                            title={t('chat.uploadFile')}
                        >
                            <svg
                                className="w-4 h-4"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
                                />
                            </svg>
                        </button>

                        {/* Send Button */}
                        <button
                            onClick={onSendMessage}
                            disabled={!inputValue.trim() || isStreaming}
                            className="btn-primary px-4 py-2 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isStreaming ? 'Streaming...' : t('chat.send')}
                        </button>
                    </div>
                </div>

                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv,.pdf"
                    className="hidden"
                />
            </div>
        </div>
    );
}
