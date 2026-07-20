import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { api } from '../lib/api'

const AuthContext = createContext(null)
const USER_KEY = 'pactai_user'
const PROFILE_DONE_KEY = 'pactai_profile_done'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [profileComplete, setProfileComplete] = useState(false)
  const [loading, setLoading] = useState(true)

  const loadSession = useCallback(async () => {
    const stored = localStorage.getItem(USER_KEY)
    if (!stored) {
      setLoading(false)
      return
    }
    setUser(JSON.parse(stored))
    await refreshProfile()
    setLoading(false)
  }, [])

  useEffect(() => {
    loadSession()
  }, [loadSession])

  async function refreshProfile() {
    try {
      const p = await api.getProfile()
      setProfile(p)
      // Your /profile endpoint always returns a FreelancerProfile — even before the user has
      // saved one — because every field has a schema default. So "profile exists" can't be
      // detected from the response shape alone. We track completion locally instead: it's set
      // the moment the user actually submits the Complete Profile form.
      setProfileComplete(localStorage.getItem(PROFILE_DONE_KEY) === '1')
    } catch (_) {
      setProfile(null)
      setProfileComplete(false)
    }
  }

  async function login(credentials) {
    const res = await api.login(credentials)
    const loggedInUser = res.user || { email: credentials.email }
    localStorage.setItem(USER_KEY, JSON.stringify(loggedInUser))
    setUser(loggedInUser)
    await refreshProfile()
  }

  async function signup(data) {
    await api.signup(data)
    // signup doesn't return a user object or token today, so we log in immediately after
    // using the same credentials to get a consistent session.
    await login({ email: data.email, password: data.password })
  }

  function logout() {
    localStorage.removeItem(USER_KEY)
    setUser(null)
    setProfile(null)
    setProfileComplete(false)
  }

  function markProfileComplete() {
    localStorage.setItem(PROFILE_DONE_KEY, '1')
    setProfileComplete(true)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        profileComplete,
        loading,
        login,
        signup,
        logout,
        refreshProfile,
        markProfileComplete,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
