// frontend/src/hooks/useChatSession.ts

import { useState, useEffect } from 'react';
import { chatApi } from '@/lib/api';
import { Message } from '@/components/chat/ChatMessages';

const SESSION_STORAGE_KEY = 'chat_session_id';
const MESSAGES_STORAGE_KEY = 'chat_messages';

const getInitialMessages = (t: (key: string) => string): Message[] => [
    {
        id: '1',
        text: t('chat.initialMessage'),
        isUser: false,
        timestamp: new Date(),
    },
];

export function useChatSession(t: (key: string) => string) {
    const [messages, setMessages] = useState<Message[]>(getInitialMessages(t));
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [isLoadingSession, setIsLoadingSession] = useState(true);

    // Session restoration on component mount and tab visibility changes
    useEffect(() => {
        const restoreSession = async () => {
            try {
                // Try to get saved session ID
                const savedSessionId = localStorage.getItem(SESSION_STORAGE_KEY);

                if (savedSessionId && savedSessionId !== sessionId) {
                    try {
                        const sessionData = await chatApi.getSession(savedSessionId);

                        // If session exists, restore it
                        if (sessionData && sessionData.messages) {
                            setSessionId(savedSessionId);

                            // Restore messages from backend
                            const restoredMessages = sessionData.messages.map(
                                (msg: {
                                    id: string;
                                    text: string;
                                    isUser: boolean;
                                    timestamp: string;
                                }) => ({
                                    id: msg.id,
                                    text: msg.text,
                                    isUser: msg.isUser,
                                    timestamp: new Date(msg.timestamp),
                                })
                            );

                            if (restoredMessages.length > 0) {
                                setMessages(restoredMessages);
                            } else {
                                setMessages(getInitialMessages(t));
                            }
                        } else {
                            localStorage.removeItem(SESSION_STORAGE_KEY);
                        }
                    } catch (err) {
                        // Clear localStorage if session not found
                        localStorage.removeItem(SESSION_STORAGE_KEY);
                    }
                }
            } catch (error) {
                console.error('Error in session restoration:', error);
            } finally {
                setIsLoadingSession(false);
            }
        };

        // Initial restoration on mount
        restoreSession();

        // Listen for tab visibility changes
        const handleVisibilityChange = () => {
            if (!document.hidden) {
                restoreSession();
            }
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);

        // Cleanup event listener
        return () => {
            document.removeEventListener('visibilitychange', handleVisibilityChange);
        };
    }, [sessionId, t]);

    // Save session ID to localStorage (messages are stored in backend)
    useEffect(() => {
        if (sessionId) {
            localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
        }
    }, [sessionId]);

    const clearSession = async (): Promise<{ success: boolean; error?: string }> => {
        if (sessionId) {
            try {
                await chatApi.clearSession(sessionId);
                setSessionId(null);
                setMessages(getInitialMessages(t));
                
                // Clear localStorage
                localStorage.removeItem(SESSION_STORAGE_KEY);
                localStorage.removeItem(MESSAGES_STORAGE_KEY);
                
                return { success: true };
            } catch (err) {
                console.error('Failed to clear session:', err);
                return { 
                    success: false, 
                    error: err instanceof Error ? err.message : 'Failed to clear session'
                };
            }
        }
        return { success: false, error: 'No active session' };
    };

    return {
        messages,
        setMessages,
        sessionId,
        setSessionId,
        isLoadingSession,
        clearSession,
    };
}
