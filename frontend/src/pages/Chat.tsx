import { useState, useRef } from 'react'
import { Navigation } from '@/components/Navigation'

type Message = {
  id: string
  text: string
  isUser: boolean
  timestamp: Date
}

const initialMessages: Message[] = [
  {
    id: '1',
    text: "Hello! I'm platine agent, your AI financial copilot. I can help you analyze your portfolio, get market insights, and optimize your investments. How can I assist you today?",
    isUser: false,
    timestamp: new Date(),
  }
]

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      isUser: true,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: generateAIResponse(inputValue),
        isUser: false,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, aiResponse])
      setIsLoading(false)
    }, 1000)
  }

  const generateAIResponse = (input: string): string => {
    const responses = [
      "Based on your portfolio analysis, I recommend increasing your diversification in the technology sector. Your current allocation shows strong performance but could benefit from some rebalancing.",
      "I've analyzed the latest market trends. There's been increased volatility in your crypto holdings. Consider taking some profits or adjusting your risk exposure.",
      "Your portfolio shows excellent diversification. The S&P 500 ETF position provides good stability. Would you like me to suggest some growth opportunities?",
      "Market sentiment analysis indicates potential opportunities in renewable energy sectors. Your current ESG exposure is minimal - shall I provide some recommendations?",
      "I notice your cash position is quite conservative at 3%. Given current market conditions, this might be optimal for risk management."
    ]
    return responses[Math.floor(Math.random() * responses.length)]
  }

  const handleFileUpload = () => {
    fileInputRef.current?.click()
  }

  const quickActions = [
    { label: 'Analyze Portfolio', action: () => setInputValue('Analyze my current portfolio performance') },
    { label: 'Optimize Allocation', action: () => setInputValue('Suggest portfolio optimization strategies') },
    { label: 'Market News', action: () => setInputValue('What are the latest market trends I should know about?') },
    { label: 'Risk Assessment', action: () => setInputValue('Assess the risk level of my current holdings') },
  ]

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="pt-20 px-6 pb-6">
        <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-hero mb-2">platine agent</h1>
            <p className="text-sub">Your AI financial copilot</p>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto space-y-6 mb-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} animate-fade-in-up`}
              >
                <div className={`max-w-[80%] ${
                  message.isUser 
                    ? 'bg-primary text-primary-foreground' 
                    : 'card-platine'
                } p-4 rounded-lg`}>
                  {!message.isUser && (
                    <div className="flex items-center space-x-2 mb-2">
                      <div className="w-6 h-6 bg-accent rounded-full flex items-center justify-center">
                        <span className="text-xs font-medium">P</span>
                      </div>
                      <span className="text-sub text-xs">platine agent</span>
                    </div>
                  )}
                  <p className="text-nav">{message.text}</p>
                  <span className="text-xs opacity-60 mt-2 block">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start animate-fade-in-up">
                <div className="card-platine p-4 rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <div className="w-6 h-6 bg-accent rounded-full flex items-center justify-center">
                      <span className="text-xs font-medium">P</span>
                    </div>
                    <span className="text-sub text-xs">platine agent</span>
                  </div>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="mb-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {quickActions.map((action) => (
                <button
                  key={action.label}
                  onClick={action.action}
                  className="btn-ghost px-3 py-2 text-xs rounded-lg text-left"
                >
                  {action.label}
                </button>
              ))}
            </div>
          </div>

          {/* Input Area */}
          <div className="card-platine p-4 rounded-lg">
            <div className="flex space-x-4">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask platine agent anything about your portfolio..."
                className="flex-1 bg-transparent border-none outline-none text-nav placeholder:text-muted-foreground"
              />
              
              <div className="flex items-center space-x-2">
                {/* File Upload */}
                <button
                  onClick={handleFileUpload}
                  className="p-2 hover:bg-accent rounded-lg transition-colors"
                  title="Upload CSV or PDF"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                </button>
                
                {/* Send Button */}
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  className="btn-primary px-4 py-2 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Send
                </button>
              </div>
            </div>
            
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.pdf"
              className="hidden"
            />
          </div>
        </div>
      </main>
    </div>
  )
}