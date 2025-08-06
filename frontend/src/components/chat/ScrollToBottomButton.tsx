// frontend/src/components/chat/ScrollToBottomButton.tsx

import { useTranslation } from 'react-i18next';

interface ScrollToBottomButtonProps {
    show: boolean;
    onClick: () => void;
}

export function ScrollToBottomButton({ show, onClick }: ScrollToBottomButtonProps) {
    const { t } = useTranslation();

    if (!show) return null;

    return (
        <button
            onClick={onClick}
            className="absolute bottom-20 right-4 bg-primary text-primary-foreground p-3 rounded-full shadow-xl hover:bg-primary/90 transition-all duration-200 animate-pulse z-20 border-2 border-background"
            title={t('chat.scrollToBottom', 'Scroll to bottom')}
        >
            <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
            >
                <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 14l-7 7m0 0l-7-7m7 7V3"
                />
            </svg>
        </button>
    );
}
