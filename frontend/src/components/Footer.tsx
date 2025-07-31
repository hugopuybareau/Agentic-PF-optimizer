import { Link } from 'react-router-dom'

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-background border-t border-border">
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          {/* Logo */}
          <div>
            <span className="text-nav font-semibold tracking-tight">
              platine<span className="text-muted-foreground">.ai</span>
            </span>
          </div>

          {/* Links */}
          <div className="flex items-center space-x-6">
            <Link to="/features" className="text-sub hover:text-primary transition-colors text-sm">
              Features
            </Link>
            <Link to="/contact" className="text-sub hover:text-primary transition-colors text-sm">
              Contact
            </Link>
            <a 
              href="https://github.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-sub hover:text-primary transition-colors text-sm"
            >
              GitHub
            </a>
            <a 
              href="/privacy" 
              className="text-sub hover:text-primary transition-colors text-sm"
            >
              Privacy
            </a>
            <a 
              href="/terms" 
              className="text-sub hover:text-primary transition-colors text-sm"
            >
              Terms
            </a>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t border-border text-center">
          <p className="text-sub text-sm">
            © {currentYear} platine.ai. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}