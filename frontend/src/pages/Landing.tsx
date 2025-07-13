import { Link } from 'react-router-dom'
import { AnimatedBackground } from '@/components/AnimatedBackground'
import { Navigation } from '@/components/Navigation'

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
              <span className="text-muted-foreground">simplified.</span>
            </h1>
            
            {/* Small subheadline */}
            <p className="text-sub mb-12 max-w-lg mx-auto">
              AI-powered portfolio analysis and market insights for modern investors
            </p>

            {/* Bottom-aligned minimal CTAs */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-16">
              <Link
                to="/portfolio"
                className="btn-primary px-6 py-3 rounded-lg text-sm"
              >
                Get Started
              </Link>
              <Link
                to="/chat"
                className="btn-ghost px-6 py-3 rounded-lg text-sm"
              >
                Log in
              </Link>
            </div>
          </div>
        </div>
      </main>

      {/* Minimal feature hints */}
      <section className="relative z-10 py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center animate-fade-in-up">
              <div className="w-12 h-12 bg-primary/10 rounded-lg mx-auto mb-4 flex items-center justify-center">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-nav font-medium mb-2">Portfolio Analysis</h3>
              <p className="text-sub text-xs">Real-time insights and optimization</p>
            </div>
            
            <div className="text-center animate-fade-in-up" style={{animationDelay: '0.2s'}}>
              <div className="w-12 h-12 bg-primary/10 rounded-lg mx-auto mb-4 flex items-center justify-center">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-nav font-medium mb-2">AI Copilot</h3>
              <p className="text-sub text-xs">Intelligent financial guidance</p>
            </div>
            
            <div className="text-center animate-fade-in-up" style={{animationDelay: '0.4s'}}>
              <div className="w-12 h-12 bg-primary/10 rounded-lg mx-auto mb-4 flex items-center justify-center">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5l-5-5h5v-5a4 4 0 00-8 0v5h5l-5 5l-5-5h5V7a9 9 0 0118 0v10z" />
                </svg>
              </div>
              <h3 className="text-nav font-medium mb-2">Smart Alerts</h3>
              <p className="text-sub text-xs">Proactive market notifications</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}