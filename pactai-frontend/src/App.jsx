import { Routes, Route, Navigate } from 'react-router-dom'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import CompleteProfile from './pages/CompleteProfile'
import Settings from './pages/Settings'
import Negotiation from './pages/Negotiation'
import NegotiationHistory from './pages/NegotiationHistory'
import ProposalHistory from './pages/ProposalHistory'
import RecycleBin from './pages/RecycleBin'
import ProposalDetail from './pages/ProposalDetail'
import Integrations from './pages/Integrations'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'

function Protected({ children }) {
  return (
    <ProtectedRoute>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      <Route path="/dashboard" element={<Protected><Dashboard /></Protected>} />
      <Route path="/complete-profile" element={<Protected><CompleteProfile /></Protected>} />
      <Route path="/settings" element={<Protected><Settings /></Protected>} />
      <Route path="/negotiation" element={<Protected><Negotiation /></Protected>} />
      <Route path="/negotiation/:sessionId" element={<Protected><Negotiation /></Protected>} />
      <Route path="/negotiations" element={<Protected><NegotiationHistory /></Protected>} />
      <Route path="/proposals" element={<Protected><ProposalHistory /></Protected>} />
      <Route path="/proposals/recycle-bin" element={<Protected><RecycleBin /></Protected>} />
      <Route path="/proposals/:id" element={<Protected><ProposalDetail /></Protected>} />
      <Route path="/integrations" element={<Protected><Integrations /></Protected>} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
