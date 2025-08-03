// frontend/src/components/ShootingStar.tsx

import { ReactNode } from 'react';

interface ShootingStarInputProps {
    children: ReactNode;
    className?: string;
}

export const ShootingStarInput: React.FC<ShootingStarInputProps> = ({
    children,
    className = '',
}) => {
    return (
        <div className={`relative ${className}`}>
            {/* Main input container */}
            <div className="relative z-10">{children}</div>

            {/* Shooting star animation container */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-lg">
                {/* The shooting star */}
                <div className="shooting-star">
                    <div className="star-core"></div>
                    <div className="star-trail"></div>
                </div>
            </div>

            <style jsx>{`
                .shooting-star {
                    position: absolute;
                    width: 12px;
                    height: 12px;
                    animation: shootingStarPath 8s linear infinite;
                }

                .star-core {
                    position: absolute;
                    width: 4px;
                    height: 4px;
                    background: var(--star-color, #c0c0c0);
                    border-radius: 50%;
                    box-shadow: 0 0 6px var(--star-color, #c0c0c0),
                        0 0 12px var(--star-color, #c0c0c0),
                        0 0 18px var(--star-color, #c0c0c0);
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                }

                .star-trail {
                    position: absolute;
                    width: 20px;
                    height: 2px;
                    background: linear-gradient(
                        90deg,
                        transparent 0%,
                        var(--star-color, #c0c0c0) 50%,
                        transparent 100%
                    );
                    top: 50%;
                    left: -8px;
                    transform: translateY(-50%);
                    opacity: 0.6;
                }

                @keyframes shootingStarPath {
                    0% {
                        /* Top-left corner */
                        left: 0%;
                        top: 0%;
                        transform: rotate(45deg);
                    }

                    25% {
                        /* Top-right corner */
                        left: calc(100% - 12px);
                        top: 0%;
                        transform: rotate(135deg);
                    }

                    50% {
                        /* Bottom-right corner */
                        left: calc(100% - 12px);
                        top: calc(100% - 12px);
                        transform: rotate(225deg);
                    }

                    75% {
                        /* Bottom-left corner */
                        left: 0%;
                        top: calc(100% - 12px);
                        transform: rotate(315deg);
                    }

                    100% {
                        /* Back to top-left corner */
                        left: 0%;
                        top: 0%;
                        transform: rotate(405deg);
                    }
                }

                /* Light mode (default) */
                :global(.shooting-star) {
                    --star-color: #c0c0c0;
                }

                /* Dark mode - lighter silver */
                :global(.dark .shooting-star) {
                    --star-color: #e5e5e5;
                }
            `}</style>
        </div>
    );
};
