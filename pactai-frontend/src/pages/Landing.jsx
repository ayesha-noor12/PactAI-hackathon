import { Link } from 'react-router-dom'
import { ArrowRight, ScrollText } from 'lucide-react'

const steps = [
  { label: 'Client describes the project', detail: 'Plain language, no forms.' },
  { label: 'PactAI extracts the requirements', detail: 'Scope, platform, features, timeline.' },
  { label: 'It prices the work', detail: 'Against your rate, margin, and hours.' },
  { label: 'It negotiates the terms', detail: 'Holds your floor, finds the close.' },
  { label: 'A proposal is drawn up', detail: 'Ready to send, ready to sign.' },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-ink text-cream">
      {/* Nav */}
      <header className="flex items-center justify-between px-8 py-6 max-w-6xl mx-auto">
        <div className="flex items-center gap-2">
          <ScrollText size={20} className="text-brass-light" strokeWidth={1.75} />
          <span className="font-display italic text-xl">PactAI</span>
        </div>
        <div className="flex items-center gap-6 text-sm">
          <Link to="/login" className="text-cream-dim hover:text-cream transition-colors">
            Log in
          </Link>
          <Link
            to="/signup"
            className="px-4 py-2 rounded-md bg-brass text-ink font-medium hover:bg-brass-light transition-colors"
          >
            Get started
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-8 pt-16 pb-24 grid md:grid-cols-[1.1fr_0.9fr] gap-16 items-center">
        <div>
          <p className="font-mono text-xs tracking-[0.2em] text-brass-light uppercase mb-6">
            For freelancers who hate quoting rates
          </p>
          <h1 className="font-display text-5xl md:text-6xl leading-[1.05] mb-6">
            Let the AI <span className="italic text-brass-light">negotiate</span> while you build.
          </h1>
          <p className="text-cream-dim text-lg leading-relaxed max-w-lg mb-10">
            A client describes a project. PactAI extracts the real scope, prices it against your
            rate and margin, negotiates the terms, and hands you a proposal ready to sign —
            without you writing a single quote.
          </p>
          <div className="flex items-center gap-4">
            <Link
              to="/signup"
              className="group flex items-center gap-2 px-6 py-3 rounded-md bg-brass text-ink font-medium hover:bg-brass-light transition-colors"
            >
              Start negotiating
              <ArrowRight size={16} className="group-hover:translate-x-0.5 transition-transform" />
            </Link>
            <Link to="/login" className="px-6 py-3 text-sm text-cream-dim hover:text-cream transition-colors">
              I already have an account
            </Link>
          </div>
        </div>

        {/* Signature element: a stamped ledger card showing a live negotiation excerpt */}
        <div className="relative">
          <div className="absolute -top-6 -right-6 w-24 h-24 rounded-full border border-brass-light/40 flex items-center justify-center rotate-[-8deg] pointer-events-none">
            <span className="font-mono text-[10px] tracking-widest text-brass-light text-center leading-tight">
              NEGOTIATED
              <br />& CLOSED
            </span>
          </div>
          <div className="bg-ink-soft border border-ink-line rounded-lg p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-ink-line mb-4">
              <span className="font-mono text-xs text-cream-dim">negotiation_#0192</span>
              <span className="font-mono text-xs text-accepted">live</span>
            </div>
            <div className="space-y-3 text-sm">
              <div className="bg-ink rounded-md px-4 py-3 max-w-[85%]">
                <p className="text-cream-dim text-xs mb-1 font-mono">client</p>
                <p>Can you do it for $800? We're a small team.</p>
              </div>
              <div className="bg-brass/15 border border-brass/30 rounded-md px-4 py-3 max-w-[85%] ml-auto">
                <p className="text-brass-light text-xs mb-1 font-mono">pactai</p>
                <p>
                  Given the auth + admin dashboard scope, $800 is below floor. I can hold $1,150
                  with a 2-week timeline, or $950 if we cut the admin dashboard to phase two.
                </p>
              </div>
            </div>
            <div className="ledger-rule mt-5 pt-4 flex items-center justify-between">
              <span className="text-xs text-cream-dim">Your floor stays protected</span>
              <span className="font-mono text-brass-light">$950–$1,150</span>
            </div>
          </div>
        </div>
      </section>

      {/* How it works — a real sequence, so numbering earns its place here */}
      <section className="border-t border-ink-line">
        <div className="max-w-6xl mx-auto px-8 py-20">
          <p className="font-mono text-xs tracking-[0.2em] text-brass-light uppercase mb-10">
            How a deal moves through PactAI
          </p>
          <div className="grid md:grid-cols-5 gap-6">
            {steps.map((step, i) => (
              <div key={step.label} className="relative pt-6">
                <span className="font-display italic text-3xl text-brass-light/70">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <p className="mt-3 font-medium leading-snug">{step.label}</p>
                <p className="mt-1 text-sm text-cream-dim leading-snug">{step.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Closing CTA */}
      <section className="max-w-6xl mx-auto px-8 py-20 text-center border-t border-ink-line">
        <h2 className="font-display text-3xl md:text-4xl italic mb-4">
          Your rate. Held firm. Every time.
        </h2>
        <p className="text-cream-dim mb-8 max-w-md mx-auto">
          Set your floor once. Let PactAI defend it in every conversation after.
        </p>
        <Link
          to="/signup"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-md bg-brass text-ink font-medium hover:bg-brass-light transition-colors"
        >
          Create your account
          <ArrowRight size={16} />
        </Link>
      </section>

      <footer className="border-t border-ink-line px-8 py-6 text-center text-xs text-cream-dim font-mono">
        PactAI — built for the Global AI Hackathon Series
      </footer>
    </div>
  )
}
