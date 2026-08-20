import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authApi } from '../services/api'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'
import { Trash2 } from 'lucide-react'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await authApi.login(email, password)
      login(res.data.access_token, {
        id: res.data.user_id,
        name: res.data.name,
        email,
        role: res.data.role,
        preferred_language: 'en',
        ward_id: null,
      })
      toast.success(`Welcome back, ${res.data.name}!`)
      if (res.data.role === 'officer' || res.data.role === 'admin') {
        navigate('/municipal')
      } else {
        navigate('/')
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-600 rounded-2xl mb-4">
            <Trash2 size={32} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">SwachhAI Gujarat</h1>
          <p className="text-gray-500 mt-1 text-sm">Agentic AI for Smarter Waste Management</p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Sign in to your account</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="you@example.com"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="••••••••"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-600 text-white py-2.5 rounded-lg font-medium text-sm hover:bg-green-700 disabled:opacity-60 transition-colors"
            >
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <div className="mt-4 text-center text-sm text-gray-500">
            Don't have an account?{' '}
            <Link to="/register" className="text-green-600 font-medium hover:underline">Register</Link>
          </div>

          {/* Demo credentials */}
          <div className="mt-6 p-3 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-800">
            <strong>Demo accounts:</strong><br />
            Admin: admin@swachhai.demo / admin123<br />
            Officer: officer@swachhai.demo / officer123<br />
            Citizen: citizen1@demo.swachhai / citizen123
          </div>
        </div>
      </div>
    </div>
  )
}
