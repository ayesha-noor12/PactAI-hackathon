import { Link2, Briefcase, Globe } from 'lucide-react'

const PLATFORMS = [
  { name: 'LinkedIn', icon: Link2 },
  { name: 'Upwork', icon: Briefcase },
  { name: 'Fiverr', icon: Globe },
]

export default function Integrations() {
  return (
    <div className="max-w-3xl mx-auto px-10 py-12">
      <p className="font-mono text-xs tracking-widest text-brass-dark uppercase mb-2">Integrations</p>
      <h1 className="font-display text-3xl text-ink mb-2">Connect PactAI to where you work</h1>
      <p className="text-sm text-ink/55 mb-10">
        Bring client conversations from your freelancing profiles straight into PactAI.
      </p>

      <div className="grid sm:grid-cols-3 gap-4">
        {PLATFORMS.map(({ name, icon: Icon }) => (
          <div
            key={name}
            className="bg-paper-card border border-paper-line border-dashed rounded-lg p-6 text-center"
          >
            <Icon size={22} className="mx-auto text-ink/30 mb-3" strokeWidth={1.5} />
            <p className="font-medium text-ink/70 text-sm mb-2">{name}</p>
            <span className="inline-block px-2.5 py-1 rounded-full bg-pending-soft border border-pending/30 text-pending text-[11px] font-mono uppercase tracking-wide">
              Under construction
            </span>
          </div>
        ))}
      </div>

      <p className="text-xs text-ink/40 mt-8">
        Connecting an account will let PactAI pull in client messages from that platform
        automatically — coming soon.
      </p>
    </div>
  )
}
