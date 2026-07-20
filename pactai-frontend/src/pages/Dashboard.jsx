import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { UserRound, MessageSquare, MessagesSquare, History, Settings, ArrowRight } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { api } from '../lib/api'

export default function Dashboard() {
  const { user, profile, profileComplete } = useAuth()
  const [proposalCount, setProposalCount] = useState(null)

  useEffect(() => {
    api.listProposals().then((list) => setProposalCount(list.length)).catch(() => setProposalCount(0))
  }, [])

  // profileComplete is tracked locally (see AuthContext) since /profile always returns a
  // populated FreelancerProfile — even the schema defaults — so there's no way to tell
  // "never saved" apart from "saved" purely from the response.
  const pct = profileComplete ? 100 : 0
  const firstName = (user?.name || profile?.name || 'there').split(' ')[0]

  return (
    <div className="max-w-4xl mx-auto px-10 py-12">
      <p className="font-mono text-xs tracking-widest text-brass-dark uppercase mb-2">Dashboard</p>
      <h1 className="font-display text-3xl text-ink mb-10">Welcome back, {firstName} 👋</h1>

      <div className="grid md:grid-cols-[220px_1fr] gap-8 mb-12">
        {/* Wax-seal style completion stamp */}
        <div className="bg-paper-card border border-paper-line rounded-lg p-6 flex flex-col items-center justify-center text-center">
          <div
            className="stamp-animate w-20 h-20 rounded-full border-2 border-brass flex items-center justify-center mb-3"
            style={{
              background: `conic-gradient(var(--color-brass) ${pct * 3.6}deg, var(--color-paper-line) 0deg)`,
            }}
          >
            <div className="w-[60px] h-[60px] rounded-full bg-paper-card flex items-center justify-center">
              <span className="seal font-medium text-ink text-sm">{pct}%</span>
            </div>
          </div>
          <p className="text-xs text-ink/60 uppercase tracking-wide font-mono">Profile status</p>
        </div>

        {/* Quick actions */}
        <div className="grid sm:grid-cols-2 gap-4">
          {profileComplete ? (
            <QuickAction
              to="/negotiation"
              icon={MessageSquare}
              title="Start Negotiation"
              desc="Bring a client brief and let PactAI take it from there."
              primary
            />
          ) : (
            <QuickAction
              to="/complete-profile"
              icon={UserRound}
              title="Complete Profile"
              desc="Set your rate, skills, and margin — takes two minutes."
              primary
            />
          )}
          <QuickAction
            to="/negotiations"
            icon={MessagesSquare}
            title="Negotiations"
            desc="Every past and in-progress conversation, kept."
          />
          <QuickAction
            to="/proposals"
            icon={History}
            title="Proposal History"
            desc={proposalCount === null ? 'Loading…' : `${proposalCount} proposal${proposalCount === 1 ? '' : 's'} so far`}
          />
          <QuickAction
            to="/settings"
            icon={Settings}
            title="Settings"
            desc="Update your profile, security, or theme."
          />
          {profileComplete && (
            <QuickAction
              to="/complete-profile"
              icon={UserRound}
              title="Edit Profile"
              desc={`${profile?.title || 'Freelancer'} · ${profile?.currency || '$'}${profile?.hourly_rate ?? '—'}/hr`}
            />
          )}
        </div>
      </div>

      <div className="ledger-rule pt-6">
        <p className="text-sm text-ink/50">
          {profileComplete
            ? 'Your profile is loaded. New negotiations will use it automatically — no repeated questions.'
            : 'Finish your profile first so PactAI can negotiate on your actual terms, not guesses.'}
        </p>
      </div>
    </div>
  )
}

function QuickAction({ to, icon: Icon, title, desc, primary }) {
  return (
    <Link
      to={to}
      className={`group relative rounded-lg p-5 border transition-colors ${
        primary
          ? 'bg-ink border-ink text-cream hover:bg-ink-soft'
          : 'bg-paper-card border-paper-line hover:border-brass/40'
      }`}
    >
      <Icon size={18} className={primary ? 'text-brass-light' : 'text-brass-dark'} strokeWidth={1.75} />
      <p className={`mt-3 font-medium text-sm ${primary ? 'text-cream' : 'text-ink'}`}>{title}</p>
      <p className={`mt-1 text-xs ${primary ? 'text-cream-dim' : 'text-ink/55'}`}>{desc}</p>
      <ArrowRight
        size={14}
        className={`absolute top-5 right-5 opacity-0 group-hover:opacity-100 transition-opacity ${
          primary ? 'text-brass-light' : 'text-brass-dark'
        }`}
      />
    </Link>
  )
}
