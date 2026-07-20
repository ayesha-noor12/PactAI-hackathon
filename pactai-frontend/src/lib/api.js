// Thin fetch wrapper around your FastAPI backend.
// Vite proxies /api/* to http://localhost:8000 and strips the /api prefix — see vite.config.js.
//
// Real route paths (confirmed from your main.py routers, no /auth or /api prefix on the backend
// itself): /signup, /login, /chat, /profile.

const BASE = '/api'
const USER_KEY = 'pactai_user'

// This is what makes profile/sessions/proposals stop crossing between accounts: every
// request (other than signup/login themselves) sends the logged-in user's email, and
// the backend scopes all data to it (see app/api/deps.py — get_current_user_email).
// NOTE: this is not secure authentication, just identity — see the backend note for
// why that's an acceptable tradeoff for now and what to replace it with later.
function getCurrentUserEmail() {
  try {
    const stored = localStorage.getItem(USER_KEY)
    return stored ? JSON.parse(stored).email : null
  } catch (_) {
    return null
  }
}

async function request(path, { method = 'GET', body, includeUser = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }

  if (includeUser) {
    const email = getCurrentUserEmail()
    if (email) headers['X-User-Email'] = email
  }

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    let detail = 'Something went wrong'
    try {
      const errBody = await res.json()
      detail = errBody.detail || errBody.message || detail
    } catch (_) {}
    throw new Error(detail)
  }

  const text = await res.text()
  return text ? JSON.parse(text) : null
}

export const api = {
  // --- Auth (backend returns no token today; no user identity to send yet) ---
  signup: (data) => request('/signup', { method: 'POST', body: data, includeUser: false }),
  login: (data) => request('/login', { method: 'POST', body: data, includeUser: false }),

  // --- Profile: GET/POST /profile, matches app/schemas/freelancer.py ---
  getProfile: () => request('/profile'),
  saveProfile: (data) => request('/profile', { method: 'POST', body: data }),

  // --- Chat: single POST /chat, matches app/schemas/chat.py ---
  sendChat: (sessionId, message) =>
    request('/chat', { method: 'POST', body: { session_id: sessionId, message } }),

  // --- Proposals: real backend persistence now (app/agent/proposal_store.py) ---
  listProposals: () => request('/proposals'),
  listRejectedProposals: () => request('/proposals/rejected'),
  getProposal: (id) => request(`/proposals/${id}`),
  acceptProposal: (id) => request(`/proposals/${id}/accept`, { method: 'POST' }),
  rejectProposal: (id) => request(`/proposals/${id}/reject`, { method: 'POST' }),

  // --- Sessions: past + in-progress negotiations (app/agent/session_manager.py) ---
  listSessions: () => request('/sessions'),
  getSession: (sessionId) => request(`/sessions/${sessionId}`),
}