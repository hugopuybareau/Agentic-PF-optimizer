import { Background } from '@/components/Background';
import { ThemeToggle } from '@/components/ThemeToggle';
import { useState, useEffect, memo } from 'react';

const TypewriterText = memo(() => {
    const textKeys = ['they make you win money', 'you follow their lead', 'they know before anyone else'];
    const [currentTextIndex, setCurrentTextIndex] = useState(0);
    const [displayedText, setDisplayedText] = useState('');
    const [isTyping, setIsTyping] = useState(true);
    const [cycleCount, setCycleCount] = useState(0);

    useEffect(() => {
        const currentText = textKeys[currentTextIndex];
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
                
                const nextIndex = (currentTextIndex + 1) % textKeys.length;
                const isCompletingCycle = nextIndex === 0;
                const newCycleCount = isCompletingCycle ? cycleCount + 1 : cycleCount;

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
    }, [currentTextIndex, cycleCount]);

    return (
        <span className="text-muted-foreground">
            {displayedText}
            {isTyping && <span className="animate-pulse">|</span>}
        </span>
    );
});

TypewriterText.displayName = 'TypewriterText';

export default function Landing() {
    return (
        <div className="min-h-screen relative overflow-hidden">
            <Background />
            <ThemeToggle />

            {/* Logo */}
            <div className="fixed top-6 left-6 z-50 flex items-center gap-3">
                <img src="/favicon.ico" alt="silveragents" className="w-6 h-6" />
                <div className="text-nav font-semibold tracking-tight">
                    silver
                    <span className="text-muted-foreground"> agents</span>
                </div>
            </div>

            <main className="relative z-20 min-h-screen flex items-center justify-center px-6">
                <div className="max-w-4xl mx-auto text-center">
                    <div className="animate-fade-in-up">
                        <h1 className="text-hero mb-4 font-medium tracking-tight">
                            agents so good
                            <br />
                            <TypewriterText />
                        </h1>

                        <p className="text-sub mb-12 max-w-lg mx-auto dark:text-white">
                            AI-powered portfolio analysis and market insights for modern investors
                        </p>
                    </div>
                </div>
            </main>
        </div>
    );
}