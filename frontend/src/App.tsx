import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sidebar } from './components/Sidebar';
import { ChatInterface } from './components/ChatInterface';
import { Portfolio } from './components/Portfolio';
import { AlertsPanel } from './components/AlertsPanel';
import { Settings } from './components/Settings';
import { Toaster } from './components/ui/sonner';

type View = 'chat' | 'portfolio' | 'alerts' | 'settings';

function App() {
  const [currentView, setCurrentView] = useState<View>('chat');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [showAlerts, setShowAlerts] = useState(false);

  const renderMainContent = () => {
    switch (currentView) {
      case 'chat':
        return <ChatInterface />;
      case 'portfolio':
        return <Portfolio />;
      case 'alerts':
        return <AlertsPanel />;
      case 'settings':
        return <Settings />;
      default:
        return <ChatInterface />;
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      <Sidebar
        currentView={currentView}
        onViewChange={setCurrentView}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />
      
      <main className="flex-1 flex flex-col relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentView}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="flex-1 overflow-hidden"
          >
            {renderMainContent()}
          </motion.div>
        </AnimatePresence>
        
        <AnimatePresence>
          {showAlerts && (
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 20, stiffness: 300 }}
              className="absolute top-0 right-0 w-80 h-full bg-slate-900/95 backdrop-blur-xl border-l border-slate-800 z-50"
            >
              <AlertsPanel onClose={() => setShowAlerts(false)} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
      
      <Toaster />
    </div>
  );
}

export default App;