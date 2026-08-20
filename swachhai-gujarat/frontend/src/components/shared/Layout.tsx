import React from 'react'
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { Trash2, Home, MessageSquare, ClipboardList, Recycle, BarChart2, MapPin, Route, Activity, LogOut, Menu, X } from 'lucide-react'
import clsx from 'clsx'

interface LayoutProps {
  role: 'citizen' | 'municipal'
}

const citizenNav = [
  { to: '/', icon: Home, label: 'Home' },
  { to: '/report', icon: ClipboardList, label: 'Report Issue' },
  { to: '/chat', icon: MessageSquare, label: 'Chat Assistant' },
  { to: '/my-complaints', icon: Trash2, label: 'My Complaints' },
  { to: '/segregation', icon: Recycle, label: 'Segregation Guide' },
]

const municipalNav = [
  { to: '/municipal', icon: BarChart2, label: 'Dashboard' },
  { to: '/municipal/complaints', icon: ClipboardList, label: 'Live Complaints' },
  { to: '/municipal/routes', icon: Route, label: 'Route Optimization' },
  { to: '/municipal/analytics', icon: MapPin, label: 'Ward Analytics' },
  { to: '/municipal/agents', icon: Activity, label: 'Agent Monitor' },
]

export default function Layout({ role }: LayoutProps) {
  const { user, logout, isAuthenticated } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = React.useState(false)

  const nav = role === 'citizen' ? citizenNav : municipalNav

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className={clsx(
        'fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 flex flex-col transform transition-transform duration-200',
        mobileOpen ? 'translate-x-0' : '-translate-x-full',
        'lg:translate-x-0 lg:static lg:flex'
      )}>
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-100">
          <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
            <Trash2 size={18} className="text-white" />
          </div>
          <div>
            <div className="font-bold text-gray-900 text-sm leading-tight">SwachhAI Gujarat</div>
            <div className="text-xs text-gray-500">{role === 'citizen' ? 'Citizen Portal' : 'Municipal Dashboard'}</div>
          </div>
        </div>

        {/* Nav links */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {nav.map(({ to, icon: Icon, label }) => {
            const active = location.pathname === to
            return (
              <Link
                key={to}
                to={to}
                onClick={() => setMobileOpen(false)}
                className={clsx(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  active
                    ? 'bg-green-50 text-green-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )}
              >
                <Icon size={18} />
                {label}
              </Link>
            )
          })}

          {/* Switch portal */}
          {role === 'citizen' && user && (user.role === 'officer' || user.role === 'admin') && (
            <Link to="/municipal" className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-blue-600 hover:bg-blue-50 mt-4">
              <BarChart2 size={18} />
              Municipal Portal
            </Link>
          )}
          {role === 'municipal' && (
            <Link to="/" className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-blue-600 hover:bg-blue-50 mt-4">
              <Home size={18} />
              Citizen Portal
            </Link>
          )}
        </nav>

        {/* User section */}
        <div className="border-t border-gray-100 p-4">
          {isAuthenticated && user ? (
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-gray-900">{user.name}</div>
                <div className="text-xs text-gray-500 capitalize">{user.role}</div>
              </div>
              <button onClick={handleLogout} className="p-2 text-gray-400 hover:text-red-500 rounded-lg">
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <Link to="/login" className="block text-center text-sm font-medium text-green-600 hover:text-green-700">
              Sign In
            </Link>
          )}
        </div>
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 bg-black/40 lg:hidden" onClick={() => setMobileOpen(false)} />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Mobile header */}
        <header className="lg:hidden flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200">
          <button onClick={() => setMobileOpen(true)} className="p-2 text-gray-500">
            <Menu size={20} />
          </button>
          <span className="font-semibold text-gray-900 text-sm">SwachhAI Gujarat</span>
          <div className="w-9" />
        </header>

        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
