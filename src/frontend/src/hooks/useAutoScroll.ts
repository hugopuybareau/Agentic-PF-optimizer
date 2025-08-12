// frontend/src/hooks/useAutoScroll.ts

import { useEffect, useRef, useState, useCallback } from 'react';

export function useAutoScroll() {
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const messagesContainerRef = useRef<HTMLDivElement>(null);
    const [showScrollButton, setShowScrollButton] = useState(false);
    const [userScrolled, setUserScrolled] = useState(false);
    const scrollHandlerRef = useRef<(() => void) | null>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        setUserScrolled(false);
        setShowScrollButton(false);
    };

    // Auto-scroll when new messages are added (if user hasn't manually scrolled up)
    const autoScrollToBottom = (messages: any[], streamedText: string, isLoadingSession: boolean) => {
        useEffect(() => {
            if (!userScrolled && !isLoadingSession) {
                scrollToBottom();
            }
        }, [messages, streamedText, userScrolled, isLoadingSession]);
    };

    const handleScroll = useCallback(() => {
        const container = messagesContainerRef.current;
        if (!container) return;
        
        const { scrollTop, scrollHeight, clientHeight } = container;
        const isAtBottom = scrollHeight - scrollTop <= clientHeight + 50;
        
        if (!isAtBottom) {
            setUserScrolled(true);
            setShowScrollButton(true);
        } else {
            setUserScrolled(false);
            setShowScrollButton(false);
        }
    }, []);

    // Handle scroll detection to show/hide scroll button
    useEffect(() => {
        const container = messagesContainerRef.current;
        if (!container) return;

        scrollHandlerRef.current = handleScroll;
        container.addEventListener('scroll', handleScroll, { passive: true });
        
        // Initial check
        setTimeout(() => handleScroll(), 100);
        
        return () => {
            if (scrollHandlerRef.current) {
                container.removeEventListener('scroll', scrollHandlerRef.current);
            }
        };
    }, []);

    const resetScrollState = () => {
        setUserScrolled(false);
        setShowScrollButton(false);
    };

    return {
        messagesEndRef,
        messagesContainerRef,
        showScrollButton,
        userScrolled,
        scrollToBottom,
        autoScrollToBottom,
        resetScrollState,
    };
}
