import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Check, X } from 'lucide-react'
import { api } from '../lib/api'

const STATUS_STYLES = {
  accepted: 'text-accepted bg-accepted-soft border-accepted/30',
  rejected: 'text-rejected bg-rejected-soft border-rejected/30',
  pending_review: 'text-pending bg-pending-soft border-pending/30',
}

export default function ProposalDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [proposal, setProposal] = useState(null)
  const [error, setError] = useState('')
  const [acting, setActing] = useState(false)

  useEffect(() => {
    load()
  }, [id])

  function load() {
    api.getProposal(id).then(setProposal).catch((e) => setError(e.message))
  }

  async function handleAccept() {
    setActing(true)
    try {
      const updated = await api.acceptProposal(id)
      setProposal(updated)
    } catch (e) {
      setError(e.message)
    } finally {
      setActing(false)
    }
  }

  async function handleReject() {
    setActing(true)
    try {
      await api.rejectProposal(id)
      // Rejected proposals move to the recycle bin and drop out of the main list —
      // send the freelancer back to the (now-filtered) history.
      navigate('/proposals')
    } catch (e) {
      setError(e.message)
      setActing(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-10 py-12">
      <Link to="/proposals" className="inline-flex items-center gap-1.5 text-sm text-ink/50 hover:text-ink mb-8">
        <ArrowLeft size={14} />
        Back to proposal history
      </Link>

      {error && <p className="text-sm text-rejected bg-rejected-soft rounded-md px-3 py-2 mb-6">{error}</p>}

      {!proposal && !error && <p className="text-sm text-ink/40 font-mono">loading proposal…</p>}

      {proposal && (
        <div className="bg-paper-card border border-paper-line rounded-lg p-8">
          <div className="flex items-start justify-between mb-6">
            <div>
              <p className="font-mono text-xs text-ink/40 mb-1">
                {new Date(proposal.created_at).toLocaleDateString()}
              </p>
              <h1 className="font-display text-2xl text-ink">{proposal.title}</h1>
            </div>
            <span
              className={`px-3 py-1 rounded-full border text-xs font-mono uppercase tracking-wide -rotate-2 ${
                STATUS_STYLES[proposal.status] || STATUS_STYLES.pending_review
              }`}
            >
              {proposal.status.replace('_', ' ')}
            </span>
          </div>

          <div className="ledger-rule pt-5 grid grid-cols-2 gap-4 mb-6">
            <div>
              <p className="text-xs text-ink/45 mb-1">Agreed amount</p>
              <p className="font-mono text-lg text-ink">${proposal.agreed_price}</p>
            </div>
            <div>
              <p className="text-xs text-ink/45 mb-1">Timeline</p>
              <p className="font-mono text-lg text-ink">
                {proposal.timeline_days ? `${proposal.timeline_days} days` : '—'}
              </p>
            </div>
          </div>

          <div className="ledger-rule pt-5 mb-6">
            <p className="text-xs text-ink/45 mb-2">Full proposal</p>
            <pre className="text-sm text-ink/80 leading-relaxed whitespace-pre-wrap font-mono bg-paper rounded-md p-4 border border-paper-line">
              {proposal.proposal_text}
            </pre>
          </div>

          {proposal.status === 'pending_review' && (
            <div className="ledger-rule pt-5 flex gap-3">
              <button
                onClick={handleAccept}
                disabled={acting}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-md bg-accepted text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                <Check size={16} />
                Accept
              </button>
              <button
                onClick={handleReject}
                disabled={acting}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-md bg-rejected-soft border border-rejected/30 text-rejected text-sm font-medium hover:bg-rejected/10 transition-colors disabled:opacity-50"
              >
                <X size={16} />
                Reject
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
