// frontend/src/components/PortfolioConfirmation.tsx

import React from 'react';
import {
    Check,
    X,
    TrendingUp,
    TrendingDown,
    DollarSign,
    Home,
    Briefcase,
    Banknote,
} from 'lucide-react';

interface AssetConfirmation {
    type: 'stock' | 'crypto' | 'real_estate' | 'mortgage' | 'cash';
    symbol?: string;
    name?: string;
    quantity: number;
    current_quantity?: number;
    action: 'add_asset' | 'remove_asset' | 'update_asset';
    display_text: string;
}

interface ConfirmationRequest {
    confirmation_id: string;
    action: string;
    assets: AssetConfirmation[];
    message: string;
    requires_confirmation: boolean;
}

interface PortfolioConfirmationProps {
    confirmationRequest: ConfirmationRequest;
    onConfirm: (confirmationId: string, confirmed: boolean) => void;
    isProcessing?: boolean;
}

const PortfolioConfirmation: React.FC<PortfolioConfirmationProps> = ({
    confirmationRequest,
    onConfirm,
    isProcessing = false,
}) => {
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

    const getActionColor = (action: string) => {
        switch (action) {
            case 'add_asset':
                return 'text-green-600 dark:text-green-400';
            case 'remove_asset':
                return 'text-red-600 dark:text-red-400';
            case 'update_asset':
                return 'text-blue-600 dark:text-blue-400';
            default:
                return 'text-gray-600 dark:text-gray-400';
        }
    };

    const getActionLabel = (action: string) => {
        switch (action) {
            case 'add_asset':
                return 'Adding';
            case 'remove_asset':
                return 'Removing';
            case 'update_asset':
                return 'Updating';
            default:
                return 'Modifying';
        }
    };

    return (
        <div className="mt-3 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="flex flex-col space-y-3">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Portfolio Action Required
                        </span>
                    </div>
                    <span
                        className={`text-xs font-semibold ${getActionColor(
                            confirmationRequest.action
                        )}`}
                    >
                        {getActionLabel(confirmationRequest.action)}
                    </span>
                </div>

                {/* Message */}
                <p className="text-sm text-gray-600 dark:text-gray-400">
                    {confirmationRequest.message}
                </p>

                {/* Assets List */}
                <div className="space-y-2">
                    {confirmationRequest.assets.map((asset, index) => (
                        <div
                            key={index}
                            className="flex items-center justify-between p-2 bg-white/50 dark:bg-gray-800/50 rounded-md"
                        >
                            <div className="flex items-center space-x-3">
                                <div
                                    className={`p-1.5 rounded-md ${
                                        asset.action === 'add_asset'
                                            ? 'bg-green-100 dark:bg-green-900/30'
                                            : asset.action === 'remove_asset'
                                            ? 'bg-red-100 dark:bg-red-900/30'
                                            : 'bg-blue-100 dark:bg-blue-900/30'
                                    }`}
                                >
                                    {getAssetIcon(asset.type)}
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                        {asset.display_text}
                                    </p>
                                    {asset.current_quantity !== undefined && (
                                        <p className="text-xs text-gray-500 dark:text-gray-500">
                                            Current: {asset.current_quantity}
                                        </p>
                                    )}
                                </div>
                            </div>
                            {asset.symbol && (
                                <span className="text-xs font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                                    {asset.symbol}
                                </span>
                            )}
                        </div>
                    ))}
                </div>

                {/* Action Buttons */}
                <div className="flex items-center justify-end space-x-2 pt-2">
                    <button
                        onClick={() =>
                            onConfirm(
                                confirmationRequest.confirmation_id,
                                false
                            )
                        }
                        disabled={isProcessing}
                        className="flex items-center space-x-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg border border-gray-300 dark:border-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <X className="w-4 h-4" />
                        <span>Cancel</span>
                    </button>
                    <button
                        onClick={() =>
                            onConfirm(confirmationRequest.confirmation_id, true)
                        }
                        disabled={isProcessing}
                        className="flex items-center space-x-1 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 rounded-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isProcessing ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                <span>Processing...</span>
                            </>
                        ) : (
                            <>
                                <Check className="w-4 h-4" />
                                <span>Confirm</span>
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PortfolioConfirmation;
