import { NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, MessageSquare, MessagesSquare, History, Settings, LogOut, ScrollText, Link2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/negotiation', label: 'New Negotiation', icon: MessageSquare },
  { to: '/negotiations', label: 'Negotiations', icon: MessagesSquare },
  { to: '/proposals', label: 'Proposal History', icon: History },
  { to: '/integrations', label: 'Integrations', icon: Link2 },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex bg-paper text-ink">
      <aside className="w-60 shrink-0 bg-ink text-cream flex flex-col">
        <div className="px-6 py-6 flex items-center gap-2">
          <ScrollText size={20} className="text-brass-light" strokeWidth={1.75} />
          <span className="font-display italic text-lg tracking-tight">PactAI</span>
        </div>

        <nav className="flex-1 px-3 mt-4 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-colors ${
                  isActive
                    ? 'bg-ink-soft text-cream border-l-2 border-brass-light pl-[10px]'
                    : 'text-cream-dim hover:text-cream hover:bg-ink-soft/60'
                }`
              }
            >
              <Icon size={16} strokeWidth={1.75} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-3 pb-6 pt-3 border-t border-ink-line">
          <div className="px-3 py-2 mb-1">
            <p className="text-sm text-cream truncate">{user?.name || user?.email}</p>
            <p className="text-xs text-cream-dim font-mono">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm text-cream-dim hover:text-cream hover:bg-ink-soft/60 transition-colors"
          >
            <LogOut size={16} strokeWidth={1.75} />
            Log out
          </button>
        </div>
      </aside>

      <main className="flex-1 min-w-0">{children}</main>
    </div>
  )
}
