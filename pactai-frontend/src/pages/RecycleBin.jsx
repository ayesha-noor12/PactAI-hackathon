import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Trash2, ArrowLeft } from 'lucide-react'
import { api } from '../lib/api'

export default function RecycleBin() {
  const [proposals, setProposals] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.listRejectedProposals().then(setProposals).catch((e) => setError(e.message))
  }, [])

  return (
    <div className="max-w-3xl mx-auto px-10 py-12">
      <Link to="/proposals" className="inline-flex items-center gap-1.5 text-sm text-ink/50 hover:text-ink mb-6">
        <ArrowLeft size={14} />
        Back to proposal history
      </Link>

      <p className="font-mono text-xs tracking-widest text-brass-dark uppercase mb-2">Recycle bin</p>
      <h1 className="font-display text-3xl text-ink mb-8">Rejected proposals</h1>

      {error && <p className="text-sm text-rejected bg-rejected-soft rounded-md px-3 py-2 mb-6">{error}</p>}

      {proposals === null && !error && <p className="text-sm text-ink/40 font-mono">loading…</p>}

      {proposals?.length === 0 && (
        <div className="bg-paper-card border border-paper-line border-dashed rounded-lg p-10 text-center">
          <Trash2 size={24} className="mx-auto text-ink/30 mb-3" strokeWidth={1.5} />
          <p className="text-sm text-ink/60">Nothing here.</p>
          <p className="text-xs text-ink/40 mt-1">Rejected proposals will show up in this list.</p>
        </div>
      )}

      <div className="divide-y divide-paper-line">
        {proposals?.map((p) => (
          <Link
            key={p.id}
            to={`/proposals/${p.id}`}
            className="group flex items-center justify-between py-5 hover:bg-paper-card/60 -mx-4 px-4 rounded-md transition-colors opacity-70 hover:opacity-100"
          >
            <div>
              <p className="font-display text-lg text-ink line-through decoration-ink/30">{p.title}</p>
              <p className="text-xs text-ink/45 font-mono mt-1">
                {new Date(p.created_at).toLocaleDateString()}
              </p>
            </div>
            <span className="font-mono text-sm text-ink/50">${p.agreed_price}</span>
          </Link>
        ))}
      </div>
    </div>
  )
}
