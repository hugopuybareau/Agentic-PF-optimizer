// frontend/src/lib/api.ts

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface ChatMessage {
    message: string;
    session_id?: string;
}

export interface ChatResponse {
    message: string;
    session_id: string;
    ui_hints?: Record<string, any>;
    show_form?: boolean;
    form_data?: Record<string, any>;
    portfolio_summary?: Record<string, any>;
}

export interface Portfolio {
    assets: Array<{
        type: string;
        ticker?: string;
        symbol?: string;
        shares?: number;
        amount?: number;
        currency?: string;
    }>;
}

export interface PortfolioSubmission {
    session_id: string;
    portfolio: Portfolio;
    analyze_immediately?: boolean;
}

class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = 'ApiError';
    }
}

async function fetchApi<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const defaultHeaders = {
        'Content-Type': 'application/json',
    };

    const config: RequestInit = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    try {
        const response = await fetch(url, config);
        const data = await response.json();

        if (!response.ok) {
            throw new ApiError(
                response.status,
                data.detail || `HTTP ${response.status}`
            );
        }

        return data;
    } catch (error) {
        if (error instanceof ApiError) {
            throw error;
        }
        throw new ApiError(
            0,
            `Network error: ${
                error instanceof Error ? error.message : 'Unknown error'
            }`
        );
    }
}

export const chatApi = {
    sendMessage: async (message: ChatMessage): Promise<ChatResponse> => {
        return fetchApi<ChatResponse>('/chat/message', {
            method: 'POST',
            body: JSON.stringify(message),
        });
    },

    sendMessageStream: async (message: ChatMessage): Promise<Response> => {
        const url = `${API_BASE_URL}/chat/message/stream`;
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(message),
        });

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new ApiError(
                response.status,
                data.detail || `HTTP ${response.status}`
            );
        }

        return response;
    },

    submitPortfolio: async (submission: PortfolioSubmission): Promise<any> => {
        return fetchApi('/api/chat/submit-portfolio', {
            method: 'POST',
            body: JSON.stringify(submission),
        });
    },

    getSessionPortfolio: async (sessionId: string): Promise<any> => {
        return fetchApi(`/chat/session/${sessionId}/portfolio`);
    },

    clearSession: async (sessionId: string): Promise<any> => {
        return fetchApi(`/chat/session/${sessionId}`, {
            method: 'DELETE',
        });
    },

    getSuggestions: async (assetType?: string): Promise<any> => {
        const params = assetType
            ? `?asset_type=${encodeURIComponent(assetType)}`
            : '';
        return fetchApi(`/chat/suggestions${params}`);
    },
};

export { ApiError };
