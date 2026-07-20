import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FileText, ArrowRight, Trash2 } from 'lucide-react'
import { api } from '../lib/api'

const STATUS_STYLES = {
  accepted: 'text-accepted bg-accepted-soft border-accepted/30',
  rejected: 'text-rejected bg-rejected-soft border-rejected/30',
  pending_review: 'text-pending bg-pending-soft border-pending/30',
}

const STATUS_LABELS = {
  accepted: 'accepted',
  rejected: 'rejected',
  pending_review: 'awaiting your review',
}

export default function ProposalHistory() {
  const [proposals, setProposals] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.listProposals().then(setProposals).catch((e) => setError(e.message))
  }, [])

  return (
    <div className="max-w-3xl mx-auto px-10 py-12">
      <p className="font-mono text-xs tracking-widest text-brass-dark uppercase mb-2">Proposal history</p>
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-display text-3xl text-ink">Every deal, on the record</h1>
        <Link to="/proposals/recycle-bin" className="flex items-center gap-1.5 text-xs text-ink/45 hover:text-ink">
          <Trash2 size={13} />
          Recycle bin
        </Link>
      </div>

      {error && <p className="text-sm text-rejected bg-rejected-soft rounded-md px-3 py-2 mb-6">{error}</p>}

      {proposals === null && !error && <p className="text-sm text-ink/40 font-mono">loading ledger…</p>}

      {proposals?.length === 0 && (
        <div className="bg-paper-card border border-paper-line border-dashed rounded-lg p-10 text-center">
          <FileText size={24} className="mx-auto text-ink/30 mb-3" strokeWidth={1.5} />
          <p className="text-sm text-ink/60">No proposals yet.</p>
          <p className="text-xs text-ink/40 mt-1">Start a negotiation and your first one will land here.</p>
        </div>
      )}

      <div className="divide-y divide-paper-line">
        {proposals?.map((p) => (
          <Link
            key={p.id}
            to={`/proposals/${p.id}`}
            className="group flex items-center justify-between py-5 hover:bg-paper-card/60 -mx-4 px-4 rounded-md transition-colors"
          >
            <div>
              <p className="font-display text-lg text-ink">{p.title}</p>
              <p className="text-xs text-ink/45 font-mono mt-1">
                {new Date(p.created_at).toLocaleDateString()}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <span className="font-mono text-sm text-ink/70">${p.agreed_price}</span>
              <span
                className={`px-2.5 py-1 rounded-full border text-[11px] font-mono uppercase tracking-wide -rotate-2 ${
                  STATUS_STYLES[p.status] || STATUS_STYLES.pending_review
                }`}
              >
                {STATUS_LABELS[p.status] || p.status}
              </span>
              <ArrowRight size={15} className="text-ink/30 group-hover:text-brass-dark transition-colors" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
