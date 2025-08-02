// frontend/src/pages/Chat.tsx

import { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Navigation } from '@/components/Navigation';
import { chatApi, ApiError } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

type Message = {
    id: string;
    text: string;
    isUser: boolean;
    timestamp: Date;
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
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            text: inputValue,
            isUser: true,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        const messageText = inputValue;
        setInputValue('');
        setIsLoading(true);
        setError(null);

        try {
            const response = await chatApi.sendMessage({
                message: messageText,
                session_id: sessionId || undefined,
            });

            if (response.session_id && response.session_id !== sessionId) {
                setSessionId(response.session_id);
            }

            const aiResponse: Message = {
                id: (Date.now() + 1).toString(),
                text: response.message,
                isUser: false,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, aiResponse]);

            // Handle special UI hints or form display
            if (response.show_form && response.form_data) {
                // TODO: Handle portfolio form display
                console.log('Portfolio form data:', response.form_data);
            }

            if (response.portfolio_summary) {
                console.log('Portfolio summary:', response.portfolio_summary);
            }
        } catch (err) {
            const errorMessage =
                err instanceof ApiError
                    ? `${t('chat.errorOccurred')}: ${err.message}`
                    : t('chat.failedToSend');

            setError(errorMessage);

            const errorResponse: Message = {
                id: (Date.now() + 1).toString(),
                text: errorMessage,
                isUser: false,
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorResponse]);
        } finally {
            setIsLoading(false);
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
                        {messages.map((message) => (
                            <div
                                key={message.id}
                                className={`flex ${
                                    message.isUser
                                        ? 'justify-end'
                                        : 'justify-start'
                                } animate-fade-in-up`}
                            >
                                <div
                                    className={`max-w-[80%] ${
                                        message.isUser
                                            ? 'bg-primary text-primary-foreground'
                                            : 'card-silver'
                                    } p-4 rounded-lg`}
                                >
                                    {!message.isUser && (
                                        <div className="flex items-center space-x-2 mb-2">
                                            <div className="w-6 h-6 bg-accent rounded-full flex items-center justify-center">
                                                <span className="text-xs font-medium">
                                                    P
                                                </span>
                                            </div>
                                            <span className="text-sub text-xs">
                                                {t('chat.silverAgent')}
                                            </span>
                                        </div>
                                    )}
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
                        ))}

                        {isLoading && (
                            <div className="flex justify-start animate-fade-in-up">
                                <div className="card-silver p-4 rounded-lg">
                                    <div className="flex items-center space-x-2 mb-2">
                                        <div className="w-6 h-6 bg-accent rounded-full flex items-center justify-center">
                                            <span className="text-xs font-medium">
                                                P
                                            </span>
                                        </div>
                                        <span className="text-sub text-xs">
                                            {t('chat.silverAgent')}
                                        </span>
                                    </div>
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
                                </div>
                            </div>
                        )}
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
                                    disabled={!inputValue.trim() || isLoading}
                                    className="btn-primary px-4 py-2 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {t('chat.send')}
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
