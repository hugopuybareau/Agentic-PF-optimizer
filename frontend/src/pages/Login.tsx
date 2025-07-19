// src/pages/LoginPage.tsx

import React from 'react';

import { useNavigate } from 'react-router-dom';
import LoginForm from '@/components/LoginForm';
import useAuthForm from '@/hooks/useAuthForm';

export default function LoginPage() {
    const navigate = useNavigate();
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
            setTimeout(() => navigate('/'), 1200);
        }
    }, [success, mode, navigate]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-background px-4">
            <LoginForm
                mode={mode}
                form={form}
                loading={loading}
                error={error}
                success={success}
                onInputChange={handleInputChange}
                onSubmit={handleSubmit}
                onSwitchMode={switchMode}
                onClose={() => navigate('/')}
            />
        </div>
    );
}
