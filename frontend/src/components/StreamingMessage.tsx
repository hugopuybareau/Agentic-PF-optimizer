// frontend/src/components/StreamingMessage.tsx

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useTranslation } from 'react-i18next';

interface StreamingMessageProps {
    text: string;
    isThinking: boolean;
    isStreaming: boolean;
    timestamp: Date;
    onCancel?: () => void;
}

const ProgressiveMarkdown: React.FC<{ text: string }> = ({ text }) => (
    <div className="prose prose-slate max-w-none dark:prose-invert">
        <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
                li: ({ children, ...props }) => (
                    <li className="ml-4" {...props}>
                        {children}
                    </li>
                ),
                code: ({ children, ...props }) => {
                    const isInline = !props.className?.includes('language-');
                    if (isInline) {
                        return (
                            <code className="bg-muted px-1 rounded" {...props}>
                                {children}
                            </code>
                        );
                    }
                    return (
                        <pre className="bg-muted rounded px-2 py-1 font-mono text-sm">
                            <code {...props}>{children}</code>
                        </pre>
                    );
                },
            }}
        >
            {text}
        </ReactMarkdown>
    </div>
);

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
