import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  Paperclip, 
  Zap, 
  TrendingUp, 
  Newspaper, 
  Bell,
  MessageCircle,
  Bot
} from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Textarea } from './ui/textarea';
import { WolfyAvatar } from './WolfyAvatar';
import { toast } from 'sonner';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'wolfy';
  timestamp: Date;
  type?: 'text' | 'suggestion' | 'analysis';
}

const initialMessages: Message[] = [
  {
    id: '1',
    content: "🐺 Hello! I'm Wolfy, your personal portfolio optimization agent. I'm here to help you make smarter investment decisions. How can I assist you today?",
    sender: 'wolfy',
    timestamp: new Date(),
    type: 'text'
  }
];

const quickActions = [
  { icon: Zap, label: 'Optimize Portfolio', action: 'optimize' },
  { icon: TrendingUp, label: 'Market Analysis', action: 'analyze' },
  { icon: Newspaper, label: 'Latest News', action: 'news' },
  { icon: Bell, label: 'Set Alerts', action: 'alerts' },
];

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate Wolfy's response
    setTimeout(() => {
      const wolfyResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: generateWolfyResponse(inputValue),
        sender: 'wolfy',
        timestamp: new Date(),
        type: 'analysis'
      };
      setMessages(prev => [...prev, wolfyResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const generateWolfyResponse = (input: string): string => {
    const responses = [
      "🐺 I've analyzed your request. Based on current market conditions, I recommend diversifying your holdings across technology and healthcare sectors. Your risk tolerance suggests a balanced approach.",
      "🐺 Great question! Looking at your portfolio, I notice you're overexposed to growth stocks. Consider adding some defensive positions to reduce volatility during market downturns.",
      "🐺 The market data shows interesting trends. Your portfolio is performing well, but there's room for optimization. I suggest rebalancing your asset allocation to capture emerging opportunities.",
      "🐺 I've processed the latest market data for you. Your current strategy aligns well with your goals, but watch out for potential risks in the energy sector. Consider reducing exposure by 3-5%."
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const handleQuickAction = (action: string) => {
    const actionMessages: Record<string, string> = {
      optimize: "Please optimize my portfolio based on current market conditions",
      analyze: "Show me a detailed analysis of my current portfolio performance",
      news: "What's the latest market news that might affect my investments?",
      alerts: "Set up alerts for significant changes in my portfolio"
    };

    setInputValue(actionMessages[action] || '');
  };

  const handleFileUpload = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      toast.success(`File "${file.name}" uploaded successfully! Wolfy is analyzing your portfolio data.`);
      // Simulate file processing
      setTimeout(() => {
        const analysisMessage: Message = {
          id: Date.now().toString(),
          content: `🐺 I've successfully imported your portfolio data from "${file.name}". I can see ${Math.floor(Math.random() * 20 + 10)} holdings with a total value of $${(Math.random() * 500000 + 50000).toLocaleString()}. Would you like me to analyze the risk distribution and suggest optimizations?`,
          sender: 'wolfy',
          timestamp: new Date(),
          type: 'analysis'
        };
        setMessages(prev => [...prev, analysisMessage]);
      }, 2000);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-950 to-slate-900">
      {/* Header */}
      <div className="p-6 border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl">
        <div className="flex items-center gap-4">
          <WolfyAvatar size="md" isActive />
          <div>
            <h2 className="text-xl font-bold text-slate-100">Chat with Wolfy</h2>
            <p className="text-sm text-slate-400">Your AI portfolio optimization assistant</p>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <div className="flex items-center gap-1 text-green-400 text-sm">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              Online
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="p-6 border-b border-slate-800">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Button
                key={action.action}
                variant="outline"
                className="border-slate-700 bg-slate-800/50 hover:bg-slate-700/50 hover:border-teal-500/50 transition-all duration-300"
                onClick={() => handleQuickAction(action.action)}
              >
                <Icon size={16} className="mr-2 text-teal-400" />
                <span className="text-slate-200">{action.label}</span>
              </Button>
            );
          })}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex gap-3 max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                {message.sender === 'wolfy' && (
                  <WolfyAvatar size="sm" isActive />
                )}
                {message.sender === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-teal-500 flex items-center justify-center">
                    <MessageCircle size={16} className="text-slate-900" />
                  </div>
                )}
                <Card className={`p-4 ${
                  message.sender === 'user'
                    ? 'bg-teal-500/20 border-teal-500/30 text-slate-100'
                    : 'bg-slate-800/50 border-slate-700 text-slate-200'
                }`}>
                  <p className="text-sm leading-relaxed">{message.content}</p>
                  <p className="text-xs text-slate-400 mt-2">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </Card>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing Indicator */}
        <AnimatePresence>
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex justify-start"
            >
              <div className="flex gap-3">
                <WolfyAvatar size="sm" isActive />
                <Card className="bg-slate-800/50 border-slate-700 p-4">
                  <div className="flex gap-1">
                    <motion.div
                      animate={{ scale: [1, 1.5, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                      className="w-2 h-2 bg-teal-400 rounded-full"
                    />
                    <motion.div
                      animate={{ scale: [1, 1.5, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                      className="w-2 h-2 bg-teal-400 rounded-full"
                    />
                    <motion.div
                      animate={{ scale: [1, 1.5, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                      className="w-2 h-2 bg-teal-400 rounded-full"
                    />
                  </div>
                </Card>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 border-t border-slate-800 bg-slate-900/50 backdrop-blur-xl">
        <div className="flex gap-3">
          <Button
            variant="outline"
            size="icon"
            className="border-slate-700 bg-slate-800/50 hover:bg-slate-700/50"
            onClick={handleFileUpload}
          >
            <Paperclip size={16} className="text-slate-400" />
          </Button>
          
          <div className="flex-1 relative">
            <Textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask Wolfy about your portfolio..."
              className="min-h-[50px] bg-slate-800/50 border-slate-700 text-slate-200 placeholder-slate-400 resize-none pr-12"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
            />
            <Button
              size="icon"
              className="absolute right-2 bottom-2 bg-teal-500 hover:bg-teal-600"
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isTyping}
            >
              <Send size={16} />
            </Button>
          </div>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.json"
          onChange={handleFileChange}
          className="hidden"
        />
      </div>
    </div>
  );
}