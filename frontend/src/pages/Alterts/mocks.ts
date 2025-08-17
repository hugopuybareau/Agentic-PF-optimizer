import { Alert } from "./interfaces";

export const mockAlerts: Alert[] = [
    {
      id: '1',
      type: 'risk',
      title: 'High Volatility Detected',
      message: 'Tesla (TSLA) showing increased volatility. Consider reviewing position size.',
      timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 mins ago
      isRead: false,
      severity: 'high'
    },
    {
      id: '2',
      type: 'opportunity',
      title: 'Rebalancing Opportunity',
      message: 'Your tech allocation is 15% over target. Consider taking profits.',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
      isRead: false,
      severity: 'medium'
    },
    {
      id: '3',
      type: 'news',
      title: 'Market Update',
      message: 'Fed meeting minutes released. Potential impact on your bond positions.',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4), // 4 hours ago
      isRead: true,
      severity: 'low'
    },
    {
      id: '4',
      type: 'performance',
      title: 'Portfolio Milestone',
      message: 'Congratulations! Your portfolio hit a new all-time high.',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
      isRead: true,
      severity: 'low'
    },
    {
      id: '5',
      type: 'opportunity',
      title: 'Dividend Alert',
      message: 'Microsoft (MSFT) ex-dividend date approaching. Consider position timing.',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2), // 2 days ago
      isRead: true,
      severity: 'medium'
    }
  ]