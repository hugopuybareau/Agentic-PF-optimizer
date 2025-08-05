import { useTheme } from '@/hooks/use-theme';

// Generate stars once outside component to prevent reset on theme change
const generateStars = () => {
    const stars = [];
    for (let i = 0; i < 50; i++) {
        stars.push({
            id: i,
            left: Math.random() * 100,
            top: Math.random() * 100,
            size: Math.random() * 0.8 + 0.3,
            animationDelay: Math.random() * 15,
            rotationDelay: Math.random() * 10,
            floatDelay: Math.random() * 8,
            rotationSpeed: Math.random() * 6 + 3,
            moveSpeed: Math.random() * 20 + 25,
            moveDirection: Math.random() < 0.33 ? 'horizontal' : Math.random() < 0.66 ? 'vertical' : 'diagonal',
        });
    }
    return stars;
};

const stars = generateStars();

export function Background() {
    const { theme } = useTheme();
    
    const getBackgroundImage = () => {
        return theme === 'dark' 
            ? '/images/dark_one_reduced_left.png'
            : '/images/white_one_reduced_left.png';
    };

    const imagePath = getBackgroundImage();

    return (
        <div className="fixed inset-0 z-0 pointer-events-none w-full h-full overflow-hidden">
            {/* Background image - hidden on mobile */}
            <div 
                className="hidden md:block w-full h-full bg-left bg-cover bg-no-repeat"
                style={{
                    backgroundImage: `url(${imagePath})`,
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
                        className={`absolute ${star.id >= 20 ? 'hidden md:block' : ''}`}
                        style={{
                            left: `${star.left}%`,
                            top: `${star.top}%`,
                            fontSize: `${star.size}rem`,
                            color: theme === 'dark' ? 'rgba(255, 255, 255, 0.4)' : 'rgba(0, 0, 0, 0.4)',
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
        </div>
    );
}