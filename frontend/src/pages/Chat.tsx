// frontend/src/pages/Chat.tsx

import { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Navigation } from '@/components/Navigation';
import { 
    ChatHeader, 
    ChatMessages, 
    ScrollToBottomButton, 
    QuickActions, 
    ChatInput 
} from '@/components/chat';
import { chatApi, ApiError } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { useStreamingText } from '@/hooks/useStreamingText';
import { useAutoScroll } from '@/hooks/useAutoScroll';
import { useChatSession } from '@/hooks/useChatSession';

export default function Chat() {
    const { t } = useTranslation();
    const { toast } = useToast();
    const [inputValue, setInputValue] = useState('');
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Custom hooks
    const { 
        messages, 
        setMessages, 
        sessionId, 
        setSessionId, 
        isLoadingSession, 
        clearSession: clearSessionData 
    } = useChatSession(t);

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
                        ? { ...msg, text: fullText, isStreaming: false }
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
                if (responseMetadata.show_form && responseMetadata.form_data) {
                    console.log(
                        'Portfolio form data:',
                        responseMetadata.form_data
                    );
                }
                if (responseMetadata.portfolio_summary) {
                    console.log(
                        'Portfolio summary:',
                        responseMetadata.portfolio_summary
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
                              }
                            : msg
                    )
                );

                if (response.show_form && response.form_data) {
                    console.log('Portfolio form data:', response.form_data);
                }
                if (response.portfolio_summary) {
                    console.log(
                        'Portfolio summary:',
                        response.portfolio_summary
                    );
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
                <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
                    <ChatHeader error={error} />

                    <ChatMessages
                        ref={messagesContainerRef}
                        messages={messages}
                        isLoadingSession={isLoadingSession}
                        streamedText={streamedText}
                        isThinking={isThinking}
                        isStreaming={isStreaming}
                        onCancelStream={cancelStream}
                        messagesEndRef={messagesEndRef}
                        userScrolled={userScrolled}
                        showScrollButton={showScrollButton}
                    />

                    <ScrollToBottomButton 
                        show={showScrollButton} 
                        onClick={scrollToBottom} 
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
            </main>
        </div>
    );
}
