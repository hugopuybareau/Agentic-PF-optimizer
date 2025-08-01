// frontend/src/pages/Landing.tsx

import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Navigation } from '@/components/Navigation';
import { SplitBackground } from '@/components/SplitBackground';
import { useState, useEffect, useMemo, memo } from 'react';

// Memoized typewriter component to prevent re-renders of parent
const TypewriterText = memo(() => {
    const { t } = useTranslation();
    const textKeys = ['theyMakeYouWinMoney', 'youFollowTheirLead', 'theyKnowBeforeAnyoneElse'];
    const [currentTextIndex, setCurrentTextIndex] = useState(0);
    const [displayedText, setDisplayedText] = useState('');
    const [isTyping, setIsTyping] = useState(true);
    const [cycleCount, setCycleCount] = useState(0);

    useEffect(() => {
        const currentText = t(`landing.${textKeys[currentTextIndex]}`);
        let charIndex = 0;
        setDisplayedText('');
        setIsTyping(true);

        const typeInterval = setInterval(() => {
            if (charIndex < currentText.length) {
                setDisplayedText(currentText.slice(0, charIndex + 1));
                charIndex++;
            } else {
                setIsTyping(false);
                clearInterval(typeInterval);
                
                // Calculate delay based on cycle completion
                const nextIndex = (currentTextIndex + 1) % textKeys.length;
                const isCompletingCycle = nextIndex === 0;
                const newCycleCount = isCompletingCycle ? cycleCount + 1 : cycleCount;

                // 30 second delay every 3 cycles, otherwise 2.5 seconds
                const delay = (isCompletingCycle && newCycleCount % 3 === 0) ? 30000 : 2500;
                
                setTimeout(() => {
                    setCurrentTextIndex(nextIndex);
                    if (isCompletingCycle) {
                        setCycleCount(newCycleCount);
                    }
                }, delay);
            }
        }, 80);

        return () => clearInterval(typeInterval);
    }, [currentTextIndex, cycleCount, t]);

    return (
        <span className="text-muted-foreground">
            {displayedText}
            {isTyping && <span className="animate-pulse">|</span>}
        </span>
    );
});

TypewriterText.displayName = 'TypewriterText';

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
                            <TypewriterText />
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
