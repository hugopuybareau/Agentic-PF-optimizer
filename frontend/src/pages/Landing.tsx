// frontend/src/pages/Landing.tsx

import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Navigation } from '@/components/Navigation';
import { SplitBackground } from '@/components/SplitBackground';

export default function Landing() {
    const { t } = useTranslation();

    return (
        <div className="min-h-screen relative overflow-hidden">
            <SplitBackground />
            <Navigation />

            {/* Hero Section */}
            <main className="relative z-20 min-h-screen flex items-center justify-center px-6">
                <div className="max-w-4xl mx-auto text-center">
                    <div className="animate-fade-in-up">
                        {/* Scarce, minimalist headline */}
                        <h1 className="text-hero mb-4 font-medium tracking-tight">
                            {t('landing.agentsSoGood')}
                            <br />
                            <span className="text-muted-foreground">
                                {t('landing.theyMakeYouWinMoney')}
                            </span>
                        </h1>

                        {/* Small subheadline */}
                        <p className="text-sub mb-12 max-w-lg mx-auto">
                            {t('landing.aiPoweredDescription')}
                        </p>

                        {/* Bottom-aligned minimal CTA */}
                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-16">
                            <Link
                                to="/chat"
                                className="btn-primary px-6 py-3 rounded-lg text-sm"
                            >
                                {t('landing.getStarted')}
                            </Link>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
