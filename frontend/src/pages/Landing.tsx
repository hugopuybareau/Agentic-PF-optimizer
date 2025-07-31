// frontend/src/pages/Landing.tsx

import { Link } from 'react-router-dom';
import { AnimatedBackground } from '@/components/AnimatedBackground';
import { Navigation } from '@/components/Navigation';

export default function Landing() {
    return (
        <div className="min-h-screen relative overflow-hidden">
            <AnimatedBackground />
            <Navigation />

            {/* Hero Section */}
            <main className="relative z-10 min-h-screen flex items-center justify-center px-6">
                <div className="max-w-4xl mx-auto text-center">
                    <div className="animate-fade-in-up">
                        {/* Scarce, minimalist headline */}
                        <h1 className="text-hero mb-4 font-medium tracking-tight">
                            Financial intelligence,
                            <br />
                            <span className="text-muted-foreground">
                                simplified.
                            </span>
                        </h1>

                        {/* Small subheadline */}
                        <p className="text-sub mb-12 max-w-lg mx-auto">
                            AI-powered portfolio analysis and market insights
                            for modern investors
                        </p>

                        {/* Bottom-aligned minimal CTA */}
                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-16">
                            <Link
                                to="/portfolio"
                                className="btn-primary px-6 py-3 rounded-lg text-sm"
                            >
                                Get Started
                            </Link>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
