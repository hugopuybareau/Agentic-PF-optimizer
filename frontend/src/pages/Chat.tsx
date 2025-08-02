// frontend/src/pages/Chat.tsx

import { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Navigation } from '@/components/Navigation';
import { StreamingMessage } from '@/components/StreamingMessage';
import { chatApi, ApiError } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { useStreamingText } from '@/hooks/useStreamingText';

type Message = {
    id: string;
    text: string;
    isUser: boolean;
    timestamp: Date;
    isStreaming?: boolean;
};

const getInitialMessages = (t: (key: string) => string): Message[] => [
    {
        id: '1',
        text: t('chat.initialMessage'),
        isUser: false,
        timestamp: new Date(),
    },
];

export default function Chat() {
    const { t } = useTranslation();
    const { toast } = useToast();
    const [messages, setMessages] = useState<Message[]>(getInitialMessages(t));
    const [inputValue, setInputValue] = useState('');
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);

    const {
        streamedText,
        isStreaming,
        isThinking,
        metadata,
        error: streamError,
        startStreaming,
        cancelStream,
        reset: resetStream,
    } = useStreamingText({
        onComplete: (fullText, responseMetadata) => {
            // Replace the streaming message with the final message
            setMessages(prev => prev.map(msg => 
                msg.id === streamingMessageId 
                    ? { ...msg, text: fullText, isStreaming: false }
                    : msg
            ));
            
            // Handle additional response metadata
            if (responseMetadata) {
                if (responseMetadata.session_id && responseMetadata.session_id !== sessionId) {
                    setSessionId(responseMetadata.session_id);
                }
                
                if (responseMetadata.show_form && responseMetadata.form_data) {
                    console.log('Portfolio form data:', responseMetadata.form_data);
                }
                
                if (responseMetadata.portfolio_summary) {
                    console.log('Portfolio summary:', responseMetadata.portfolio_summary);
                }
            }
            
            setStreamingMessageId(null);
        },
        onError: (errorMessage) => {
            // Replace streaming message with error message
            if (streamingMessageId) {
                setMessages(prev => prev.map(msg => 
                    msg.id === streamingMessageId 
                        ? { ...msg, text: `Error: ${errorMessage}`, isStreaming: false }
                        : msg
                ));
            }
            setStreamingMessageId(null);
            setError(errorMessage);
        },
        onStart: () => {
            setError(null);
        }
    });

    const handleSendMessage = async () => {
        if (!inputValue.trim() || isStreaming) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            text: inputValue,
            isUser: true,
            timestamp: new Date(),
        };

        // Add user message
        setMessages((prev) => [...prev, userMessage]);
        const messageText = inputValue;
        setInputValue('');
        setError(null);

        // Create streaming AI message placeholder
        const aiMessageId = (Date.now() + 1).toString();
        const aiMessage: Message = {
            id: aiMessageId,
            text: '',
            isUser: false,
            timestamp: new Date(),
            isStreaming: true,
        };
        
        setMessages((prev) => [...prev, aiMessage]);
        setStreamingMessageId(aiMessageId);

        try {
            const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
            await startStreaming(`${API_BASE_URL}/chat/message/stream`, {
                message: messageText,
                session_id: sessionId || undefined,
            });
        } catch (err) {
            console.error('Streaming failed, fallback to regular API:', err);
            
            // Fallback to non-streaming API
            try {
                const response = await chatApi.sendMessage({
                    message: messageText,
                    session_id: sessionId || undefined,
                });

                if (response.session_id && response.session_id !== sessionId) {
                    setSessionId(response.session_id);
                }

                // Update the streaming message with the complete response
                setMessages(prev => prev.map(msg => 
                    msg.id === aiMessageId 
                        ? { ...msg, text: response.message, isStreaming: false }
                        : msg
                ));

                // Handle special UI hints or form display
                if (response.show_form && response.form_data) {
                    console.log('Portfolio form data:', response.form_data);
                }

                if (response.portfolio_summary) {
                    console.log('Portfolio summary:', response.portfolio_summary);
                }
                
                setStreamingMessageId(null);
            } catch (fallbackErr) {
                const errorMessage =
                    fallbackErr instanceof ApiError
                        ? `${t('chat.errorOccurred')}: ${fallbackErr.message}`
                        : t('chat.failedToSend');

                setError(errorMessage);
                
                // Update streaming message with error
                setMessages(prev => prev.map(msg => 
                    msg.id === aiMessageId 
                        ? { ...msg, text: errorMessage, isStreaming: false }
                        : msg
                ));
                
                setStreamingMessageId(null);
            }
        }
    };

    const clearSession = async () => {
        if (sessionId) {
            try {
                await chatApi.clearSession(sessionId);
                setSessionId(null);
                setMessages(getInitialMessages(t));
                setError(null);
                
                toast({
                    title: t('chat.clearSession'),
                    description: t('chat.sessionClearedSuccessfully'),
                    variant: 'success',
                });
            } catch (err) {
                console.error('Failed to clear session:', err);
                
                const errorMessage = err instanceof ApiError 
                    ? err.message 
                    : t('chat.failedToClearSession');
                
                toast({
                    title: t('chat.clearSession'),
                    description: errorMessage,
                    variant: 'destructive',
                });
            }
        }
    };

    const handleFileUpload = () => {
        fileInputRef.current?.click();
    };

    const quickActions = [
        {
            label: t('chat.quickActions.analyzePortfolio'),
            action: () =>
                setInputValue(t('chat.quickActions.analyzePortfolioAction')),
        },
        {
            label: t('chat.quickActions.optimizeAllocation'),
            action: () =>
                setInputValue(t('chat.quickActions.optimizeAllocationAction')),
        },
        {
            label: t('chat.quickActions.marketNews'),
            action: () =>
                setInputValue(t('chat.quickActions.marketNewsAction')),
        },
        {
            label: t('chat.quickActions.riskAssessment'),
            action: () =>
                setInputValue(t('chat.quickActions.riskAssessmentAction')),
        },
    ];

    return (
        <div className="min-h-screen bg-background">
            <Navigation />

            <main className="pt-20 px-6 pb-6">
                <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
                    {/* Header */}
                    <div className="mb-6">
                        <div className="flex justify-between items-start">
                            <div>
                                <h1 className="text-hero mb-2">
                                    {t('chat.silverAgent')}
                                </h1>
                                <p className="text-sub">
                                    {t('chat.yourAIFinancialCopilot')}
                                </p>
                            </div>
                            {sessionId && (
                                <button
                                    onClick={clearSession}
                                    className="btn-ghost px-3 py-1 text-xs rounded-lg"
                                    title={t('chat.clearSessionTooltip')}
                                >
                                    {t('chat.clearSession')}
                                </button>
                            )}
                        </div>
                        {error && (
                            <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-lg text-red-700 text-sm">
                                {error}
                            </div>
                        )}
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto space-y-6 mb-6">
                        {messages.map((message) => {
                            // Handle streaming messages
                            if (!message.isUser && message.id === streamingMessageId) {
                                return (
                                    <StreamingMessage
                                        key={message.id}
                                        text={streamedText}
                                        isThinking={isThinking}
                                        isStreaming={isStreaming}
                                        timestamp={message.timestamp}
                                        onCancel={cancelStream}
                                    />
                                );
                            }

                            // Handle user messages
                            if (message.isUser) {
                                return (
                                    <div
                                        key={message.id}
                                        className="flex justify-end animate-fade-in-up"
                                    >
                                        <div className="max-w-[80%] bg-primary text-primary-foreground p-4 rounded-lg">
                                            <p className="text-nav">{message.text}</p>
                                            <span className="text-xs opacity-60 mt-2 block">
                                                {message.timestamp.toLocaleTimeString(
                                                    [],
                                                    {
                                                        hour: '2-digit',
                                                        minute: '2-digit',
                                                    }
                                                )}
                                            </span>
                                        </div>
                                    </div>
                                );
                            }

                            // Handle regular AI messages
                            return (
                                <StreamingMessage
                                    key={message.id}
                                    text={message.text}
                                    isThinking={false}
                                    isStreaming={false}
                                    timestamp={message.timestamp}
                                />
                            );
                        })}
                    </div>

                    {/* Quick Actions */}
                    <div className="mb-4">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                            {quickActions.map((action) => (
                                <button
                                    key={action.label}
                                    onClick={action.action}
                                    className="btn-ghost px-3 py-2 text-xs rounded-lg text-left"
                                >
                                    {action.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Input Area */}
                    <div className="card-silver p-4 rounded-lg">
                        <div className="flex space-x-4">
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyDown={(e) =>
                                    e.key === 'Enter' &&
                                    !e.shiftKey &&
                                    !isStreaming &&
                                    handleSendMessage()
                                }
                                placeholder={t('chat.placeholder')}
                                className="flex-1 bg-transparent border-none outline-none text-nav placeholder:text-muted-foreground"
                            />

                            <div className="flex items-center space-x-2">
                                {/* File Upload */}
                                <button
                                    onClick={handleFileUpload}
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
                                    onClick={handleSendMessage}
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
            </main>
        </div>
    );
}
