import React from 'react';
import { motion } from 'framer-motion';
import { 
  MessageCircle, 
  PieChart, 
  Bell, 
  Settings as SettingsIcon, 
  ChevronLeft, 
  ChevronRight,
  TrendingUp,
  Shield,
  DollarSign
} from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Progress } from './ui/progress';
import { WolfyAvatar } from './WolfyAvatar';

type View = 'chat' | 'portfolio' | 'alerts' | 'settings';

interface SidebarProps {
  currentView: View;
  onViewChange: (view: View) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const mockPortfolio = {
  totalValue: 142750,
  dailyChange: 2.34,
  riskScore: 6.8,
  assets: [
    { name: 'Stocks', value: 85650, percentage: 60, color: '#14B8A6' },
    { name: 'Bonds', value: 28550, percentage: 20, color: '#06B6D4' },
    { name: 'Crypto', value: 21412.5, percentage: 15, color: '#8B5CF6' },
    { name: 'Cash', value: 7137.5, percentage: 5, color: '#64748B' },
  ]
};

export function Sidebar({ currentView, onViewChange, isCollapsed, onToggleCollapse }: SidebarProps) {
  const navItems = [
    { id: 'chat' as View, label: 'Chat with Wolfy', icon: MessageCircle },
    { id: 'portfolio' as View, label: 'Portfolio', icon: PieChart },
    { id: 'alerts' as View, label: 'Alerts', icon: Bell },
    { id: 'settings' as View, label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <motion.aside
      animate={{ width: isCollapsed ? 80 : 320 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="bg-slate-900/50 backdrop-blur-xl border-r border-slate-800 flex flex-col"
    >
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        {!isCollapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-3"
          >
            <WolfyAvatar size="sm" isActive />
            <div>
              <h1 className="text-lg font-bold text-teal-400">Wolfy</h1>
              <p className="text-xs text-slate-400">Portfolio Agent</p>
            </div>
          </motion.div>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggleCollapse}
          className="text-slate-400 hover:text-slate-200"
        >
          {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          
          return (
            <Button
              key={item.id}
              variant={isActive ? "default" : "ghost"}
              className={`w-full justify-start gap-3 ${
                isActive 
                  ? 'bg-teal-500/20 text-teal-400 border border-teal-500/30' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
              onClick={() => onViewChange(item.id)}
            >
              <Icon size={18} />
              {!isCollapsed && <span>{item.label}</span>}
            </Button>
          );
        })}
      </nav>

      {/* Portfolio Summary */}
      {!isCollapsed && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="p-4 flex-1"
        >
          <Card className="bg-slate-800/50 border-slate-700 p-4 space-y-4">
            <div className="text-center">
              <h3 className="text-sm font-medium text-slate-400 mb-1">Total Portfolio</h3>
              <p className="text-2xl font-bold text-slate-100">
                ${mockPortfolio.totalValue.toLocaleString()}
              </p>
              <div className="flex items-center justify-center gap-1 mt-1">
                <TrendingUp size={14} className="text-green-400" />
                <span className="text-sm text-green-400">+{mockPortfolio.dailyChange}%</span>
              </div>
            </div>

            <div className="space-y-3">
              {mockPortfolio.assets.map((asset) => (
                <div key={asset.name} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-300">{asset.name}</span>
                    <span className="text-slate-400">{asset.percentage}%</span>
                  </div>
                  <Progress 
                    value={asset.percentage} 
                    className="h-2"
                    style={{
                      '--progress-background': asset.color,
                    } as React.CSSProperties}
                  />
                </div>
              ))}
            </div>

            <div className="flex items-center gap-2 pt-2 border-t border-slate-700">
              <Shield size={16} className="text-amber-400" />
              <div className="flex-1">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-300">Risk Score</span>
                  <span className="text-amber-400">{mockPortfolio.riskScore}/10</span>
                </div>
                <Progress value={mockPortfolio.riskScore * 10} className="h-1 mt-1" />
              </div>
            </div>
          </Card>
        </motion.div>
      )}
    </motion.aside>
  );
}