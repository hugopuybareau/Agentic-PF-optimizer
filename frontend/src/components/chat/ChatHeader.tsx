import { useTranslation } from 'react-i18next';

interface ChatHeaderProps {
    error: string | null;
}

export function ChatHeader({ error }: ChatHeaderProps) {
    const { t } = useTranslation();

    return (
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
            </div>
            {error && (
                <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-lg text-red-700 text-sm">
                    {error}
                </div>
            )}
        </div>
    );
}
