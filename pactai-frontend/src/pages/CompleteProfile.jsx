import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { api } from '../lib/api'
import ProfileForm from '../components/ProfileForm'

export default function CompleteProfile() {
  const { profile, profileComplete, refreshProfile, markProfileComplete } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(data) {
    await api.saveProfile(data)
    markProfileComplete()
    await refreshProfile()
    navigate('/dashboard')
  }

  return (
    <div className="max-w-2xl mx-auto px-10 py-12">
      <p className="font-mono text-xs tracking-widest text-brass-dark uppercase mb-2">
        {profileComplete ? 'Edit profile' : 'One-time setup'}
      </p>
      <h1 className="font-display text-3xl text-ink mb-2">
        {profileComplete ? 'Update your terms' : 'Set your terms once'}
      </h1>
      <p className="text-sm text-ink/60 mb-10">
        PactAI negotiates on your behalf using exactly this — your rate, your margin, your
        availability. You won't be asked this again.
      </p>

      <div className="bg-paper-card border border-paper-line rounded-lg p-8">
        <ProfileForm
          initial={profileComplete ? profile : null}
          onSubmit={handleSubmit}
          submitLabel="Save and continue"
        />
      </div>
    </div>
  )
}
