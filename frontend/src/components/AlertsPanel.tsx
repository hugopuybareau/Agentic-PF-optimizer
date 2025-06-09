import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Bell, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Info,
  CheckCircle2,
  Plus,
  Settings
} from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { WolfyAvatar } from './WolfyAvatar';

interface Alert {
  id: string;
  type: 'info' | 'warning' | 'success' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  isRead: boolean;
  actionable?: boolean;
}

const mockAlerts: Alert[] = [
  {
    id: '1',
    type: 'warning',
    title: 'Portfolio Risk Alert',
    message: 'Your portfolio risk score has increased to 7.2/10. Consider rebalancing to reduce exposure to volatile assets.',
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    isRead: false,
    actionable: true
  },
  {
    id: '2',
    type: 'success',
    title: 'Optimization Completed',
    message: 'Your portfolio has been successfully optimized. Expected annual return increased by 2.3%.',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    isRead: false,
    actionable: false
  },
  {
    id: '3',
    type: 'info',
    title: 'Market News Update',
    message: 'Fed announces interest rate decision. This may impact your bond holdings. Wolfy recommends monitoring closely.',
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
    isRead: true,
    actionable: true
  },
  {
    id: '4',
    type: 'error',
    title: 'Asset Performance Alert',
    message: 'TSLA has declined 8% today. Consider reviewing your position size or setting a stop-loss.',
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
    isRead: true,
    actionable: true
  }
];

interface AlertsPanelProps {
  onClose?: () => void;
}

export function AlertsPanel({ onClose }: AlertsPanelProps) {
  const [alerts, setAlerts] = useState<Alert[]>(mockAlerts);
  const [filter, setFilter] = useState<'all' | 'unread' | 'actionable'>('all');

  const markAsRead = (alertId: string) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId ? { ...alert, isRead: true } : alert
      )
    );
  };

  const dismissAlert = (alertId: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const getAlertIcon = (type: Alert['type']) => {
    switch (type) {
      case 'info':
        return <Info size={20} className="text-blue-400" />;
      case 'warning':
        return <AlertTriangle size={20} className="text-amber-400" />;
      case 'success':
        return <CheckCircle2 size={20} className="text-green-400" />;
      case 'error':
        return <TrendingDown size={20} className="text-red-400" />;
      default:
        return <Bell size={20} className="text-slate-400" />;
    }
  };

  const getAlertBadgeColor = (type: Alert['type']) => {
    switch (type) {
      case 'info':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'warning':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'success':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'error':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      default:
        return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  const filteredAlerts = alerts.filter(alert => {
    switch (filter) {
      case 'unread':
        return !alert.isRead;
      case 'actionable':
        return alert.actionable;
      default:
        return true;
    }
  });

  const unreadCount = alerts.filter(alert => !alert.isRead).length;

  return (
    <div className="h-full flex flex-col bg-slate-900/95 backdrop-blur-xl">
      {/* Header */}
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Bell className="text-teal-400" size={24} />
            <div>
              <h2 className="text-xl font-bold text-slate-100">Alerts</h2>
              {unreadCount > 0 && (
                <p className="text-sm text-slate-400">{unreadCount} unread</p>
              )}
            </div>
          </div>
          {onClose && (
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X size={20} />
            </Button>
          )}
        </div>

        {/* Filter Buttons */}
        <div className="flex gap-2">
          {(['all', 'unread', 'actionable'] as const).map((filterOption) => (
            <Button
              key={filterOption}
              variant={filter === filterOption ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter(filterOption)}
              className={filter === filterOption 
                ? "bg-teal-500/20 border-teal-500/30 text-teal-400" 
                : "border-slate-700 text-slate-400"
              }
            >
              {filterOption.charAt(0).toUpperCase() + filterOption.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {/* Alerts List */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        <AnimatePresence>
          {filteredAlerts.map((alert, index) => (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, x: 300 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 300 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card 
                className={`p-4 border cursor-pointer transition-all duration-300 ${
                  alert.isRead 
                    ? 'bg-slate-800/30 border-slate-700' 
                    : 'bg-slate-800/70 border-slate-600 shadow-lg'
                }`}
                onClick={() => markAsRead(alert.id)}
              >
                <div className="flex gap-3">
                  <div className="flex-shrink-0 mt-1">
                    {getAlertIcon(alert.type)}
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="flex items-start justify-between">
                      <h3 className={`font-medium ${alert.isRead ? 'text-slate-300' : 'text-slate-100'}`}>
                        {alert.title}
                      </h3>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          dismissAlert(alert.id);
                        }}
                        className="text-slate-400 hover:text-slate-200 h-6 w-6 p-0"
                      >
                        <X size={14} />
                      </Button>
                    </div>
                    
                    <p className={`text-sm ${alert.isRead ? 'text-slate-400' : 'text-slate-300'}`}>
                      {alert.message}
                    </p>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Badge className={getAlertBadgeColor(alert.type)}>
                          {alert.type}
                        </Badge>
                        {alert.actionable && (
                          <Badge variant="outline" className="border-teal-500/30 text-teal-400">
                            Actionable
                          </Badge>
                        )}
                      </div>
                      <span className="text-xs text-slate-500">
                        {alert.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    
                    {alert.actionable && !alert.isRead && (
                      <div className="flex gap-2 mt-3">
                        <Button size="sm" className="bg-teal-500/20 text-teal-400 border border-teal-500/30 hover:bg-teal-500/30">
                          Take Action
                        </Button>
                        <Button variant="outline" size="sm" className="border-slate-600 text-slate-400">
                          Learn More
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </AnimatePresence>

        {filteredAlerts.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <WolfyAvatar size="lg" className="mx-auto mb-4" />
            <p className="text-slate-400 mb-2">No alerts to show</p>
            <p className="text-sm text-slate-500">
              {filter === 'all' 
                ? "You're all caught up! I'll notify you when something important happens."
                : `No ${filter} alerts at the moment.`
              }
            </p>
          </motion.div>
        )}
      </div>

      {/* Footer */}
      <div className="p-6 border-t border-slate-800">
        <div className="flex gap-3">
          <Button variant="outline" className="flex-1 border-slate-700 bg-slate-800/50">
            <Plus size={16} className="mr-2" />
            Create Alert
          </Button>
          <Button variant="outline" size="icon" className="border-slate-700 bg-slate-800/50">
            <Settings size={16} />
          </Button>
        </div>
      </div>
    </div>
  );
}