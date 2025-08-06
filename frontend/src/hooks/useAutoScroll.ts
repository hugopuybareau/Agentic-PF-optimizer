// frontend/src/hooks/useAutoScroll.ts

import { useEffect, useRef, useState } from 'react';

export function useAutoScroll() {
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const messagesContainerRef = useRef<HTMLDivElement>(null);
    const [showScrollButton, setShowScrollButton] = useState(false);
    const [userScrolled, setUserScrolled] = useState(false);

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

    // Handle scroll detection to show/hide scroll button
    useEffect(() => {
        const container = messagesContainerRef.current;
        if (!container) return;

        const handleScroll = () => {
            const { scrollTop, scrollHeight, clientHeight } = container;
            const isAtBottom = scrollHeight - scrollTop <= clientHeight + 100; // Increased threshold to 100px
            
            // Debug logging
            console.log('Scroll Debug:', {
                scrollTop,
                scrollHeight,
                clientHeight,
                isAtBottom,
                userScrolled,
                showScrollButton
            });
            
            if (!isAtBottom && !userScrolled) {
                setUserScrolled(true);
                setShowScrollButton(true);
            } else if (isAtBottom && userScrolled) {
                setUserScrolled(false);
                setShowScrollButton(false);
            }
        };

        container.addEventListener('scroll', handleScroll);
        
        // Initial check
        handleScroll();
        
        return () => container.removeEventListener('scroll', handleScroll);
    }, [userScrolled]);

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
