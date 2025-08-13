import { useTranslation } from 'react-i18next';

interface QuickAction {
    label: string;
    action: () => void;
}

interface QuickActionsProps {
    actions: QuickAction[];
    sessionId: string | null;
    onClearSession: () => void;
}

export function QuickActions({ actions, sessionId, onClearSession }: QuickActionsProps) {
    const { t } = useTranslation();

    return (
        <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-muted-foreground">
                    {t('chat.quickActions.title', 'Quick Actions')}
                </span>
                {sessionId && (
                    <button
                        onClick={onClearSession}
                        className="btn-ghost px-3 py-1 text-xs rounded-lg hover:bg-destructive/10 hover:text-destructive transition-colors"
                        title={t('chat.clearSessionTooltip')}
                    >
                        {t('chat.clearSession')}
                    </button>
                )}
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {actions.map((action) => (
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
    );
}
