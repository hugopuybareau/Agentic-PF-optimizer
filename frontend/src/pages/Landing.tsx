// frontend/src/pages/Landing.tsx

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Eye, EyeOff, Mail, Lock, User, UserPlus, LogIn } from 'lucide-react';
import useAuthForm from '@/hooks/useAuthForm';

export default function Landing() {
    const { t } = useTranslation();
    const [showPassword, setShowPassword] = useState(false);
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

    return (
        <div className="min-h-screen flex">
            {/* Left Side - Login Form (Black) */}
            <div className="w-1/2 bg-black flex items-center justify-center p-8">
                <div className="w-full max-w-md">
                    {/* Logo */}
                    <div className="mb-8 text-center">
                        <h1 className="text-2xl font-bold text-white mb-2">
                            silver <span className="text-gray-400">agents</span>
                        </h1>
                    </div>

                    {/* Login Form */}
                    <div className="bg-gray-900 p-6 rounded-lg">
                        <div className="mb-6 text-center">
                            <h2 className="text-xl font-semibold text-white mb-2">
                                {mode === 'login' ? t('login.welcomeBack') : t('login.createAccount')}
                            </h2>
                            <p className="text-gray-400 text-sm">
                                {mode === 'login' ? t('login.signInToContinue') : t('login.joinUsToday')}
                            </p>
                        </div>

                        {/* Success Message */}
                        {success && (
                            <div className="mb-4 p-3 bg-green-900/50 border border-green-600 rounded-lg">
                                <p className="text-green-400 text-sm text-center">
                                    {success}
                                </p>
                            </div>
                        )}

                        {/* Error Message */}
                        {error && (
                            <div className="mb-4 p-3 bg-red-900/50 border border-red-600 rounded-lg">
                                <p className="text-red-400 text-sm text-center">
                                    {error}
                                </p>
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-4">
                            {/* Email Field */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-300">
                                    {t('login.email')}
                                </label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                    <input
                                        type="email"
                                        name="email"
                                        value={form.email}
                                        onChange={handleInputChange}
                                        placeholder={t('login.emailPlaceholder')}
                                        className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        required
                                    />
                                </div>
                            </div>

                            {/* Username Field (Register only) */}
                            {mode === 'register' && (
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-gray-300">
                                        {t('login.username')}
                                    </label>
                                    <div className="relative">
                                        <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                        <input
                                            type="text"
                                            name="username"
                                            value={form.username || ''}
                                            onChange={handleInputChange}
                                            placeholder={t('login.usernamePlaceholder')}
                                            className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            required
                                        />
                                    </div>
                                </div>
                            )}

                            {/* Full Name Field (Register only) */}
                            {mode === 'register' && (
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-gray-300">
                                        {t('login.fullName')} <span className="text-gray-500 text-xs">{t('common.optional')}</span>
                                    </label>
                                    <div className="relative">
                                        <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                        <input
                                            type="text"
                                            name="full_name"
                                            value={form.full_name || ''}
                                            onChange={handleInputChange}
                                            placeholder={t('login.fullNamePlaceholder')}
                                            className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        />
                                    </div>
                                </div>
                            )}

                            {/* Password Field */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-300">
                                    {t('login.password')}
                                </label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                    <input
                                        type={showPassword ? 'text' : 'password'}
                                        name="password"
                                        value={form.password}
                                        onChange={handleInputChange}
                                        placeholder={t('login.passwordPlaceholder')}
                                        className="w-full pl-10 pr-12 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        required
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="absolute right-3 top-3 text-gray-400 hover:text-gray-300"
                                    >
                                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                    </button>
                                </div>
                            </div>

                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <span>{t('common.processing')}</span>
                                ) : (
                                    <>
                                        {mode === 'login' ? (
                                            <>
                                                <LogIn className="h-4 w-4" />
                                                {t('login.logIn')}
                                            </>
                                        ) : (
                                            <>
                                                <UserPlus className="h-4 w-4" />
                                                {t('login.register')}
                                            </>
                                        )}
                                    </>
                                )}
                            </button>

                            {/* Mode Switch */}
                            <div className="text-center pt-4">
                                <p className="text-gray-400 text-sm">
                                    {mode === 'login' ? t('login.noAccount?') : t('login.account?')}
                                    <button
                                        type="button"
                                        onClick={switchMode}
                                        className="text-blue-400 hover:text-blue-300 ml-1 font-medium"
                                    >
                                        {mode === 'login' ? t('login.register') : t('login.logIn')}
                                    </button>
                                </p>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            {/* Right Side - Welcome Text (White) */}
            <div className="w-1/2 bg-white flex items-center justify-center p-8">
                <div className="text-center max-w-md">
                    <h1 className="text-3xl font-bold text-gray-900 mb-6">
                        {t('landing.testPlatform.title')}
                    </h1>
                    <p className="text-lg text-gray-600">
                        {t('landing.testPlatform.subtitle')}
                    </p>
                </div>
            </div>
        </div>
    );
}
