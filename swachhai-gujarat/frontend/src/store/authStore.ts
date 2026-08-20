import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, AuthState } from '../types'

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: (token: string, user: User) => {
        localStorage.setItem('swachhai_token', token)
        set({ token, user, isAuthenticated: true })
      },

      logout: () => {
        localStorage.removeItem('swachhai_token')
        localStorage.removeItem('swachhai_user')
        set({ token: null, user: null, isAuthenticated: false })
      },
    }),
    {
      name: 'swachhai_auth',
      partialize: (state) => ({ token: state.token, user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)
