// frontend/src/components/SplitBackground.tsx

import { useTheme } from '@/hooks/use-theme';
import { useEffect, useState, useMemo } from 'react';

export function SplitBackground() {
    const { theme } = useTheme();
    const [currentTheme, setCurrentTheme] = useState(theme);
    
    // Update current theme when theme changes
    useEffect(() => {
        setCurrentTheme(theme);
    }, [theme]);
    
    // Determine which image to use based on theme
    const getBackgroundImage = () => {
        // Default to light mode image
        let imagePath = '/images/background-light.png';
        
        if (currentTheme === 'dark') {
            imagePath = '/images/background-dark.png';
        } else if (currentTheme === 'light') {
            imagePath = '/images/background-light.png';
        } else if (currentTheme === 'system') {
            // System theme - check if user prefers dark mode
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            imagePath = isDark ? '/images/background-dark.png' : '/images/background-light.png';
        }
        
        return imagePath;
    };

    const imagePath = getBackgroundImage();
    
    // Debug logging
    console.log('SplitBackground - Current theme:', currentTheme);
    console.log('SplitBackground - Image path:', imagePath);

    // Memoize star generation to prevent recreation on every render
    const stars = useMemo(() => {
        const generatedStars = [];
        for (let i = 0; i < 50; i++) {
            generatedStars.push({
                id: i,
                left: Math.random() * 100,
                top: Math.random() * 100,
                size: Math.random() * 0.8 + 0.3, // 0.3 to 1.1
                animationDelay: Math.random() * 15, // 0 to 15 seconds
                rotationDelay: Math.random() * 10, // 0 to 10 seconds
                floatDelay: Math.random() * 8, // 0 to 8 seconds
                rotationSpeed: Math.random() * 6 + 3, // 3 to 9 seconds
                moveSpeed: Math.random() * 20 + 25, // 25 to 45 seconds
                moveDirection: Math.random() < 0.33 ? 'horizontal' : Math.random() < 0.66 ? 'vertical' : 'diagonal',
            });
        }
        return generatedStars;
    }, []); // Empty dependency array - only generate once

    return (
        <div className="fixed inset-0 z-0 pointer-events-none flex w-full h-full overflow-hidden">
            {/* Left half - mirrored image */}
            <div 
                className="w-1/2 h-full bg-center bg-no-repeat scale-x-[-1]"
                style={{
                    backgroundImage: `url(${imagePath})`,
                    backgroundSize: '200% 100%',
                    backgroundPosition: 'left center',
                }}
            />
            
            {/* Right half - mirrored image */}
            <div 
                className="w-1/2 h-full bg-center bg-no-repeat scale-x-[-1]"
                style={{
                    backgroundImage: `url(${imagePath})`,
                    backgroundSize: '200% 100%',
                    backgroundPosition: 'right center',
                }}
            />
            
            {/* Animated Star Particles */}
            <div className="absolute inset-0 pointer-events-none">
                <style>{`
                    @keyframes moveHorizontal {
                        0% { transform: translateX(-10vw); }
                        100% { transform: translateX(110vw); }
                    }
                    @keyframes moveVertical {
                        0% { transform: translateY(-10vh); }
                        100% { transform: translateY(110vh); }
                    }
                    @keyframes moveDiagonal {
                        0% { transform: translate(-10vw, -10vh); }
                        100% { transform: translate(110vw, 110vh); }
                    }
                `}</style>
                {stars.map((star) => (
                    <div
                        key={star.id}
                        className="absolute"
                        style={{
                            left: `${star.left}%`,
                            top: `${star.top}%`,
                            fontSize: `${star.size}rem`,
                            color: currentTheme === 'dark' ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.12)',
                            animation: `${
                                star.moveDirection === 'horizontal' 
                                    ? 'moveHorizontal' 
                                    : star.moveDirection === 'vertical'
                                    ? 'moveVertical'
                                    : 'moveDiagonal'
                            } ${star.moveSpeed}s linear infinite`,
                            animationDelay: `${star.animationDelay}s`,
                        }}
                    >
                        <div
                            className="animate-spin"
                            style={{
                                animationDuration: `${star.rotationSpeed}s`,
                                animationDelay: `${star.rotationDelay}s`,
                                animationIterationCount: 'infinite',
                                animationTimingFunction: 'linear',
                            }}
                        >
                            <div
                                className="animate-pulse"
                                style={{
                                    animationDuration: '3s',
                                    animationDelay: `${star.floatDelay}s`,
                                }}
                            >
                                ✦
                            </div>
                        </div>
                    </div>
                ))}
            </div>
            
            {/* Optional: Subtle center line */}
            <div className="absolute left-1/2 top-0 w-0.5 h-full bg-gradient-to-b from-transparent via-black/5 to-transparent dark:via-white/5 transform -translate-x-1/2 pointer-events-none" />
        </div>
    );
}