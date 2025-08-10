// frontend/src/pages/Chat.tsx

import { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Navigation } from '@/components/Navigation';
import {
    ChatHeader,
    ChatMessages,
    QuickActions,
    ChatInput,
} from '@/components/chat';
import LivePortfolioView from '@/components/chat/LivePortfolioView';
import { chatApi, ApiError } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { useStreamingText } from '@/hooks/useStreamingText';
import { useAutoScroll } from '@/hooks/useAutoScroll';
import { useChatSession } from '@/hooks/useChatSession';
import { usePortfolio } from '@/hooks/usePortfolio';

export default function Chat() {
    const { t } = useTranslation();
    const { toast } = useToast();
    const [inputValue, setInputValue] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [processingConfirmation, setProcessingConfirmation] = useState<
        string | null
    >(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Custom hooks
    const {
        messages,
        setMessages,
        sessionId,
        setSessionId,
        isLoadingSession,
        clearSession: clearSessionData,
    } = useChatSession(t);

    const {
        portfolioSummary,
        isLoading: isLoadingPortfolio,
        fetchPortfolio,
        confirmAction: confirmPortfolioAction,
    } = usePortfolio();

    const {
        messagesEndRef,
        messagesContainerRef,
        showScrollButton,
        userScrolled,
        scrollToBottom,
        autoScrollToBottom,
        resetScrollState,
    } = useAutoScroll();

    const {
        streamedText,
        isStreaming,
        isThinking,
        startStreaming,
        cancelStream,
    } = useStreamingText({
        onComplete: (fullText, responseMetadata, aiMessageId) => {
            setMessages((prev) =>
                prev.map((msg) =>
                    msg.id === aiMessageId
                        ? {
                              ...msg,
                              text: fullText,
                              isStreaming: false,
                              metadata: responseMetadata,
                          }
                        : msg
                )
            );

            if (responseMetadata) {
                if (
                    responseMetadata.session_id &&
                    responseMetadata.session_id !== sessionId
                ) {
                    setSessionId(responseMetadata.session_id);
                }

                // Handle confirmation requests
                if (responseMetadata.confirmation_request) {
                    console.log(
                        'Confirmation request received:',
                        responseMetadata.confirmation_request
                    );
                }

                // Handle portfolio updates
                if (responseMetadata.portfolio_summary) {
                    console.log(
                        'Portfolio summary:',
                        responseMetadata.portfolio_summary
                    );
                    // Refresh portfolio view
                    fetchPortfolio();
                }

                if (responseMetadata.show_form && responseMetadata.form_data) {
                    console.log(
                        'Portfolio form data:',
                        responseMetadata.form_data
                    );
                }
            }
        },
        onError: (errorMessage, aiMessageId) => {
            setMessages((prev) =>
                prev.map((msg) =>
                    msg.id === aiMessageId
                        ? {
                              ...msg,
                              text: `Error: ${errorMessage}`,
                              isStreaming: false,
                          }
                        : msg
                )
            );
            setError(errorMessage);
        },
        onStart: () => {
            setError(null);
        },
    });

    // Auto-scroll when new messages are added
    autoScrollToBottom(messages, streamedText, isLoadingSession);

    const handleSendMessage = async () => {
        if (!inputValue.trim() || isStreaming) return;

        const userMessage = {
            id: crypto.randomUUID(),
            text: inputValue,
            isUser: true,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        const messageText = inputValue;
        setInputValue('');
        setError(null);

        // Reset scroll state when sending a new message
        resetScrollState();

        // Create streaming AI message placeholder with a unique ID
        const aiMessageId = crypto.randomUUID();
        const aiMessage = {
            id: aiMessageId,
            text: '',
            isUser: false,
            timestamp: new Date(),
            isStreaming: true,
        };

        setMessages((prev) => [...prev, aiMessage]);

        try {
            const API_BASE_URL =
                import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
            await startStreaming(
                `${API_BASE_URL}/chat/message/stream`,
                {
                    message: messageText,
                    session_id: sessionId || undefined,
                },
                aiMessageId
            );
        } catch (err) {
            console.error('Streaming failed, fallback to regular API:', err);

            try {
                const response = await chatApi.sendMessage({
                    message: messageText,
                    session_id: sessionId || undefined,
                });

                if (response.session_id && response.session_id !== sessionId) {
                    setSessionId(response.session_id);
                }

                setMessages((prev) =>
                    prev.map((msg) =>
                        msg.id === aiMessageId
                            ? {
                                  ...msg,
                                  text: response.message,
                                  isStreaming: false,
                                  metadata: {
                                      confirmation_request:
                                          response.confirmation_request,
                                      ui_hints: response.ui_hints,
                                  },
                              }
                            : msg
                    )
                );

                // Handle confirmation requests
                if (response.confirmation_request) {
                    console.log(
                        'Confirmation request:',
                        response.confirmation_request
                    );
                }

                // Refresh portfolio if updated
                if (response.portfolio_summary) {
                    fetchPortfolio();
                }

                if (response.show_form && response.form_data) {
                    console.log('Portfolio form data:', response.form_data);
                }
            } catch (fallbackErr) {
                const errorMessage =
                    fallbackErr instanceof ApiError
                        ? `${t('chat.errorOccurred')}: ${fallbackErr.message}`
                        : t('chat.failedToSend');

                setError(errorMessage);

                setMessages((prev) =>
                    prev.map((msg) =>
                        msg.id === aiMessageId
                            ? { ...msg, text: errorMessage, isStreaming: false }
                            : msg
                    )
                );
            }
        }
    };

    const handleConfirmAction = async (
        confirmationId: string,
        confirmed: boolean
    ) => {
        setProcessingConfirmation(confirmationId);

        try {
            const success = await confirmPortfolioAction(
                confirmationId,
                confirmed,
                sessionId || undefined
            );

            if (success) {
                // Remove confirmation from message metadata
                setMessages((prev) =>
                    prev.map((msg) => {
                        if (
                            msg.metadata?.confirmation_request
                                ?.confirmation_id === confirmationId
                        ) {
                            return {
                                ...msg,
                                metadata: {
                                    ...msg.metadata,
                                    confirmation_request: null,
                                    confirmation_processed: true,
                                },
                            };
                        }
                        return msg;
                    })
                );

                // Add a system message about the confirmation
                const systemMessage = {
                    id: crypto.randomUUID(),
                    text: confirmed
                        ? '✅ Portfolio updated successfully!'
                        : '❌ Action cancelled',
                    isUser: false,
                    timestamp: new Date(),
                };
                setMessages((prev) => [...prev, systemMessage]);
            }
        } finally {
            setProcessingConfirmation(null);
        }
    };

    const handleClearSession = async () => {
        const result = await clearSessionData();

        if (result.success) {
            setError(null);
            resetScrollState();
            toast({
                title: t('chat.clearSession'),
                description: t('chat.sessionClearedSuccessfully'),
                variant: 'success',
            });
        } else {
            toast({
                title: t('chat.clearSession'),
                description: result.error || t('chat.failedToClearSession'),
                variant: 'destructive',
            });
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
                <div className="max-w-7xl mx-auto flex gap-6">
                    {/* Chat Section */}
                    <div className="flex-1 h-[calc(100vh-8rem)] flex flex-col relative">
                        <ChatHeader error={error} />

                        <ChatMessages
                            ref={messagesContainerRef}
                            messages={messages}
                            isLoadingSession={isLoadingSession}
                            streamedText={streamedText}
                            isThinking={isThinking}
                            isStreaming={isStreaming}
                            onCancelStream={cancelStream}
                            onConfirmAction={handleConfirmAction}
                            processingConfirmation={processingConfirmation}
                            messagesEndRef={messagesEndRef}
                            userScrolled={userScrolled}
                            showScrollButton={showScrollButton}
                        />

                        <QuickActions
                            actions={quickActions}
                            sessionId={sessionId}
                            onClearSession={handleClearSession}
                        />

                        <ChatInput
                            inputValue={inputValue}
                            onInputChange={setInputValue}
                            onSendMessage={handleSendMessage}
                            onFileUpload={handleFileUpload}
                            isStreaming={isStreaming}
                            fileInputRef={fileInputRef}
                        />
                    </div>

                    {/* Live Portfolio View */}
                    <div className="w-96 hidden lg:block">
                        <div className="sticky top-24">
                            <LivePortfolioView
                                portfolioSummary={portfolioSummary}
                                isLoading={isLoadingPortfolio}
                                onRefresh={fetchPortfolio}
                                onAddAsset={() =>
                                    setInputValue(
                                        'I want to add an asset to my portfolio'
                                    )
                                }
                                isExpanded={true}
                                className="h-[calc(100vh-10rem)]"
                            />
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
