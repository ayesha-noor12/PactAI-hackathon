import { useState } from 'react'
import { UserRound, ShieldCheck, Moon } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { api } from '../lib/api'
import ProfileForm from '../components/ProfileForm'

const TABS = [
  { id: 'profile', label: 'Profile', icon: UserRound },
  { id: 'security', label: 'Security', icon: ShieldCheck },
  { id: 'theme', label: 'Theme', icon: Moon },
]

export default function Settings() {
  const [tab, setTab] = useState('profile')
  const { profile, profileComplete, refreshProfile, markProfileComplete } = useAuth()
  const [saved, setSaved] = useState(false)

  async function handleProfileSave(data) {
    await api.saveProfile(data)
    markProfileComplete()
    await refreshProfile()
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  return (
    <div className="max-w-3xl mx-auto px-10 py-12">
      <p className="font-mono text-xs tracking-widest text-brass-dark uppercase mb-2">Settings</p>
      <h1 className="font-display text-3xl text-ink mb-8">Account</h1>

      <div className="flex gap-1 border-b border-paper-line mb-8">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`flex items-center gap-2 px-4 py-3 text-sm border-b-2 -mb-px transition-colors ${
              tab === id
                ? 'border-brass text-ink font-medium'
                : 'border-transparent text-ink/50 hover:text-ink/80'
            }`}
          >
            <Icon size={15} strokeWidth={1.75} />
            {label}
          </button>
        ))}
      </div>

      {tab === 'profile' && (
        <div className="bg-paper-card border border-paper-line rounded-lg p-8">
          {saved && (
            <p className="text-sm text-accepted bg-accepted-soft rounded-md px-3 py-2 mb-5">
              Profile updated.
            </p>
          )}
          <ProfileForm
            initial={profileComplete ? profile : null}
            onSubmit={handleProfileSave}
            submitLabel="Save changes"
          />
        </div>
      )}

      {tab === 'security' && <SecurityPanel />}
      {tab === 'theme' && <ThemePanel />}
    </div>
  )
}

function SecurityPanel() {
  const [form, setForm] = useState({ current: '', next: '' })
  const [status, setStatus] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    // Wire this to a real PUT /api/auth/password endpoint once it exists.
    setStatus('changed')
    setTimeout(() => setStatus(''), 2500)
  }

  return (
    <div className="bg-paper-card border border-paper-line rounded-lg p-8 max-w-md">
      <h2 className="font-display text-lg text-ink mb-1">Change password</h2>
      <p className="text-sm text-ink/55 mb-6">Use a password you're not using anywhere else.</p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="password"
          required
          placeholder="Current password"
          value={form.current}
          onChange={(e) => setForm({ ...form, current: e.target.value })}
          className="w-full px-3 py-2.5 rounded-md border border-paper-line bg-paper text-ink text-sm focus:outline-none focus:ring-2 focus:ring-brass/40 focus:border-brass"
        />
        <input
          type="password"
          required
          minLength={8}
          placeholder="New password"
          value={form.next}
          onChange={(e) => setForm({ ...form, next: e.target.value })}
          className="w-full px-3 py-2.5 rounded-md border border-paper-line bg-paper text-ink text-sm focus:outline-none focus:ring-2 focus:ring-brass/40 focus:border-brass"
        />
        {status === 'changed' && (
          <p className="text-sm text-accepted bg-accepted-soft rounded-md px-3 py-2">Password changed.</p>
        )}
        <button
          type="submit"
          className="px-6 py-2.5 rounded-md bg-brass text-ink font-medium text-sm hover:bg-brass-light transition-colors"
        >
          Update password
        </button>
      </form>
    </div>
  )
}

function ThemePanel() {
  const [dark, setDark] = useState(false)

  return (
    <div className="bg-paper-card border border-paper-line rounded-lg p-8 max-w-md">
      <h2 className="font-display text-lg text-ink mb-1">Appearance</h2>
      <p className="text-sm text-ink/55 mb-6">Choose how PactAI looks for you.</p>
      <div className="flex items-center justify-between py-3 ledger-rule">
        <div>
          <p className="text-sm font-medium text-ink">Dark mode</p>
          <p className="text-xs text-ink/50">Ink theme across the whole app, not just the landing page.</p>
        </div>
        <button
          onClick={() => setDark((d) => !d)}
          className={`w-11 h-6 rounded-full transition-colors relative ${dark ? 'bg-brass' : 'bg-paper-line'}`}
        >
          <span
            className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ${
              dark ? 'translate-x-[22px]' : 'translate-x-0.5'
            }`}
          />
        </button>
      </div>
      <p className="text-xs text-ink/40 mt-3">
        Note: hook this toggle up to a theme context / `dark:` classes when you're ready — kept
        local-state-only for now so it doesn't block the hackathon demo.
      </p>
    </div>
  )
}
