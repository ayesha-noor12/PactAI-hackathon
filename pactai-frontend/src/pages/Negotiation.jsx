import { useEffect, useRef, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { Send, ScrollText, FileCheck2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { api } from '../lib/api'

export default function Negotiation() {
  const { profile } = useAuth()
  const navigate = useNavigate()
  const { sessionId: routeSessionId } = useParams()
  const [sessionId, setSessionId] = useState(routeSessionId || null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [proposalId, setProposalId] = useState(null)
  const [closed, setClosed] = useState(false)
  const [loading, setLoading] = useState(Boolean(routeSessionId))
  const bottomRef = useRef(null)

  // If we landed here without a session id (fresh "Start Negotiation" click), mint one
  // and push it into the URL — this is what makes a negotiation resumable/refreshable
  // instead of silently vanishing the moment you navigate away.
  useEffect(() => {
    if (!routeSessionId) {
      const newId = crypto.randomUUID()
      setSessionId(newId)
      navigate(`/negotiation/${newId}`, { replace: true })
    }
  }, [routeSessionId, navigate])

  useEffect(() => {
    if (!routeSessionId) return

    setLoading(true)
    api
      .getSession(routeSessionId)
      .then((data) => {
        if (data.messages?.length) {
          setMessages(data.messages.map((m) => ({ role: m.role === 'assistant' ? 'assistant' : 'user', content: m.content })))
        } else {
          setMessages([greeting(profile)])
        }
        if (data.proposal_id) setProposalId(data.proposal_id)
        if (data.stage === 'COMPLETED') setClosed(true)
      })
      .catch(() => setMessages([greeting(profile)]))
      .finally(() => setLoading(false))
  }, [routeSessionId]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function greeting(p) {
    return {
      role: 'assistant',
      content: "Hey, I'm PactAI 👋 Tell me a bit about the project that you want to built?",
    }
  }

  async function handleSend(e) {
    e.preventDefault()
    if (!input.trim() || sending || !sessionId) return
    const text = input.trim()
    setInput('')
    setMessages((m) => [...m, { role: 'user', content: text }])
    setSending(true)
    try {
      const res = await api.sendChat(sessionId, text)
      setMessages((m) => [...m, { role: 'assistant', content: res.reply }])
      if (res.proposal_id) setProposalId(res.proposal_id)
      if (res.stage === 'COMPLETED') setClosed(true)
    } catch (err) {
      setMessages((m) => [...m, { role: 'system', content: err.message || 'Message failed to send. Try again.' }])
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-10 py-10 flex flex-col h-screen">
      <div className="mb-6 shrink-0">
        <div className="flex items-center justify-between">
          <p className="font-mono text-xs tracking-widest text-brass-dark uppercase mb-2">Negotiation</p>
          <Link to="/negotiations" className="text-xs text-ink/45 hover:text-ink font-mono">
            past negotiations →
          </Link>
        </div>
        <div className="flex items-center gap-2">
          <ScrollText size={20} className="text-brass" strokeWidth={1.75} />
          <h1 className="font-display text-2xl text-ink">Let's start negotiating with your client</h1>
        </div>
        {profile && (
          <div className="mt-3 flex flex-wrap gap-2 text-xs">
            <Tag>{profile.title}</Tag>
            <Tag>{profile.currency}{profile.hourly_rate}/hr</Tag>
            {profile.skills?.slice(0, 4).map((s) => <Tag key={s}>{s}</Tag>)}
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {loading && <p className="text-sm text-ink/40 font-mono">loading conversation…</p>}
        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} content={m.content} />
        ))}
        {sending && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {proposalId && (
        <Link
          to={`/proposals/${proposalId}`}
          className="shrink-0 mb-4 flex items-center justify-center gap-2 w-full py-3 rounded-md bg-accepted-soft border border-accepted/30 text-accepted font-medium text-sm hover:bg-accepted/10 transition-colors"
        >
          <FileCheck2 size={16} />
          Proposal drafted — review it now
        </Link>
      )}

      {closed ? (
        <p className="shrink-0 text-center text-sm text-ink/45 py-4 border-t border-paper-line">
          This negotiation is closed.{' '}
          <Link to="/negotiation" className="text-brass-dark hover:underline">
            Start a new one
          </Link>
        </p>
      ) : (
        <form onSubmit={handleSend} className="shrink-0 flex gap-2 pt-4 border-t border-paper-line">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe the client's project, or reply to PactAI's question…"
            disabled={sending || loading}
            className="flex-1 px-4 py-3 rounded-md border border-paper-line bg-paper-card text-ink text-sm focus:outline-none focus:ring-2 focus:ring-brass/40 focus:border-brass disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={sending || loading || !input.trim()}
            className="px-4 py-3 rounded-md bg-brass text-ink hover:bg-brass-light transition-colors disabled:opacity-50"
          >
            <Send size={16} />
          </button>
        </form>
      )}
    </div>
  )
}

function Tag({ children }) {
  return (
    <span className="px-2.5 py-1 rounded-full bg-paper-card border border-paper-line text-ink/60 font-mono">
      {children}
    </span>
  )
}

function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-brass/10 border border-brass/25 rounded-md rounded-bl-sm px-4 py-3">
        <p className="text-[11px] font-mono mb-1.5 text-brass-dark">pactai</p>
        <div className="flex gap-1 items-center h-3">
          <span className="w-1.5 h-1.5 rounded-full bg-ink/40 animate-bounce [animation-delay:-0.3s]" />
          <span className="w-1.5 h-1.5 rounded-full bg-ink/40 animate-bounce [animation-delay:-0.15s]" />
          <span className="w-1.5 h-1.5 rounded-full bg-ink/40 animate-bounce" />
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ role, content }) {
  if (role === 'system') {
    return <p className="text-center text-xs text-rejected font-mono">{content}</p>
  }
  const isUser = role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-md px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'bg-ink text-cream rounded-br-sm'
            : 'bg-brass/10 border border-brass/25 text-ink rounded-bl-sm'
        }`}
      >
        <p className={`text-[11px] font-mono mb-1 ${isUser ? 'text-cream-dim' : 'text-brass-dark'}`}>
          {isUser ? 'you (relaying client)' : 'pactai'}
        </p>
        {content}
      </div>
    </div>
  )
}
