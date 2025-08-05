// frontend/src/pages/Landing.tsx

import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Navigation } from '@/components/Navigation';
import { Background } from '@/components/Background';
import { useState, useEffect, memo } from 'react';
import { Linkedin } from 'lucide-react';

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
            {isTyping && <span className="animate-pulse"></span>}
        </span>
    );
});

TypewriterText.displayName = 'TypewriterText';

export default function Landing() {
    const { t } = useTranslation();

    return (
        <div className="min-h-screen relative overflow-hidden">
            <Background />
            <Navigation />
            
            {/* Social Links Navigation */}
            <nav className="fixed top-16 right-6 z-50 flex flex-col gap-2" aria-label="Social media links">
                <a
                    href="https://linkedin.com/company/silveragents"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 rounded-lg hover:bg-accent transition-smooth"
                    aria-label="Visit Silver Agents on LinkedIn"
                >
                    <Linkedin className="w-4 h-4 text-[#0A66C2]" />
                </a>
                
                <a
                    href="https://discord.gg/VfUzKj9zKb"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 rounded-lg hover:bg-accent transition-smooth"
                    aria-label="Join Silver Agents Discord"
                >
                    <svg
                        className="w-4 h-4"
                        fill="#5865F2"
                        viewBox="0 0 24 24"
                    >
                        <path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419-.0189 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1568 2.4189Z"/>
                    </svg>
                </a>
            </nav>


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
                        <h2 className="text-sub mb-12 max-w-lg mx-auto dark:text-white">
                            {t('landing.aiPoweredDescription')}
                        </h2>

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
