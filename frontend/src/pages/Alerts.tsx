import { useState } from 'react'
import { Navigation } from '@/components/Navigation'

type Alert = {
  id: string
  type: 'risk' | 'opportunity' | 'news' | 'performance'
  title: string
  message: string
  timestamp: Date
  isRead: boolean
  severity: 'low' | 'medium' | 'high'
}

const mockAlerts: Alert[] = [
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

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>(mockAlerts)
  const [filter, setFilter] = useState<'all' | 'unread' | 'risk' | 'opportunity'>('all')

  const getAlertIcon = (type: Alert['type']) => {
    switch (type) {
      case 'risk':
        return (
          <svg className="w-5 h-5 text-destructive" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.962-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        )
      case 'opportunity':
        return (
          <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        )
      case 'news':
        return (
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9.5a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
        )
      case 'performance':
        return (
          <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
          </svg>
        )
    }
  }

  const getSeverityColor = (severity: Alert['severity']) => {
    switch (severity) {
      case 'high': return 'border-l-destructive bg-destructive/5'
      case 'medium': return 'border-l-orange-500 bg-orange-500/5'
      case 'low': return 'border-l-blue-500 bg-blue-500/5'
    }
  }

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date()
    const diff = now.getTime() - timestamp.getTime()
    const minutes = Math.floor(diff / (1000 * 60))
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days > 0) return `${days}d ago`
    if (hours > 0) return `${hours}h ago`
    if (minutes > 0) return `${minutes}m ago`
    return 'Just now'
  }

  const dismissAlert = (id: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id))
  }

  const markAsRead = (id: string) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === id ? { ...alert, isRead: true } : alert
    ))
  }

  const filteredAlerts = alerts.filter(alert => {
    switch (filter) {
      case 'unread': return !alert.isRead
      case 'risk': return alert.type === 'risk'
      case 'opportunity': return alert.type === 'opportunity'
      default: return true
    }
  })

  const unreadCount = alerts.filter(alert => !alert.isRead).length

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="pt-20 px-6 pb-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-hero mb-2">
              Alerts & Notifications
              {unreadCount > 0 && (
                <span className="ml-3 bg-destructive text-destructive-foreground px-2 py-1 rounded-full text-sm font-medium">
                  {unreadCount}
                </span>
              )}
            </h1>
            <p className="text-sub">Stay informed about your portfolio and market opportunities</p>
          </div>

          {/* Filters */}
          <div className="flex space-x-2 mb-6">
            {[
              { key: 'all', label: 'All' },
              { key: 'unread', label: 'Unread' },
              { key: 'risk', label: 'Risks' },
              { key: 'opportunity', label: 'Opportunities' }
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setFilter(key as typeof filter)}
                className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                  filter === key 
                    ? 'bg-primary text-primary-foreground' 
                    : 'btn-ghost'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Alerts List */}
          <div className="space-y-4">
            {filteredAlerts.length === 0 ? (
              <div className="card-platine p-8 rounded-lg text-center">
                <svg className="w-12 h-12 text-muted-foreground mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5l-5-5h5v-5a4 4 0 00-8 0v5h5l-5 5l-5-5h5V7a9 9 0 0118 0v10z" />
                </svg>
                <h3 className="text-nav font-medium mb-2">No alerts found</h3>
                <p className="text-sub">You're all caught up! No {filter !== 'all' ? filter : ''} alerts at this time.</p>
              </div>
            ) : (
              filteredAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`card-platine p-6 rounded-lg border-l-4 transition-all hover:shadow-elevation ${
                    getSeverityColor(alert.severity)
                  } ${!alert.isRead ? 'ring-1 ring-primary/20' : ''}`}
                  onClick={() => !alert.isRead && markAsRead(alert.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4 flex-1">
                      <div className="mt-1">
                        {getAlertIcon(alert.type)}
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <h3 className={`text-nav font-medium ${!alert.isRead ? 'text-primary' : ''}`}>
                            {alert.title}
                          </h3>
                          {!alert.isRead && (
                            <div className="w-2 h-2 bg-primary rounded-full"></div>
                          )}
                        </div>
                        <p className="text-sub mb-2">{alert.message}</p>
                        <span className="text-xs text-muted-foreground">
                          {formatTimestamp(alert.timestamp)}
                        </span>
                      </div>
                    </div>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        dismissAlert(alert.id)
                      }}
                      className="ml-4 p-1 hover:bg-accent rounded transition-colors"
                      title="Dismiss"
                    >
                      <svg className="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Alert Settings */}
          <div className="mt-12 card-platine p-6 rounded-lg">
            <h2 className="text-nav font-medium mb-4">Alert Preferences</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-nav">Risk Alerts</h3>
                  <p className="text-sub text-xs">Get notified about portfolio risks and volatility</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" defaultChecked className="sr-only peer" />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                </label>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-nav">Opportunity Alerts</h3>
                  <p className="text-sub text-xs">Receive investment opportunities and optimization tips</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" defaultChecked className="sr-only peer" />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                </label>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-nav">Market News</h3>
                  <p className="text-sub text-xs">Stay updated with relevant market developments</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" defaultChecked className="sr-only peer" />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                </label>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}