// src/components/LoginModal.tsx

import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { X, Mail, Lock, User, UserPlus, LogIn, Eye, EyeOff } from 'lucide-react';
import { Dialog, DialogContent, DialogOverlay } from '@/components/ui/dialog';
import './LoginModal.css';

interface LoginModalProps {
    isOpen: boolean;
    onClose: () => void;
    mode: 'login' | 'register';
    form: {
        email: string;
        password: string;
        username?: string;
        full_name?: string;
    };
    loading: boolean;
    error?: string | null;
    success?: string | null;
    onInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onSubmit: (e: React.FormEvent) => void;
    onSwitchMode: () => void;
}

export default function LoginModal({
    isOpen,
    onClose,
    mode,
    form,
    loading,
    error,
    success,
    onInputChange,
    onSubmit,
    onSwitchMode,
}: LoginModalProps) {
    const { t } = useTranslation();
    const [showPassword, setShowPassword] = React.useState(false);

    // Reset password visibility when switching modes
    useEffect(() => {
        setShowPassword(false);
    }, [mode]);

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogOverlay className="login-modal-overlay bg-black/60 backdrop-blur-sm" />
            <DialogContent className="max-w-md w-full mx-4 p-0 bg-transparent border-0 shadow-none">
                <div className="login-modal-content relative bg-background/95 backdrop-blur-xl border border-border/50 rounded-2xl shadow-2xl overflow-hidden">
                    {/* Background gradient overlay */}
                    <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5" />
                    
                    {/* Floating particles */}
                    <div className="login-modal-particles" />
                    
                    {/* Close button */}
                    <button
                        className="absolute top-4 right-4 z-10 p-2 rounded-full hover:bg-accent/80 transition-all duration-200 text-muted-foreground hover:text-foreground group"
                        onClick={onClose}
                        type="button"
                        aria-label={t('close')}
                    >
                        <X className="h-4 w-4 group-hover:rotate-90 transition-transform duration-200" />
                    </button>

                    <div className="relative z-10 p-8">
                        {/* Header with icon */}
                        <div className="text-center mb-8">
                            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 border border-primary/20 mb-4">
                                {mode === 'login' ? (
                                    <LogIn className="h-7 w-7 text-primary" />
                                ) : (
                                    <UserPlus className="h-7 w-7 text-primary" />
                                )}
                            </div>
                            <h2 className="text-2xl font-bold text-foreground mb-2">
                                {mode === 'login' ? t('login.welcomeBack') : t('login.createAccount')}
                            </h2>
                            <p className="text-muted-foreground text-sm">
                                {mode === 'login' 
                                    ? t('login.signInToContinue')
                                    : t('login.joinUsToday')
                                }
                            </p>
                        </div>

                        {/* Mode toggle */}
                        <div className="flex p-1 bg-accent/30 rounded-lg mb-6 border border-border/50">
                            <button
                                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all duration-200 ${
                                    mode === 'login'
                                        ? 'bg-background text-foreground shadow-sm border border-border/50'
                                        : 'text-muted-foreground hover:text-foreground'
                                }`}
                                onClick={mode === 'login' ? undefined : onSwitchMode}
                                disabled={mode === 'login'}
                                type="button"
                            >
                                {t('login.logIn')}
                            </button>
                            <button
                                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all duration-200 ${
                                    mode === 'register'
                                        ? 'bg-background text-foreground shadow-sm border border-border/50'
                                        : 'text-muted-foreground hover:text-foreground'
                                }`}
                                onClick={mode === 'register' ? undefined : onSwitchMode}
                                disabled={mode === 'register'}
                                type="button"
                            >
                                {t('login.register')}
                            </button>
                        </div>

                        {/* Error/Success messages */}
                        {error && (
                            <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm animate-in slide-in-from-top-2 duration-300">
                                {error}
                            </div>
                        )}
                        {success && (
                            <div className="mb-4 p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-green-600 text-sm animate-in slide-in-from-top-2 duration-300">
                                {success}
                            </div>
                        )}

                        {/* Form */}
                        <form className="space-y-4" onSubmit={onSubmit}>
                            {/* Email field */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-foreground" htmlFor="email">
                                    {t('login.email')}
                                </label>
                                <div className="form-field-focus relative">
                                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                    <input
                                        name="email"
                                        type="email"
                                        autoComplete="email"
                                        value={form.email}
                                        onChange={onInputChange}
                                        className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-background/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200 text-foreground placeholder:text-muted-foreground"
                                        placeholder={t('login.emailPlaceholder')}
                                        required
                                    />
                                </div>
                            </div>

                            {/* Register-only fields */}
                            {mode === 'register' && (
                                <>
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-foreground" htmlFor="username">
                                            {t('login.username')}
                                        </label>
                                        <div className="form-field-focus relative">
                                            <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                            <input
                                                name="username"
                                                type="text"
                                                value={form.username || ''}
                                                onChange={onInputChange}
                                                className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-background/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200 text-foreground placeholder:text-muted-foreground"
                                                placeholder={t('login.usernamePlaceholder')}
                                                required
                                            />
                                        </div>
                                    </div>
                                    
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-foreground" htmlFor="full_name">
                                            {t('login.fullName')} <span className="text-muted-foreground text-xs">{t('common.optional')}</span>
                                        </label>
                                        <div className="form-field-focus relative">
                                            <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                            <input
                                                name="full_name"
                                                type="text"
                                                value={form.full_name || ''}
                                                onChange={onInputChange}
                                                className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-background/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200 text-foreground placeholder:text-muted-foreground"
                                                placeholder={t('login.fullNamePlaceholder')}
                                            />
                                        </div>
                                    </div>
                                </>
                            )}

                            {/* Password field */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-foreground" htmlFor="password">
                                    {t('login.password')}
                                </label>
                                <div className="form-field-focus relative">
                                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                    <input
                                        name="password"
                                        type={showPassword ? 'text' : 'password'}
                                        autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                                        value={form.password}
                                        onChange={onInputChange}
                                        className="w-full pl-10 pr-12 py-3 border border-border rounded-lg bg-background/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200 text-foreground placeholder:text-muted-foreground"
                                        placeholder={t('login.passwordPlaceholder')}
                                        required
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-muted-foreground hover:text-foreground transition-colors"
                                    >
                                        {showPassword ? (
                                            <EyeOff className="h-4 w-4" />
                                        ) : (
                                            <Eye className="h-4 w-4" />
                                        )}
                                    </button>
                                </div>
                            </div>

                            {/* Submit button */}
                            <button
                                className="w-full mt-6 bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 text-primary-foreground font-medium py-3 rounded-lg transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:transform-none disabled:cursor-not-allowed shadow-lg shadow-primary/25"
                                type="submit"
                                disabled={loading}
                            >
                                {loading ? (
                                    <div className="flex items-center justify-center space-x-2">
                                        <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                                        <span>{t('common.processing')}</span>
                                    </div>
                                ) : (
                                    <div className="flex items-center justify-center space-x-2">
                                        {mode === 'login' ? (
                                            <LogIn className="h-4 w-4" />
                                        ) : (
                                            <UserPlus className="h-4 w-4" />
                                        )}
                                        <span>
                                            {mode === 'login' ? t('login.logIn') : t('login.register')}
                                        </span>
                                    </div>
                                )}
                            </button>
                        </form>

                        {/* Footer */}
                        <div className="mt-6 text-center">
                            <p className="text-sm text-muted-foreground">
                                {mode === 'login' ? t('login.noAccount?') : t('login.account?')}{' '}
                                <button
                                    className="text-primary hover:text-primary/80 font-medium underline-offset-4 hover:underline transition-all duration-200"
                                    type="button"
                                    onClick={onSwitchMode}
                                >
                                    {mode === 'login' ? t('login.register') : t('login.logIn')}
                                </button>
                            </p>
                        </div>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}