// Central TypeScript types for SwachhAI Gujarat

export interface User {
  id: number
  name: string
  email: string
  role: 'citizen' | 'officer' | 'admin'
  preferred_language: string
  ward_id: number | null
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (token: string, user: User) => void
  logout: () => void
}

export interface Complaint {
  id: number
  ticket_id: string
  original_text: string
  language: string
  description: string | null
  category: string | null
  priority: 'low' | 'medium' | 'high' | 'critical' | null
  status: 'new' | 'assigned' | 'in_progress' | 'resolved' | 'closed' | null
  ward_id: number | null
  address: string | null
  latitude: number | null
  longitude: number | null
  department_id: number | null
  routing_reason: string | null
  ai_confidence: number | null
  ai_provider: string | null
  requires_route_optimization: boolean
  is_demo_data: boolean
  created_at: string
  updated_at: string
  resolved_at: string | null
  agent_logs?: AgentLog[]
}

export interface AgentLog {
  agent: string
  event: string
  detail: string | null
  provider: string | null
  latency_ms?: number | null
  timestamp: string
}

export interface Ward {
  id: number
  name: string
  code: string
  latitude: number | null
  longitude: number | null
  population: number | null
  is_active: boolean
}

export interface WasteBin {
  id: number
  bin_code: string
  ward_id: number | null
  latitude: number
  longitude: number
  fill_level_pct: number
  is_overflow: boolean
  capacity_liters: number
  waste_category: string | null
  last_collected: string | null
  is_demo_data: boolean
}

export interface CollectionRoute {
  id: number
  route_code: string
  ward_id: number | null
  vehicle_id: number | null
  status: string
  total_distance_km: number | null
  estimated_duration_min: number | null
  stop_count: number
  created_at: string
}

export interface OverviewKPIs {
  total_complaints: number
  open_complaints: number
  resolved_complaints: number
  resolution_rate_pct: number
  avg_resolution_hours: number
  overflow_bins: number
  segregation_compliance_pct: number
  total_bins: number
}

export interface WardPerformance {
  ward_id: number
  ward_name: string
  total_complaints: number
  resolved_complaints: number
  resolution_rate_pct: number
  overflow_bins: number
}

export interface CategoryCount {
  category: string
  count: number
}

export interface DailyTrend {
  date: string
  count: number
}
