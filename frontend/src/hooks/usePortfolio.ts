// frontend/src/hooks/usePortfolio.ts

import { useState, useEffect, useCallback } from 'react';
import { portfolioApi, PortfolioSummary } from '@/lib/portfolioApi';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';

export function usePortfolio() {
    const [portfolioSummary, setPortfolioSummary] = useState<PortfolioSummary | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { toast } = useToast();
    const { user } = useAuth();

    // Fetch portfolio summary
    const fetchPortfolio = useCallback(async () => {
        if (!user) {
            setPortfolioSummary(null);
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const summary = await portfolioApi.getPortfolioSummary();
            setPortfolioSummary(summary);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to fetch portfolio';
            setError(errorMessage);
            console.error('Failed to fetch portfolio:', err);
        } finally {
            setIsLoading(false);
        }
    }, [user]);

    // Subscribe to portfolio updates
    useEffect(() => {
        if (!user) return;

        let eventSource: EventSource | null = null;

        const setupEventSource = () => {
            eventSource = portfolioApi.subscribeToUpdates(
                (event) => {
                    console.log('Portfolio update received:', event);
                    
                    // Handle different event types
                    if (event.event_type === 'ASSET_ADDED' || 
                        event.event_type === 'ASSET_REMOVED' || 
                        event.event_type === 'ASSET_UPDATED') {
                        // Refresh portfolio
                        fetchPortfolio();
                        
                        // Show toast notification
                        toast({
                            title: 'Portfolio Updated',
                            description: `Asset ${event.event_type.toLowerCase().replace('_', ' ')}`,
                            variant: 'success',
                        });
                    }
                },
                (error) => {
                    console.error('Portfolio stream error:', error);
                    // Attempt to reconnect after 5 seconds
                    setTimeout(() => {
                        if (eventSource) {
                            eventSource.close();
                            setupEventSource();
                        }
                    }, 5000);
                }
            );
        };

        // Initial fetch
        fetchPortfolio();
        
        // Set up SSE connection (optional - only if backend SSE is fully implemented)
        // setupEventSource();

        // Cleanup
        return () => {
            if (eventSource) {
                eventSource.close();
            }
        };
    }, [user, fetchPortfolio, toast]);

    // Confirm portfolio action
    const confirmAction = useCallback(async (
        confirmationId: string,
        confirmed: boolean,
        sessionId?: string
    ): Promise<boolean> => {
        try {
            const response = sessionId 
                ? await portfolioApi.confirmChatAction(sessionId, confirmationId, confirmed)
                : await portfolioApi.confirmAction(confirmationId, confirmed);

            if (response.success) {
                if (response.confirmed && response.portfolio_updated) {
                    // Update local portfolio state
                    if (response.portfolio_summary) {
                        setPortfolioSummary(response.portfolio_summary);
                    } else {
                        // Refetch if summary not provided
                        await fetchPortfolio();
                    }

                    toast({
                        title: 'Portfolio Updated',
                        description: response.message || 'Your portfolio has been updated successfully',
                        variant: 'success',
                    });
                } else if (!response.confirmed) {
                    toast({
                        title: 'Action Cancelled',
                        description: 'The portfolio update was cancelled',
                        variant: 'default',
                    });
                }

                return true;
            } else {
                toast({
                    title: 'Action Failed',
                    description: response.message || 'Failed to process portfolio action',
                    variant: 'destructive',
                });
                return false;
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to confirm action';
            toast({
                title: 'Error',
                description: errorMessage,
                variant: 'destructive',
            });
            return false;
        }
    }, [fetchPortfolio, toast]);

    // Clear portfolio
    const clearPortfolio = useCallback(async (): Promise<boolean> => {
        try {
            const response = await portfolioApi.clearPortfolio('Main Portfolio', true);
            
            if (response.success) {
                setPortfolioSummary({
                    exists: true,
                    asset_count: 0,
                    assets: [],
                    by_type: {},
                    last_updated: new Date().toISOString()
                });

                toast({
                    title: 'Portfolio Cleared',
                    description: response.message || 'All assets have been removed from your portfolio',
                    variant: 'success',
                });

                return true;
            }
            
            return false;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to clear portfolio';
            toast({
                title: 'Error',
                description: errorMessage,
                variant: 'destructive',
            });
            return false;
        }
    }, [toast]);

    return {
        portfolioSummary,
        isLoading,
        error,
        fetchPortfolio,
        confirmAction,
        clearPortfolio,
    };
}