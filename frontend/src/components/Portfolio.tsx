import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Target, 
  Shield,
  PieChart,
  BarChart3,
  RefreshCcw,
  Download
} from 'lucide-react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

const mockPortfolio = {
  totalValue: 142750,
  dailyChange: 2.34,
  weeklyChange: -1.2,
  monthlyChange: 8.7,
  riskScore: 6.8,
  diversificationScore: 8.2,
  lastUpdated: new Date(),
  assets: [
    { 
      name: 'Apple Inc.', 
      symbol: 'AAPL', 
      value: 28550, 
      shares: 150, 
      price: 190.33, 
      change: 2.1, 
      percentage: 20,
      sector: 'Technology'
    },
    { 
      name: 'Microsoft Corp.', 
      symbol: 'MSFT', 
      value: 25620, 
      shares: 75, 
      price: 341.60, 
      change: 1.8, 
      percentage: 18,
      sector: 'Technology'
    },
    { 
      name: 'Vanguard S&P 500', 
      symbol: 'VOO', 
      value: 21412.5, 
      shares: 50, 
      price: 428.25, 
      change: 1.5, 
      percentage: 15,
      sector: 'Index Fund'
    },
    { 
      name: 'Tesla Inc.', 
      symbol: 'TSLA', 
      value: 17130, 
      shares: 80, 
      price: 214.13, 
      change: -0.8, 
      percentage: 12,
      sector: 'Automotive'
    },
    { 
      name: 'Bitcoin', 
      symbol: 'BTC', 
      value: 14275, 
      shares: 0.25, 
      price: 57100, 
      change: 4.2, 
      percentage: 10,
      sector: 'Cryptocurrency'
    },
  ],
  sectors: [
    { name: 'Technology', value: 54170, percentage: 38, color: '#14B8A6' },
    { name: 'Index Funds', value: 21412.5, percentage: 15, color: '#06B6D4' },
    { name: 'Automotive', value: 17130, percentage: 12, color: '#8B5CF6' },
    { name: 'Cryptocurrency', value: 14275, percentage: 10, color: '#F59E0B' },
    { name: 'Other', value: 35762.5, percentage: 25, color: '#64748B' },
  ]
};

