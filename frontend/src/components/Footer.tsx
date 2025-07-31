// frontend/src/components/Footer.tsx

import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export function Footer() {
    const { t } = useTranslation();
    const currentYear = new Date().getFullYear();

    return (
        <footer className="bg-background border-t border-border">
            <div className="max-w-6xl mx-auto px-6 py-8">
                <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
                    {/* Logo */}
                    <div>
                        <span className="text-nav font-semibold tracking-tight">
                            silver
                            <span className="text-muted-foreground">
                                agents
                            </span>
                        </span>
                    </div>

                    {/* Links */}
                    <div className="flex items-center space-x-6">
                        <Link
                            to="/features"
                            className="text-sub hover:text-primary transition-colors text-sm"
                        >
                            {t('footer.features')}
                        </Link>
                        <a
                            href="https://github.com"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sub hover:text-primary transition-colors text-sm"
                        >
                            {t('footer.github')}
                        </a>
                        <a
                            href="/privacy"
                            className="text-sub hover:text-primary transition-colors text-sm"
                        >
                            {t('footer.privacy')}
                        </a>
                        <a
                            href="/terms"
                            className="text-sub hover:text-primary transition-colors text-sm"
                        >
                            {t('footer.terms')}
                        </a>
                    </div>
                </div>

                <div className="mt-6 pt-6 border-t border-border text-center">
                    <p className="text-sub text-sm">
                        {t('footer.copyright', { currentYear })}
                    </p>
                </div>
            </div>
        </footer>
    );
}
