// frontend/src/pages/LoginPage.tsx

import React from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import useAuthForm from '@/hooks/useAuthForm';

export default function LoginPage() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { login } = useAuth();
    const {
        mode,
        form,
        loading,
        error,
        success,
        switchMode,
        handleInputChange,
        handleSubmit,
    } = useAuthForm();

    React.useEffect(() => {
        if (success && mode === 'login') {
            login(); // Set authentication state
            setTimeout(() => navigate('/landing'), 1200);
        }
    }, [success, mode, navigate, login]);

    return (
        <div className="min-h-screen flex">
            {/* Left Side - Black with Text */}
            <div className="flex-1 bg-black text-white flex items-center justify-center p-12">
                <div className="max-w-md">
                    <h1 className="text-4xl font-bold mb-6 tracking-tight">
                        silver
                        <span className="text-gray-300"> agents</span>
                    </h1>
                    <h2 className="text-2xl mb-4 font-light">
                        {t('loginPage.welcomeTitle')}
                    </h2>
                    <p className="text-gray-300 text-lg leading-relaxed mb-6">
                        {t('loginPage.description')}
                    </p>
                    <div className="border-l-4 border-white pl-4">
                        <p className="text-sm text-gray-400 italic">
                            {t('loginPage.exclusiveAccess')}
                        </p>
                    </div>
                </div>
            </div>

            {/* Right Side - White with Form */}
            <div className="flex-1 bg-white flex items-center justify-center p-12">
                <div className="w-full max-w-md">
                    {/* Mode Toggle */}
                    <div className="flex mb-8 bg-gray-100 rounded-lg p-1">
                        <button
                            className={`flex-1 py-3 px-4 rounded-md text-sm font-medium transition-all duration-200 ${
                                mode === 'login'
                                    ? 'bg-white text-gray-900 shadow-sm border border-gray-200'
                                    : 'text-gray-600 hover:text-gray-900'
                            }`}
                            onClick={mode === 'login' ? undefined : switchMode}
                            disabled={mode === 'login'}
                            type="button"
                        >
                            {t('login.logIn')}
                        </button>
                        <button
                            className={`flex-1 py-3 px-4 rounded-md text-sm font-medium transition-all duration-200 ${
                                mode === 'register'
                                    ? 'bg-white text-gray-900 shadow-sm border border-gray-200'
                                    : 'text-gray-600 hover:text-gray-900'
                            }`}
                            onClick={mode === 'register' ? undefined : switchMode}
                            disabled={mode === 'register'}
                            type="button"
                        >
                            {t('login.register')}
                        </button>
                    </div>

                    {/* Header */}
                    <div className="mb-8">
                        <h2 className="text-3xl font-bold text-gray-900 mb-2">
                            {mode === 'login' ? t('login.welcomeBack') : t('login.createAccount')}
                        </h2>
                        <p className="text-gray-600">
                            {mode === 'login' 
                                ? t('login.signInToContinue')
                                : t('login.joinUsToday')
                            }
                        </p>
                    </div>

                    {/* Error/Success messages */}
                    {error && (
                        <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
                            {error}
                        </div>
                    )}
                    {success && (
                        <div className="mb-6 p-4 rounded-lg bg-green-50 border border-green-200 text-green-700 text-sm">
                            {success}
                        </div>
                    )}

                    {/* Form */}
                    <form className="space-y-6" onSubmit={handleSubmit}>
                        {/* Email field */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="email">
                                {t('login.email')}
                            </label>
                            <input
                                name="email"
                                type="email"
                                autoComplete="email"
                                value={form.email}
                                onChange={handleInputChange}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all duration-200 text-gray-900"
                                placeholder={t('login.emailPlaceholder')}
                                required
                            />
                        </div>

                        {/* Register-only fields */}
                        {mode === 'register' && (
                            <>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="username">
                                        {t('login.username')}
                                    </label>
                                    <input
                                        name="username"
                                        type="text"
                                        value={form.username || ''}
                                        onChange={handleInputChange}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all duration-200 text-gray-900"
                                        placeholder={t('login.usernamePlaceholder')}
                                        required
                                    />
                                </div>
                                
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="full_name">
                                        {t('login.fullName')} <span className="text-gray-500 text-xs">({t('login.optional')})</span>
                                    </label>
                                    <input
                                        name="full_name"
                                        type="text"
                                        value={form.full_name || ''}
                                        onChange={handleInputChange}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all duration-200 text-gray-900"
                                        placeholder={t('login.fullNamePlaceholder')}
                                    />
                                </div>
                            </>
                        )}

                        {/* Password field */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="password">
                                {t('login.password')}
                            </label>
                            <input
                                name="password"
                                type="password"
                                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                                value={form.password}
                                onChange={handleInputChange}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all duration-200 text-gray-900"
                                placeholder={t('login.passwordPlaceholder')}
                                required
                            />
                        </div>

                        {/* Submit button */}
                        <button
                            className="w-full bg-black hover:bg-gray-800 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:transform-none disabled:cursor-not-allowed"
                            type="submit"
                            disabled={loading}
                        >
                            {loading ? (
                                <div className="flex items-center justify-center space-x-2">
                                    <div className="w-4 h-4 border-2 border-gray-300 border-t-white rounded-full animate-spin" />
                                    <span>Processing...</span>
                                </div>
                            ) : (
                                <span>
                                    {mode === 'login' ? t('login.logIn') : t('login.register')}
                                </span>
                            )}
                        </button>
                    </form>

                    {/* Footer */}
                    <div className="mt-8 text-center">
                        <p className="text-sm text-gray-600">
                            {mode === 'login' ? t('login.noAccount?') : t('login.account?')}{' '}
                            <button
                                className="text-black hover:text-gray-800 font-medium underline-offset-4 hover:underline transition-all duration-200"
                                type="button"
                                onClick={switchMode}
                            >
                                {mode === 'login' ? t('login.register') : t('login.logIn')}
                            </button>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}