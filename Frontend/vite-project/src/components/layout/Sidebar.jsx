import { NavLink } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import './Sidebar.css'

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: '📊' },
  { path: '/settlement', label: 'Settlement Predictor', icon: '🎯' },
  { path: '/negotiation', label: 'Negotiation Email', icon: '✉️' },
  { path: '/rights', label: 'Know Your Rights', icon: '⚖️' },
  { path: '/history', label: 'History', icon: '📜' },
]

export default function Sidebar() {
  const { user, logout } = useAuth()

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="sidebar-logo">💰</span>
        <div>
          <strong>DebtRelief AI</strong>
          <span className="sidebar-tagline">Financial Recovery</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map(({ path, label, icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
          >
            <span className="sidebar-link-icon">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        {user && (
          <div className="sidebar-user">
            <span className="sidebar-avatar">{user.name?.charAt(0)?.toUpperCase() || 'U'}</span>
            <div className="sidebar-user-info">
              <span className="sidebar-user-name">{user.name}</span>
              <span className="sidebar-user-email">{user.email}</span>
            </div>
          </div>
        )}
        <button type="button" className="sidebar-logout" onClick={logout}>
          Sign Out
        </button>
      </div>
    </aside>
  )
}
