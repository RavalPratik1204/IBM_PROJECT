import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('swachhai_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('swachhai_token')
      localStorage.removeItem('swachhai_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (data: object) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
}

// ── Complaints ────────────────────────────────────────────────────────────
export const complaintsApi = {
  submit: (data: object) => api.post('/complaints', data),
  list: (params?: object) => api.get('/complaints', { params }),
  my: () => api.get('/complaints/my'),
  get: (ticketId: string) => api.get(`/complaints/${ticketId}`),
  update: (id: number, data: object) => api.patch(`/complaints/${id}`, data),
}

// ── Agents ────────────────────────────────────────────────────────────────
export const agentsApi = {
  chat: (message: string, language: string, history: object[]) =>
    api.post('/agents/chat', { message, language, history }),
  segregation: (question: string, language: string) =>
    api.post('/agents/segregation', { question, language }),
  optimizeRoute: (ward_id: number, min_fill_pct = 40) =>
    api.post('/agents/optimize-route', { ward_id, min_fill_pct }),
  logs: (params?: object) => api.get('/agents/logs', { params }),
}

// ── Analytics ─────────────────────────────────────────────────────────────
export const analyticsApi = {
  overview: () => api.get('/analytics/overview'),
  byWard: () => api.get('/analytics/by-ward'),
  byCategory: () => api.get('/analytics/by-category'),
  dailyTrend: (days = 14) => api.get('/analytics/daily-trend', { params: { days } }),
  wardPerformance: () => api.get('/analytics/ward-performance'),
  aiProviders: () => api.get('/analytics/ai-providers'),
  summary: () => api.get('/analytics/summary'),
}

// ── Routes / Bins ─────────────────────────────────────────────────────────
export const routesApi = {
  active: (ward_id?: number) => api.get('/routes/active', { params: ward_id ? { ward_id } : {} }),
  stops: (routeId: number) => api.get(`/routes/${routeId}/stops`),
  bins: (ward_id?: number, overflow_only = false) =>
    api.get('/routes/bins', { params: { ward_id, overflow_only } }),
}

// ── Admin ─────────────────────────────────────────────────────────────────
export const adminApi = {
  users: () => api.get('/admin/users'),
  wards: () => api.get('/admin/wards'),
  departments: () => api.get('/admin/departments'),
  createWard: (data: object) => api.post('/admin/wards', data),
}

export default api
