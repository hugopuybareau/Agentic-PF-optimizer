import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Navigation } from '@/components/Navigation'
import { mockAlerts } from './mocks'
import { Alert } from './interfaces'
import { formatTimestamp, getAlertIcon, getSeverityColor } from './utils'

export default function Alerts() {
  const { t } = useTranslation()
  const [alerts, setAlerts] = useState<Alert[]>(mockAlerts)
  const [filter, setFilter] = useState<'all' | 'unread' | 'risk' | 'opportunity'>('all')

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
              {t('alerts.alertsAndNotifications')}
              {unreadCount > 0 && (
                <span className="ml-3 bg-destructive text-destructive-foreground px-2 py-1 rounded-full text-sm font-medium">
                  {unreadCount}
                </span>
              )}
            </h1>
            <p className="text-sub">{t('alerts.stayInformed')}</p>
          </div>

          {/* Filters */}
          <div className="flex space-x-2 mb-6">
            {[
              { key: 'all', label: t('alerts.all') },
              { key: 'unread', label: t('alerts.unread') },
              { key: 'risk', label: t('alerts.risks') },
              { key: 'opportunity', label: t('alerts.opportunities') }
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
              <div className="card-silver p-8 rounded-lg text-center">
                <svg className="w-12 h-12 text-muted-foreground mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5l-5-5h5v-5a4 4 0 00-8 0v5h5l-5 5l-5-5h5V7a9 9 0 0118 0v10z" />
                </svg>
                <h3 className="text-nav font-medium mb-2">{t('alerts.noAlertsFound')}</h3>
                <p className="text-sub">{t('alerts.allCaughtUp')}</p>
              </div>
            ) : (
              filteredAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`card-silver p-6 rounded-lg border-l-4 transition-all hover:shadow-elevation ${
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
                      title={t('alerts.dismiss')}
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
          <div className="mt-12 card-silver p-6 rounded-lg">
            <h2 className="text-nav font-medium mb-4">{t('alerts.alertPreferences')}</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-nav">{t('alerts.riskAlerts')}</h3>
                  <p className="text-sub text-xs">{t('alerts.riskAlertsDescription')}</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" defaultChecked className="sr-only peer" />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                </label>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-nav">{t('alerts.opportunityAlerts')}</h3>
                  <p className="text-sub text-xs">{t('alerts.opportunityAlertsDescription')}</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" defaultChecked className="sr-only peer" />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                </label>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-nav">{t('alerts.marketNews')}</h3>
                  <p className="text-sub text-xs">{t('alerts.marketNewsDescription')}</p>
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