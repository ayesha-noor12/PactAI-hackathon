import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { MessageSquare, ArrowRight } from 'lucide-react'
import { api } from '../lib/api'

const STAGE_LABELS = {
  DISCOVERY: 'gathering requirements',
  WAITING_FOR_CLIENT: 'awaiting client',
  NEGOTIATION: 'negotiating',
  COMPLETED: 'closed',
}

export default function NegotiationHistory() {
  const [sessions, setSessions] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.listSessions().then(setSessions).catch((e) => setError(e.message))
  }, [])

  return (
    <div className="max-w-3xl mx-auto px-10 py-12">
      <div className="flex items-center justify-between mb-2">
        <p className="font-mono text-xs tracking-widest text-brass-dark uppercase">Negotiations</p>
        <Link
          to="/negotiation"
          className="text-xs font-medium text-brass-dark hover:underline"
        >
          + start new
        </Link>
      </div>
      <h1 className="font-display text-3xl text-ink mb-8">Every conversation, kept</h1>

      {error && <p className="text-sm text-rejected bg-rejected-soft rounded-md px-3 py-2 mb-6">{error}</p>}

      {sessions === null && !error && <p className="text-sm text-ink/40 font-mono">loading…</p>}

      {sessions?.length === 0 && (
        <div className="bg-paper-card border border-paper-line border-dashed rounded-lg p-10 text-center">
          <MessageSquare size={24} className="mx-auto text-ink/30 mb-3" strokeWidth={1.5} />
          <p className="text-sm text-ink/60">No negotiations yet.</p>
        </div>
      )}

      <div className="divide-y divide-paper-line">
        {sessions?.map((s) => (
          <Link
            key={s.session_id}
            to={`/negotiation/${s.session_id}`}
            className="group flex items-center justify-between py-5 hover:bg-paper-card/60 -mx-4 px-4 rounded-md transition-colors"
          >
            <div className="min-w-0">
              <p className="font-display text-lg text-ink truncate">{s.label}</p>
              <p className="text-xs text-ink/45 mt-1 truncate max-w-md">
                {s.last_message || 'No messages yet'}
              </p>
            </div>
            <div className="flex items-center gap-4 shrink-0">
              <span className="px-2.5 py-1 rounded-full bg-paper-card border border-paper-line text-[11px] font-mono uppercase tracking-wide text-ink/55">
                {STAGE_LABELS[s.stage] || s.stage}
              </span>
              <ArrowRight size={15} className="text-ink/30 group-hover:text-brass-dark transition-colors" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
