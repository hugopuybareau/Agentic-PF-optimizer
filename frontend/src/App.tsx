// frontend/src/App.tsx

import '@/lib/i18n';

import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/hooks/use-theme";
import { AuthProvider } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";

// Pages
import LoginPage from "@/pages/LoginPage";
import Landing from "@/pages/Landing";
import Portfolio from "@/pages/Portfolio";
import Chat from "@/pages/Chat";
import Alerts from "@/pages/Alerts";
import Features from "@/pages/Features";
import NotFound from "@/pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
    <QueryClientProvider client={queryClient}>
        <ThemeProvider defaultTheme="dark" storageKey="platine-ui-theme">
            <AuthProvider>
                <TooltipProvider>
                    <Toaster />
                    <Sonner />
                    <BrowserRouter>
                        <Routes>
                            <Route path="/" element={<LoginPage />} />
                            <Route path="/landing" element={
                                <ProtectedRoute>
                                    <Landing />
                                </ProtectedRoute>
                            } />
                            <Route path="/portfolio" element={
                                <ProtectedRoute>
                                    <Portfolio />
                                </ProtectedRoute>
                            } />
                            <Route path="/chat" element={
                                <ProtectedRoute>
                                    <Chat />
                                </ProtectedRoute>
                            } />
                            <Route path="/alerts" element={
                                <ProtectedRoute>
                                    <Alerts />
                                </ProtectedRoute>
                            } />
                            <Route path="/features" element={
                                <ProtectedRoute>
                                    <Features />
                                </ProtectedRoute>
                            } />
                            <Route path="*" element={<NotFound />} />
                        </Routes>
                    </BrowserRouter>
                </TooltipProvider>
            </AuthProvider>
        </ThemeProvider>
    </QueryClientProvider>
);

export default App;