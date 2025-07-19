// src/components/LoginForm.tsx

import React from 'react';
import { useTranslation } from 'react-i18next';
import { X } from 'lucide-react';

interface LoginFormProps {
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
    onClose: () => void;
}

export default function LoginForm({
    mode,
    form,
    loading,
    error,
    success,
    onInputChange,
    onSubmit,
    onSwitchMode,
    onClose,
}: LoginFormProps) {
    const { t } = useTranslation();

    return (
        <div className="relative max-w-md w-full bg-card shadow-lg rounded-xl p-8">
            {/* X Close button */}
            <button
                className="absolute top-4 right-4 text-zinc-400 hover:text-zinc-700 transition-colors"
                onClick={onClose}
                type="button"
                aria-label={t('close')}
            >
                <X className="h-6 w-6" />
            </button>

            <div className="mb-6 flex justify-center">
                <button
                    className={`w-1/2 px-3 py-2 font-semibold ${
                        mode === 'login'
                            ? 'text-primary border-b-2 border-primary'
                            : 'text-muted-foreground'
                    }`}
                    onClick={mode === 'login' ? undefined : onSwitchMode}
                    disabled={mode === 'login'}
                    type="button"
                >
                    {t('login.logIn')}
                </button>
                <button
                    className={`w-1/2 px-3 py-2 font-semibold ${
                        mode === 'register'
                            ? 'text-primary border-b-2 border-primary'
                            : 'text-muted-foreground'
                    }`}
                    onClick={mode === 'register' ? undefined : onSwitchMode}
                    disabled={mode === 'register'}
                    type="button"
                >
                    {t('login.register')}
                </button>
            </div>
            {error && (
                <div className="mb-4 p-3 rounded bg-red-100 text-red-700 border border-red-200 text-sm">
                    {error}
                </div>
            )}
            {success && (
                <div className="mb-4 p-3 rounded bg-green-100 text-green-700 border border-green-200 text-sm">
                    {success}
                </div>
            )}
            <form className="space-y-4" onSubmit={onSubmit}>
                <div>
                    <label
                        className="block mb-1 text-sm font-medium"
                        htmlFor="email"
                    >
                        {t('login.email')} <span className="text-red-500">*</span>
                    </label>
                    <input
                        name="email"
                        type="email"
                        autoComplete="email"
                        value={form.email}
                        onChange={onInputChange}
                        className="w-full px-3 py-2 border rounded focus:outline-none"
                        placeholder={t('login.emailPlaceholder')}
                        required
                    />
                </div>
                {mode === 'register' && (
                    <>
                        <div>
                            <label
                                className="block mb-1 text-sm font-medium"
                                htmlFor="username"
                            >
                                {t('login.username')} <span className="text-red-500">*</span>
                            </label>
                            <input
                                name="username"
                                type="text"
                                value={form.username}
                                onChange={onInputChange}
                                className="w-full px-3 py-2 border rounded focus:outline-none"
                                placeholder={t('login.usernamePlaceholder')}
                                required
                            />
                        </div>
                        <div>
                            <label
                                className="block mb-1 text-sm font-medium"
                                htmlFor="full_name"
                            >
                                {t('login.fullName')} {/* no star, optional */}
                            </label>
                            <input
                                name="full_name"
                                type="text"
                                value={form.full_name || ''}
                                onChange={onInputChange}
                                className="w-full px-3 py-2 border rounded focus:outline-none"
                                placeholder={t('login.fullNamePlaceholder')}
                            />
                        </div>
                    </>
                )}
                <div>
                    <label
                        className="block mb-1 text-sm font-medium"
                        htmlFor="password"
                    >
                        {t('login.password')} <span className="text-red-500">*</span>
                    </label>
                    <input
                        name="password"
                        type="password"
                        autoComplete={
                            mode === 'login'
                                ? 'current-password'
                                : 'new-password'
                        }
                        value={form.password}
                        onChange={onInputChange}
                        className="w-full px-3 py-2 border rounded focus:outline-none"
                        placeholder={t('login.passwordPlaceholder')}
                        required
                    />
                </div>
                <button
                    className="w-full mt-2 bg-primary text-white font-semibold py-2 rounded disabled:opacity-60"
                    type="submit"
                    disabled={loading}
                >
                    {loading
                        ? '...'
                        : mode === 'login'
                        ? t('login.logIn')
                        : t('login.register')}
                </button>
            </form>
            <div className="mt-4 text-center">
                <span className="text-sm text-muted-foreground">
                    {mode === 'login' ? t('login.noAccount?') : t('login.account?')}{' '}
                    <button
                        className="text-primary underline ml-1"
                        type="button"
                        onClick={onSwitchMode}
                    >
                        {mode === 'login' ? t('login.register') : t('login.logIn')}
                    </button>
                </span>
            </div>
        </div>
    );
}
