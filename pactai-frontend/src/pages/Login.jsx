import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ScrollText } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(form)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Could not log in. Check your details and try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-paper flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-center gap-2 mb-8">
          <ScrollText size={20} className="text-brass" strokeWidth={1.75} />
          <span className="font-display italic text-xl text-ink">PactAI</span>
        </div>

        <div className="bg-paper-card border border-paper-line rounded-lg p-8 shadow-sm">
          <h1 className="font-display text-2xl text-ink mb-1">Welcome back</h1>
          <p className="text-sm text-ink/60 mb-6">Log in to keep negotiating.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-ink/70 mb-1.5">Email</label>
              <input
                type="email"
                required
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full px-3 py-2.5 rounded-md border border-paper-line bg-paper text-ink text-sm focus:outline-none focus:ring-2 focus:ring-brass/40 focus:border-brass"
                placeholder="you@studio.com"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-ink/70 mb-1.5">Password</label>
              <input
                type="password"
                required
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="w-full px-3 py-2.5 rounded-md border border-paper-line bg-paper text-ink text-sm focus:outline-none focus:ring-2 focus:ring-brass/40 focus:border-brass"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <p className="text-sm text-rejected bg-rejected-soft rounded-md px-3 py-2">{error}</p>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 rounded-md bg-brass text-ink font-medium text-sm hover:bg-brass-light transition-colors disabled:opacity-60"
            >
              {submitting ? 'Logging in…' : 'Log in'}
            </button>
          </form>
        </div>

        <p className="text-center text-sm text-ink/60 mt-6">
          New to PactAI?{' '}
          <Link to="/signup" className="text-brass-dark font-medium hover:underline">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  )
}
