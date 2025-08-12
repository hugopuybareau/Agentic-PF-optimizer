// frontend/src/components/chat/ChatMessages.tsx

import { RefObject, forwardRef } from 'react';
import { useTranslation } from 'react-i18next';
import { StreamingMessage } from '@/components/StreamingMessage';

export type Message = {
    id: string;
    text: string;
    isUser: boolean;
    timestamp: Date;
    isStreaming?: boolean;
};

interface ChatMessagesProps {
    messages: Message[];
    isLoadingSession: boolean;
    streamedText: string;
    isThinking: boolean;
    isStreaming: boolean;
    onCancelStream: () => void;
    messagesEndRef: RefObject<HTMLDivElement>;
    userScrolled: boolean;
    showScrollButton: boolean;
}

export const ChatMessages = forwardRef<HTMLDivElement, ChatMessagesProps>(
    function ChatMessages({
        messages,
        isLoadingSession,
        streamedText,
        isThinking,
        isStreaming,
        onCancelStream,
        messagesEndRef,
        userScrolled,
        showScrollButton,
    }, messagesContainerRef) {
        const { t } = useTranslation();

        return (
            <div className="flex-1 relative">
                <div 
                    ref={messagesContainerRef}
                    className="h-full overflow-y-auto space-y-6 mb-6 scroll-smooth px-1"
                >
                    {isLoadingSession && (
                        <div className="flex justify-center items-center h-32">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                            <span className="ml-2 text-muted-foreground">
                                {t('chat.loadingSession')}
                            </span>
                        </div>
                    )}
                    {messages.map((message) => {
                        // Handle streaming AI messages
                        if (!message.isUser && message.isStreaming) {
                            return (
                                <StreamingMessage
                                    key={message.id}
                                    text={streamedText}
                                    isThinking={isThinking}
                                    isStreaming={isStreaming}
                                    timestamp={message.timestamp}
                                    onCancel={onCancelStream}
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
                                        <p className="text-nav">
                                            {message.text}
                                        </p>
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
                    <div ref={messagesEndRef} />
                </div>
            </div>
        );
    }
);
