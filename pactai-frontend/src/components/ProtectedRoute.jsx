import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-paper">
        <span className="font-mono text-sm text-ink/50 tracking-wide">loading session…</span>
      </div>
    )
  }

  if (!user) return <Navigate to="/login" replace />

  return children
}
