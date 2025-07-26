// src/hooks/useAuthForm.ts

import { useState } from 'react';

import { useTranslation } from 'react-i18next';

export type AuthFormType = 'login' | 'register';

export interface AuthFormState {
    email: string;
    password: string;
    username?: string;
    full_name?: string;
}

export default function useAuthForm() {
    const { i18n } = useTranslation();
    const { t } = useTranslation();
    const [mode, setMode] = useState<AuthFormType>('login');
    const [form, setForm] = useState<AuthFormState>({
        email: '',
        password: '',
        username: '',
        full_name: '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setForm({ ...form, [e.target.name]: e.target.value });
        setError(null);
        setSuccess(null);
    };

    const switchMode = () => {
        setMode(mode === 'login' ? 'register' : 'login');
        setForm({
            email: '',
            password: '',
            username: '',
            full_name: '',
        });
        setError(null);
        setSuccess(null);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccess(null);
        try {
            const endpoint =
                mode === 'login' ? '/auth/login' : '/auth/register';
            const payload =
                mode === 'login'
                    ? { email: form.email, password: form.password }
                    : {
                          email: form.email,
                          username: form.username,
                          password: form.password,
                          full_name: form.full_name || undefined,
                          preferred_language: i18n.language || 'en',
                      };

            const response = await fetch(
                `${import.meta.env.VITE_API_URL}${endpoint}`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || t('error.occured'));
            }

            if (mode === 'login') {
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                setSuccess(t('login.successLogin'));
            } else {
                setSuccess(t('login.successRegister'));
                setMode('login');
                setForm({
                    email: '',
                    password: '',
                    username: '',
                    full_name: '',
                });
            }
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : t('error.unknown'));
        } finally {
            setLoading(false);
        }
    };

    return {
        mode,
        form,
        loading,
        error,
        success,
        setMode,
        switchMode,
        handleInputChange,
        handleSubmit,
    };
}
