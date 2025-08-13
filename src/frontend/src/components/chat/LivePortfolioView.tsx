import React, { useState, useEffect } from 'react';
import {
    TrendingUp,
    TrendingDown,
    DollarSign,
    Home,
    Briefcase,
    Banknote,
    RefreshCw,
    Eye,
    EyeOff,
    Plus,
} from 'lucide-react';

interface PortfolioAsset {
    type: string;
    symbol?: string;
    quantity: number;
    display: string;
}

interface PortfolioSummary {
    exists: boolean;
    asset_count: number;
    assets: PortfolioAsset[];
    by_type?: Record<string, PortfolioAsset[]>;
    last_updated?: string;
}

interface LivePortfolioViewProps {
    portfolioSummary: PortfolioSummary | null;
    isLoading?: boolean;
    onRefresh?: () => void;
    onAddAsset?: () => void;
    isExpanded?: boolean;
    className?: string;
}

const LivePortfolioView: React.FC<LivePortfolioViewProps> = ({
    portfolioSummary,
    isLoading = false,
    onRefresh,
    onAddAsset,
    isExpanded = true,
    className = '',
}) => {
    const [showDetails, setShowDetails] = useState(isExpanded);
    const [animateUpdate, setAnimateUpdate] = useState(false);

    // Trigger animation when portfolio updates
    useEffect(() => {
        if (portfolioSummary?.last_updated) {
            setAnimateUpdate(true);
            const timer = setTimeout(() => setAnimateUpdate(false), 1000);
            return () => clearTimeout(timer);
        }
    }, [portfolioSummary?.last_updated]);

    const getAssetIcon = (type: string) => {
        switch (type) {
            case 'stock':
                return <TrendingUp className="w-4 h-4" />;
            case 'crypto':
                return <TrendingDown className="w-4 h-4" />;
            case 'real_estate':
                return <Home className="w-4 h-4" />;
            case 'mortgage':
                return <Briefcase className="w-4 h-4" />;
            case 'cash':
                return <Banknote className="w-4 h-4" />;
            default:
                return <DollarSign className="w-4 h-4" />;
        }
    };

    const getAssetColor = (type: string) => {
        switch (type) {
            case 'stock':
                return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400';
            case 'crypto':
                return 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400';
            case 'real_estate':
                return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400';
            case 'mortgage':
                return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400';
            case 'cash':
                return 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400';
            default:
                return 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400';
        }
    };

    const formatLastUpdated = (timestamp?: string) => {
        if (!timestamp) return 'Never';
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} min ago`;
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24)
            return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        return date.toLocaleDateString();
    };

    if (!portfolioSummary || !portfolioSummary.exists) {
        return (
            <div
                className={`bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 rounded-xl p-6 ${className}`}
            >
                <div className="text-center space-y-4">
                    <div className="w-16 h-16 mx-auto bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
                        <DollarSign className="w-8 h-8 text-gray-400" />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">
                            No Portfolio Yet
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                            Start building your portfolio by adding assets
                        </p>
                    </div>
                    {onAddAsset && (
                        <button
                            onClick={onAddAsset}
                            className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                        >
                            <Plus className="w-4 h-4" />
                            <span>Add First Asset</span>
                        </button>
                    )}
                </div>
            </div>
        );
    }

    return (
        <div
            className={`bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 rounded-xl border border-blue-200 dark:border-blue-800 ${
                animateUpdate ? 'ring-2 ring-blue-400 ring-opacity-50' : ''
            } transition-all duration-300 ${className}`}
        >
            {/* Header */}
            <div className="p-4 border-b border-blue-200 dark:border-blue-800">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <div className="relative">
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                                <DollarSign className="w-5 h-5 text-white" />
                            </div>
                            {animateUpdate && (
                                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-ping" />
                            )}
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                                Live Portfolio
                            </h3>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                                {portfolioSummary.asset_count} asset
                                {portfolioSummary.asset_count !== 1 ? 's' : ''}{' '}
                                • Updated{' '}
                                {formatLastUpdated(
                                    portfolioSummary.last_updated
                                )}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center space-x-2">
                        {onRefresh && (
                            <button
                                onClick={onRefresh}
                                disabled={isLoading}
                                className="p-2 hover:bg-white/50 dark:hover:bg-gray-800/50 rounded-lg transition-colors"
                                title="Refresh portfolio"
                            >
                                <RefreshCw
                                    className={`w-4 h-4 ${
                                        isLoading ? 'animate-spin' : ''
                                    }`}
                                />
                            </button>
                        )}
                        <button
                            onClick={() => setShowDetails(!showDetails)}
                            className="p-2 hover:bg-white/50 dark:hover:bg-gray-800/50 rounded-lg transition-colors"
                            title={
                                showDetails ? 'Hide details' : 'Show details'
                            }
                        >
                            {showDetails ? (
                                <EyeOff className="w-4 h-4" />
                            ) : (
                                <Eye className="w-4 h-4" />
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Asset Summary */}
            {showDetails && (
                <div className="p-4 space-y-4">
                    {/* By Type Summary */}
                    {portfolioSummary.by_type &&
                        Object.keys(portfolioSummary.by_type).length > 0 && (
                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                                {Object.entries(portfolioSummary.by_type).map(
                                    ([type, assets]) => (
                                        <div
                                            key={type}
                                            className={`flex items-center space-x-2 p-2 rounded-lg ${getAssetColor(
                                                type
                                            )}`}
                                        >
                                            {getAssetIcon(type)}
                                            <div className="flex-1">
                                                <p className="text-xs font-medium capitalize">
                                                    {type.replace('_', ' ')}
                                                </p>
                                                <p className="text-sm font-semibold">
                                                    {assets.length}
                                                </p>
                                            </div>
                                        </div>
                                    )
                                )}
                            </div>
                        )}

                    {/* Detailed Asset List */}
                    <div className="space-y-2">
                        <div className="flex items-center justify-between mb-2">
                            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                Holdings
                            </h4>
                            {onAddAsset && (
                                <button
                                    onClick={onAddAsset}
                                    className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 flex items-center space-x-1"
                                >
                                    <Plus className="w-3 h-3" />
                                    <span>Add</span>
                                </button>
                            )}
                        </div>

                        <div className="max-h-64 overflow-y-auto space-y-1">
                            {portfolioSummary.assets.map((asset, index) => (
                                <div
                                    key={index}
                                    className="flex items-center justify-between p-2 bg-white/50 dark:bg-gray-800/50 rounded-lg hover:bg-white/70 dark:hover:bg-gray-800/70 transition-colors"
                                >
                                    <div className="flex items-center space-x-3">
                                        <div
                                            className={`p-1.5 rounded-md ${getAssetColor(
                                                asset.type
                                            )}`}
                                        >
                                            {getAssetIcon(asset.type)}
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                                {asset.display}
                                            </p>
                                            {asset.symbol && (
                                                <p className="text-xs text-gray-500 dark:text-gray-500">
                                                    {asset.type.toUpperCase()}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                    {asset.quantity !== undefined &&
                                        asset.type !== 'real_estate' &&
                                        asset.type !== 'mortgage' && (
                                            <span className="text-sm font-mono text-gray-600 dark:text-gray-400">
                                                {asset.quantity}
                                            </span>
                                        )}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Empty State for Asset List */}
                    {portfolioSummary.assets.length === 0 && (
                        <div className="text-center py-4">
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                                No assets in portfolio
                            </p>
                        </div>
                    )}
                </div>
            )}

            {/* Loading Overlay */}
            {isLoading && (
                <div className="absolute inset-0 bg-white/50 dark:bg-gray-900/50 rounded-xl flex items-center justify-center">
                    <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                            Updating...
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LivePortfolioView;
