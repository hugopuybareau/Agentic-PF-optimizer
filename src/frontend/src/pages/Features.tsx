// frontend/src/pages/Features.tsx

import { useTranslation } from 'react-i18next';
import { Navigation } from '@/components/Navigation';

export default function Features() {
    const { t } = useTranslation();
    
    const features = [
        {
            title: t('features.portfolioAnalysis.title'),
            description: t('features.portfolioAnalysis.description'),
            icon: (
                <svg
                    className="w-8 h-8"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                </svg>
            ),
        },
        {
            title: t('features.aiFinancialCopilot.title'),
            description: t('features.aiFinancialCopilot.description'),
            icon: (
                <svg
                    className="w-8 h-8"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                </svg>
            ),
        },
        {
            title: t('features.smartAlerts.title'),
            description: t('features.smartAlerts.description'),
            icon: (
                <svg
                    className="w-8 h-8"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15 17h5l-5 5l-5-5h5v-5a4 4 0 00-8 0v5h5l-5 5l-5-5h5V7a9 9 0 0118 0v10z"
                    />
                </svg>
            ),
        },
        {
            title: t('features.riskManagement.title'),
            description: t('features.riskManagement.description'),
            icon: (
                <svg
                    className="w-8 h-8"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                    />
                </svg>
            ),
        },
        {
            title: t('features.marketIntelligence.title'),
            description: t('features.marketIntelligence.description'),
            icon: (
                <svg
                    className="w-8 h-8"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                    />
                </svg>
            ),
        },
        {
            title: t('features.portfolioOptimization.title'),
            description: t('features.portfolioOptimization.description'),
            icon: (
                <svg
                    className="w-8 h-8"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"
                    />
                </svg>
            ),
        },
    ];

    return (
        <div className="min-h-screen bg-background">
            <Navigation />

            <main className="pt-20 px-6 pb-12">
                <div className="max-w-6xl mx-auto">
                    {/* Header */}
                    <div className="text-center mb-16">
                        <h1 className="text-hero mb-4">
                            {t('features.intelligentFinancialTools')}
                        </h1>
                        <p className="text-sub max-w-2xl mx-auto">
                            {t('features.silverAgentsDescription')}
                        </p>
                    </div>

                    {/* Features Grid */}
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {features.map((feature, index) => (
                            <div
                                key={feature.title}
                                className="card-silver p-8 rounded-lg hover:shadow-elevation transition-all duration-300 animate-fade-in-up"
                                style={{ animationDelay: `${index * 0.1}s` }}
                            >
                                <div className="mb-6">
                                    <div className="w-16 h-16 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                                        {feature.icon}
                                    </div>
                                    <h3 className="text-nav font-semibold mb-3">
                                        {feature.title}
                                    </h3>
                                    <p className="text-sub leading-relaxed">
                                        {feature.description}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* CTA Section */}
                    <div className="mt-20 text-center">
                        <div className="card-silver p-12 rounded-lg">
                            <h2 className="text-hero mb-4">
                                {t('features.readyToGetStarted')}
                            </h2>
                            <p className="text-sub mb-8 max-w-md mx-auto">
                                {t('features.joinThousandsOfInvestors')}
                            </p>
                            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                                <a
                                    href="/portfolio"
                                    className="btn-primary px-8 py-3 rounded-lg text-nav"
                                >
                                    {t('features.startFreeTrial')}
                                </a>
                                <a
                                    href="/chat"
                                    className="btn-ghost px-8 py-3 rounded-lg text-nav"
                                >
                                    {t('features.talkTosilverAgent')}
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
