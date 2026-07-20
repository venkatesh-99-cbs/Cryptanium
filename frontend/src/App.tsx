import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { SecurityProvider, useSecurity } from './context/SecurityContext';
import DashboardLayout from './layouts/DashboardLayout';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Repository from './pages/Repository';
import Scans from './pages/Scans';
import ScanDetails from './pages/ScanDetails';
import Findings from './pages/Findings';
import Reports from './pages/Reports';
import AIAssistant from './pages/AIAssistant';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

// Protected Route Guard
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useSecurity();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

const App: React.FC = () => {
  return (
    <SecurityProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />

          {/* Protected Dashboard Workspace */}
          <Route 
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/repositories" element={<Repository />} />
            <Route path="/scans" element={<Scans />} />
            <Route path="/scans/:id" element={<ScanDetails />} />
            <Route path="/findings" element={<Findings />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/assistant" element={<AIAssistant />} />
            <Route path="/settings" element={<Settings />} />
          </Route>

          {/* Fallbacks */}
          <Route path="/404" element={<NotFound />} />
          <Route path="*" element={<Navigate to="/404" replace />} />
        </Routes>
      </Router>
    </SecurityProvider>
  );
};

export default App;
