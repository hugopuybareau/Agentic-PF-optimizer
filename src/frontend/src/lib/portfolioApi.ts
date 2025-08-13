import { ApiError } from './api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface PortfolioAsset {
    type: string;
    symbol?: string;
    quantity: number;
    display: string;
}

export interface PortfolioSummary {
    exists: boolean;
    asset_count: number;
    assets: PortfolioAsset[];
    by_type?: Record<string, PortfolioAsset[]>;
    last_updated?: string;
}

export interface ConfirmationResponse {
    success: boolean;
    confirmed?: boolean;
    message: string;
    portfolio_updated?: boolean;
    portfolio_summary?: PortfolioSummary;
    action_result?: any;
}

export interface PortfolioSnapshot {
    portfolio_id: string;
    user_id: string;
    name: string;
    assets: PortfolioAsset[];
    total_assets: number;
    asset_types: string[];
    last_updated: string;
    metadata?: any;
}

class PortfolioApi {
    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const token = localStorage.getItem('access_token');

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...(token && { Authorization: `Bearer ${token}` }),
                ...options.headers,
            },
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({
                detail: 'An error occurred',
            }));
            throw new ApiError(error.detail || 'An error occurred', response.status);
        }

        return response.json();
    }

    async getPortfolioSummary(portfolioName: string = 'Main Portfolio'): Promise<PortfolioSummary> {
        return this.request<PortfolioSummary>(
            `/portfolio/summary?portfolio_name=${encodeURIComponent(portfolioName)}`
        );
    }

    async getPortfolioSnapshot(portfolioName: string = 'Main Portfolio'): Promise<PortfolioSnapshot> {
        return this.request<PortfolioSnapshot>(
            `/portfolio/snapshot?portfolio_name=${encodeURIComponent(portfolioName)}`
        );
    }

    async confirmAction(
        confirmationId: string,
        confirmed: boolean
    ): Promise<ConfirmationResponse> {
        return this.request<ConfirmationResponse>('/portfolio/confirm', {
            method: 'POST',
            body: JSON.stringify({
                confirmation_id: confirmationId,
                confirmed,
            }),
        });
    }

    async confirmChatAction(
        sessionId: string,
        confirmationId: string,
        confirmed: boolean
    ): Promise<ConfirmationResponse> {
        return this.request<ConfirmationResponse>('/chat/confirm', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                confirmation_id: confirmationId,
                confirmed,
            }),
        });
    }

    async clearPortfolio(
        portfolioName: string = 'Main Portfolio',
        confirm: boolean = false
    ): Promise<any> {
        return this.request(`/portfolio/clear?portfolio_name=${encodeURIComponent(portfolioName)}&confirm=${confirm}`, {
            method: 'DELETE',
        });
    }

    // Subscribe to portfolio updates via Server-Sent Events
    subscribeToUpdates(
        onUpdate: (event: any) => void,
        onError?: (error: any) => void
    ): EventSource {
        const token = localStorage.getItem('access_token');
        const eventSource = new EventSource(
            `${API_BASE_URL}/portfolio/stream`,
            {
                withCredentials: true,
            }
        );

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onUpdate(data);
            } catch (error) {
                console.error('Failed to parse portfolio update:', error);
            }
        };

        eventSource.onerror = (error) => {
            console.error('Portfolio stream error:', error);
            if (onError) {
                onError(error);
            }
        };

        return eventSource;
    }
}

export const portfolioApi = new PortfolioApi();