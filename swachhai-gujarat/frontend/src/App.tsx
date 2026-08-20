import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from './store/authStore'

// Pages
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'

// Citizen pages
import CitizenHome from './pages/citizen/CitizenHome'
import ReportIssue from './pages/citizen/ReportIssue'
import ChatAssistant from './pages/citizen/ChatAssistant'
import MyComplaints from './pages/citizen/MyComplaints'
import ComplaintTracking from './pages/citizen/ComplaintTracking'
import SegregationGuide from './pages/citizen/SegregationGuide'

// Municipal pages
import MunicipalDashboard from './pages/municipal/MunicipalDashboard'
import LiveComplaints from './pages/municipal/LiveComplaints'
import RouteOptimization from './pages/municipal/RouteOptimization'
import WardAnalytics from './pages/municipal/WardAnalytics'
import AgentMonitor from './pages/municipal/AgentMonitor'

// Shared
import Layout from './components/shared/Layout'
import DemoBanner from './components/shared/DemoBanner'

// Route guard
const ProtectedRoute: React.FC<{ children: React.ReactNode; roles?: string[] }> = ({ children, roles }) => {
  const { isAuthenticated, user } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (roles && user && !roles.includes(user.role)) return <Navigate to="/" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <BrowserRouter>
      <DemoBanner />
      <Toaster position="top-right" />
      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Citizen */}
        <Route path="/" element={<Layout role="citizen" />}>
          <Route index element={<CitizenHome />} />
          <Route path="report" element={<ProtectedRoute><ReportIssue /></ProtectedRoute>} />
          <Route path="chat" element={<ChatAssistant />} />
          <Route path="my-complaints" element={<ProtectedRoute><MyComplaints /></ProtectedRoute>} />
          <Route path="track/:ticketId" element={<ComplaintTracking />} />
          <Route path="segregation" element={<SegregationGuide />} />
        </Route>

        {/* Municipal / Officer */}
        <Route path="/municipal" element={<ProtectedRoute roles={['officer', 'admin']}><Layout role="municipal" /></ProtectedRoute>}>
          <Route index element={<MunicipalDashboard />} />
          <Route path="complaints" element={<LiveComplaints />} />
          <Route path="routes" element={<RouteOptimization />} />
          <Route path="analytics" element={<WardAnalytics />} />
          <Route path="agents" element={<AgentMonitor />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
