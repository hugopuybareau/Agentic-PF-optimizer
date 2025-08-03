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

// Add intelligent line breaks for backend that doesn't send newlines
const addLineBreaks = (text: string): string => {
    let patchedText = text;
    
    // Add intelligent line breaks for common patterns
    // 1. Add newline before numbered lists (1. 2. 3. etc.)
    patchedText = patchedText.replace(/(\S)\s+(\d+\.\s)/g, '$1\n\n$2');
    
    // 2. Add newline before bullet points (- * +)
    patchedText = patchedText.replace(/(\S)\s+([-*+]\s)/g, '$1\n\n$2');
    
    // 3. Add newline before headers (# ## ### etc.)
    patchedText = patchedText.replace(/(\S)\s+(#{1,6}\s)/g, '$1\n\n$2');
    
    // 4. Add newline before horizontal rules (--- ***)
    patchedText = patchedText.replace(/(\S)\s+(---+|\*\*\*+)/g, '$1\n\n$2');
    
    // 5. Add newline before blockquotes (>)
    patchedText = patchedText.replace(/(\S)\s+(>\s)/g, '$1\n\n$2');
    
    return patchedText;
};

// Fix incomplete markdown elements during streaming
const fixIncompleteMarkdown = (text: string): string => {
    let patchedText = text;
    
    // Fix unclosed code blocks (triple backticks)
    const tripleBacktickMatches = (patchedText.match(/```/g) || []).length;
    if (tripleBacktickMatches % 2 === 1) {
        patchedText += '\n```';
    }
    
    // Fix unclosed inline code (single backticks)
    const backtickMatches = (patchedText.match(/`/g) || []).length;
    if (backtickMatches % 2 === 1) {
        patchedText += '`';
    }
    
    // Fix unclosed bold (**text)
    const boldMatches = (patchedText.match(/\*\*/g) || []).length;
    if (boldMatches % 2 === 1) {
        patchedText += '**';
    }
    
    // Fix unclosed italic (*text, but not ** or ***)
    const italicMatches = (patchedText.match(/(?<!\*)\*(?!\*)/g) || []).length;
    if (italicMatches % 2 === 1) {
        patchedText += '*';
    }
    
    // Fix unclosed underline bold (__text)
    const underlineBoldMatches = (patchedText.match(/__/g) || []).length;
    if (underlineBoldMatches % 2 === 1) {
        patchedText += '__';
    }
    
    // Fix unclosed underline italic (_text, but not __)
    const underlineItalicMatches = (patchedText.match(/(?<!_)_(?!_)/g) || []).length;
    if (underlineItalicMatches % 2 === 1) {
        patchedText += '_';
    }
    
    // Fix incomplete links ([text without closing )
    patchedText = patchedText.replace(/\[([^\]]*)\](?!\()/g, '[$1]()');
    
    // Fix incomplete strikethrough (~~text)
    const strikethroughMatches = (patchedText.match(/~~/g) || []).length;
    if (strikethroughMatches % 2 === 1) {
        patchedText += '~~';
    }
    
    return patchedText;
};

// Safe markdown renderer for streaming content
const ProgressiveMarkdown: React.FC<{ text: string; isStreaming?: boolean }> = ({ text, isStreaming = false }) => {
    // Always add line breaks since backend doesn't send them
    let displayText = addLineBreaks(text);
    
    // During streaming, also fix incomplete markdown elements
    if (isStreaming) {
        displayText = fixIncompleteMarkdown(displayText);
    }
    
    return (
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
                {displayText}
            </ReactMarkdown>
        </div>
    );
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
                            <ProgressiveMarkdown text={text} isStreaming={isStreaming} />
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