export function Portfolio() {
  const [selectedTimeframe, setSelectedTimeframe] = useState('1D');
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate data refresh
    setTimeout(() => setRefreshing(false), 2000);
  };

  const timeframes = ['1D', '1W', '1M', '3M', '1Y'];

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-slate-950 to-slate-900 min-h-full">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Portfolio Overview</h1>
          <p className="text-slate-400">
            Last updated: {mockPortfolio.lastUpdated.toLocaleString()}
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={refreshing}
            className="border-slate-700 bg-slate-800/50 hover:bg-slate-700/50"
          >
            <RefreshCcw size={16} className={`mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button className="bg-teal-500 hover:bg-teal-600">
            <Download size={16} className="mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="bg-slate-800/50 border-slate-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Total Value</p>
                <p className="text-2xl font-bold text-slate-100">
                  ${mockPortfolio.totalValue.toLocaleString()}
                </p>
              </div>
              <DollarSign className="text-teal-400" size={24} />
            </div>
            <div className="flex items-center gap-1 mt-2">
              <TrendingUp size={16} className="text-green-400" />
              <span className="text-sm text-green-400">+{mockPortfolio.dailyChange}%</span>
              <span className="text-xs text-slate-400">today</span>
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="bg-slate-800/50 border-slate-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Weekly Change</p>
                <p className="text-2xl font-bold text-slate-100">
                  {mockPortfolio.weeklyChange > 0 ? '+' : ''}{mockPortfolio.weeklyChange}%
                </p>
              </div>
              <TrendingDown className="text-red-400" size={24} />
            </div>
            <div className="flex items-center gap-1 mt-2">
              <span className="text-xs text-slate-400">7 days</span>
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="bg-slate-800/50 border-slate-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Risk Score</p>
                <p className="text-2xl font-bold text-slate-100">{mockPortfolio.riskScore}/10</p>
              </div>
              <Shield className="text-amber-400" size={24} />
            </div>
            <Progress value={mockPortfolio.riskScore * 10} className="mt-2 h-2" />
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="bg-slate-800/50 border-slate-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Diversification</p>
                <p className="text-2xl font-bold text-slate-100">{mockPortfolio.diversificationScore}/10</p>
              </div>
              <Target className="text-green-400" size={24} />
            </div>
            <Progress value={mockPortfolio.diversificationScore * 10} className="mt-2 h-2" />
          </Card>
        </motion.div>
      </div>

      {/* Portfolio Content */}
      <Tabs defaultValue="holdings" className="space-y-6">
        <TabsList className="bg-slate-800/50 border border-slate-700">
          <TabsTrigger value="holdings" className="data-[state=active]:bg-teal-500/20">
            Holdings
          </TabsTrigger>
          <TabsTrigger value="allocation" className="data-[state=active]:bg-teal-500/20">
            Allocation
          </TabsTrigger>
          <TabsTrigger value="performance" className="data-[state=active]:bg-teal-500/20">
            Performance
          </TabsTrigger>
        </TabsList>

        <TabsContent value="holdings" className="space-y-4">
          <Card className="bg-slate-800/50 border-slate-700">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-slate-100 mb-4">Individual Holdings</h3>
              <div className="space-y-3">
                {mockPortfolio.assets.map((asset, index) => (
                  <motion.div
                    key={asset.symbol}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg border border-slate-700"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-teal-500/20 rounded-full flex items-center justify-center">
                        <span className="text-sm font-bold text-teal-400">
                          {asset.symbol.slice(0, 2)}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-slate-100">{asset.name}</p>
                        <p className="text-sm text-slate-400">{asset.symbol}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-slate-100">${asset.value.toLocaleString()}</p>
                      <div className="flex items-center gap-1">
                        {asset.change > 0 ? (
                          <TrendingUp size={14} className="text-green-400" />
                        ) : (
                          <TrendingDown size={14} className="text-red-400" />
                        )}
                        <span className={`text-sm ${asset.change > 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {asset.change > 0 ? '+' : ''}{asset.change}%
                        </span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="allocation" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-slate-800/50 border-slate-700 p-6">
              <h3 className="text-lg font-semibold text-slate-100 mb-4">Sector Allocation</h3>
              <div className="space-y-4">
                {mockPortfolio.sectors.map((sector, index) => (
                  <motion.div
                    key={sector.name}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="space-y-2"
                  >
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-300">{sector.name}</span>
                      <span className="text-slate-400">{sector.percentage}%</span>
                    </div>
                    <Progress 
                      value={sector.percentage} 
                      className="h-3"
                      style={{
                        '--progress-background': sector.color,
                      } as React.CSSProperties}
                    />
                  </motion.div>
                ))}
              </div>
            </Card>

            <Card className="bg-slate-800/50 border-slate-700 p-6">
              <h3 className="text-lg font-semibold text-slate-100 mb-4">Asset Distribution</h3>
              <div className="relative w-48 h-48 mx-auto">
                <svg viewBox="0 0 200 200" className="w-full h-full">
                  {mockPortfolio.sectors.map((sector, index) => {
                    const radius = 80;
                    const circumference = 2 * Math.PI * radius;
                    const strokeDasharray = `${(sector.percentage / 100) * circumference} ${circumference}`;
                    const strokeDashoffset = -index * (circumference / mockPortfolio.sectors.length);
                    
                    return (
                      <circle
                        key={sector.name}
                        cx="100"
                        cy="100"
                        r={radius}
                        fill="none"
                        stroke={sector.color}
                        strokeWidth="16"
                        strokeDasharray={strokeDasharray}
                        strokeDashoffset={strokeDashoffset}
                        className="transform -rotate-90 origin-center"
                      />
                    );
                  })}
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-slate-100">100%</p>
                    <p className="text-sm text-slate-400">Allocated</p>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card className="bg-slate-800/50 border-slate-700 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-slate-100">Performance Chart</h3>
              <div className="flex gap-2">
                {timeframes.map((timeframe) => (
                  <Button
                    key={timeframe}
                    variant={selectedTimeframe === timeframe ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedTimeframe(timeframe)}
                    className={selectedTimeframe === timeframe 
                      ? "bg-teal-500/20 border-teal-500/30 text-teal-400" 
                      : "border-slate-700 text-slate-400"
                    }
                  >
                    {timeframe}
                  </Button>
                ))}
              </div>
            </div>
            <div className="h-64 flex items-center justify-center bg-slate-900/50 rounded-lg border border-slate-700">
              <div className="text-center">
                <BarChart3 className="mx-auto mb-2 text-slate-400" size={48} />
                <p className="text-slate-400">Performance chart for {selectedTimeframe}</p>
                <p className="text-sm text-slate-500 mt-1">Chart visualization would be integrated here</p>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}