// frontend/src/pages/Features.tsx

import { useTranslation } from 'react-i18next';
import { Navigation } from '@/components/Navigation';
import { useFeatures } from './featuresList';

export default function Features() {
    const { t } = useTranslation();
    const features = useFeatures();

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
