// frontend/src/components/StreamingMessage.tsx

import React from 'react';
import { useTranslation } from 'react-i18next';

interface StreamingMessageProps {
    text: string;
    isThinking: boolean;
    isStreaming: boolean;
    timestamp: Date;
    onCancel?: () => void;
}

const ProgressiveMarkdown: React.FC<{ text: string }> = ({ text }) => {
    // Simple progressive markdown renderer
    // This handles basic formatting as text streams in
    const renderText = (content: string) => {
        // Split by lines to handle progressive list building
        const lines = content.split('\n');
        
        return lines.map((line, index) => {
            // Handle bullet points
            if (line.trim().startsWith('- ') || line.trim().startsWith('• ')) {
                return (
                    <li key={index} className="ml-4 list-disc">
                        {line.replace(/^[-•]\s*/, '')}
                    </li>
                );
            }
            
            // Handle numbered lists
            if (/^\d+\.\s/.test(line.trim())) {
                return (
                    <li key={index} className="ml-4 list-decimal">
                        {line.replace(/^\d+\.\s*/, '')}
                    </li>
                );
            }
            
            // Handle code blocks (basic)
            if (line.trim().startsWith('```')) {
                return (
                    <div key={index} className="bg-muted rounded px-2 py-1 font-mono text-sm">
                        {line.replace(/```\w*/, '')}
                    </div>
                );
            }
            
            // Handle inline code
            const codeFormatted = line.replace(/`([^`]+)`/g, '<code class="bg-muted px-1 rounded">$1</code>');
            
            // Handle bold
            const boldFormatted = codeFormatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
            
            // Handle italic
            const italicFormatted = boldFormatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
            
            return (
                <span
                    key={index}
                    dangerouslySetInnerHTML={{ __html: italicFormatted }}
                />
            );
        });
    };

    return <div className="space-y-1">{renderText(text)}</div>;
};

const ThinkingAnimation: React.FC = () => {
    return (
        <div className="flex space-x-1 items-center">
            <div className="flex space-x-1">
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                <div
                    className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                    style={{ animationDelay: '0.1s' }}
                ></div>
                <div
                    className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                    style={{ animationDelay: '0.2s' }}
                ></div>
            </div>
            <span className="text-xs text-muted-foreground ml-2">
                Thinking...
            </span>
        </div>
    );
};

export const StreamingMessage: React.FC<StreamingMessageProps> = ({
    text,
    isThinking,
    isStreaming,
    timestamp,
    onCancel,
}) => {
    const { t } = useTranslation();

    return (
        <div className="flex justify-start animate-fade-in-up">
            <div className="card-silver p-4 rounded-lg max-w-[80%]">
                {/* Agent Header */}
                <div className="flex items-center space-x-2 mb-2">
                    <span className="text-sub text-xs">
                        {t('chat.silverAgent')}
                    </span>
                    {isStreaming && onCancel && (
                        <button
                            onClick={onCancel}
                            className="ml-auto text-xs text-muted-foreground hover:text-foreground transition-colors"
                            title="Cancel streaming"
                        >
                            ✕
                        </button>
                    )}
                </div>

                {/* Content */}
                <div className="text-nav">
                    {isThinking ? (
                        <ThinkingAnimation />
                    ) : (
                        <>
                            <ProgressiveMarkdown text={text} />
                            {isStreaming && (
                                <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1" />
                            )}
                        </>
                    )}
                </div>

                {/* Timestamp */}
                <span className="text-xs opacity-60 mt-2 block">
                    {timestamp.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                    })}
                </span>
            </div>
        </div>
    );
};