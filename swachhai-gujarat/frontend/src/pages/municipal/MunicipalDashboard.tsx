import React, { useEffect, useState } from 'react'
import { analyticsApi } from '../../services/api'
import type { OverviewKPIs } from '../../types'
import { Loader2, AlertTriangle, CheckCircle2, Clock, Trash2, Recycle, TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from 'recharts'

function KPICard({ label, value, sub, color, icon: Icon }: any) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
          {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
        </div>
        <div className={`p-2 rounded-lg bg-gray-50`}>
          <Icon size={20} className="text-gray-400" />
        </div>
      </div>
    </div>
  )
}

export default function MunicipalDashboard() {
  const [kpis, setKpis] = useState<OverviewKPIs | null>(null)
  const [byCategory, setByCategory] = useState<any[]>([])
  const [trend, setTrend] = useState<any[]>([])
  const [summary, setSummary] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      analyticsApi.overview(),
      analyticsApi.byCategory(),
      analyticsApi.dailyTrend(14),
      analyticsApi.summary(),
    ]).then(([k, c, t, s]) => {
      setKpis(k.data)
      setByCategory(c.data)
      setTrend(t.data)
      setSummary(s.data.summary)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex justify-center py-20"><Loader2 size={32} className="animate-spin text-green-500" /></div>
  if (!kpis) return <div className="text-center py-16 text-gray-500">Could not load dashboard data.</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Municipal Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Live operational overview — SwachhAI Gujarat</p>
      </div>

      {/* AI summary */}
      {summary && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800">
          <strong>AI Summary (Ward Analytics Agent):</strong> {summary}
        </div>
      )}

      {/* KPI grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Total Complaints" value={kpis.total_complaints} color="text-gray-900" icon={Trash2} />
        <KPICard label="Open Complaints" value={kpis.open_complaints} color="text-orange-600" icon={AlertTriangle} />
        <KPICard label="Resolved" value={kpis.resolved_complaints} sub={`${kpis.resolution_rate_pct}% rate`} color="text-green-600" icon={CheckCircle2} />
        <KPICard label="Avg Resolution" value={`${kpis.avg_resolution_hours}h`} color="text-blue-600" icon={Clock} />
        <KPICard label="Overflow Bins" value={kpis.overflow_bins} color="text-red-600" icon={AlertTriangle} />
        <KPICard label="Total Bins" value={kpis.total_bins} color="text-gray-700" icon={Trash2} />
        <KPICard label="Segregation Compliance" value={`${kpis.segregation_compliance_pct}%`} color="text-emerald-600" icon={Recycle} />
        <KPICard label="Resolution Rate" value={`${kpis.resolution_rate_pct}%`} color="text-purple-600" icon={TrendingUp} />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h2 className="font-semibold text-gray-900 mb-4 text-sm">Complaints by Category</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={byCategory} margin={{ top: 0, right: 10, left: -10, bottom: 0 }}>
              <XAxis dataKey="category" tick={{ fontSize: 10 }} tickFormatter={v => v.replace('_', ' ')} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip formatter={(v: any, n: any) => [v, 'Complaints']} labelFormatter={l => l.replace('_', ' ')} />
              <Bar dataKey="count" fill="#16a34a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h2 className="font-semibold text-gray-900 mb-4 text-sm">Daily Complaints (Last 14 Days)</h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={trend} margin={{ top: 0, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={v => v.slice(5)} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#16a34a" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
