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
            className="absolute bottom-20 left-1/2 transform -translate-x-1/2 z-50 bg-background border border-border text-foreground p-2 rounded-full shadow-lg hover:shadow-xl hover:bg-muted transition-all duration-200 flex items-center justify-center"
            title={t('chat.scrollToBottom', 'Scroll to bottom')}
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
                    d="M19 14l-7 7m0 0l-7-7m7 7V3"
                />
            </svg>
        </button>
    );
}
