import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./hooks/useAuth";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AppLayout } from "./components/layout/AppLayout";
import Dashboard from "./pages/Dashboard";
import TestCases from "./pages/TestCases";
import TestPlans from "./pages/TestPlans";
import Execution from "./pages/Execution";
import AIGenerator from "./pages/AIGenerator";
import SelfHealing from "./pages/SelfHealing";
import AIDebug from "./pages/AIDebug";
import Insights from "./pages/Insights";
import APITesting from "./pages/APITesting";
import VisualTesting from "./pages/VisualTesting";
import Security from "./pages/Security";
import Performance from "./pages/Performance";
import Team from "./pages/Team";
import Settings from "./pages/Settings";
import Auth from "./pages/Auth";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/auth" element={<Auth />} />
            <Route path="/*" element={
              <ProtectedRoute>
                <AppLayout>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/test-cases" element={<TestCases />} />
                    <Route path="/test-plans" element={<TestPlans />} />
                    <Route path="/execution" element={<Execution />} />
                    <Route path="/ai-generator" element={<AIGenerator />} />
                    <Route path="/self-healing" element={<SelfHealing />} />
                    <Route path="/ai-debug" element={<AIDebug />} />
                    <Route path="/insights" element={<Insights />} />
                    <Route path="/api-testing" element={<APITesting />} />
                    <Route path="/visual-testing" element={<VisualTesting />} />
                    <Route path="/security" element={<Security />} />
                    <Route path="/performance" element={<Performance />} />
                    <Route path="/team" element={<Team />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="*" element={<NotFound />} />
                  </Routes>
                </AppLayout>
              </ProtectedRoute>
            } />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
