export type Alert = {
    id: string
    type: 'risk' | 'opportunity' | 'news' | 'performance'
    title: string
    message: string
    timestamp: Date
    isRead: boolean
    severity: 'low' | 'medium' | 'high'
  }