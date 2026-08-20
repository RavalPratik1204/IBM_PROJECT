import React, { useEffect, useState } from 'react'
import { routesApi, agentsApi, adminApi } from '../../services/api'
import type { CollectionRoute, Ward, WasteBin } from '../../types'
import { Loader2, Play, MapPin, Truck } from 'lucide-react'
import toast from 'react-hot-toast'

export default function RouteOptimization() {
  const [routes, setRoutes] = useState<CollectionRoute[]>([])
  const [bins, setBins] = useState<WasteBin[]>([])
  const [wards, setWards] = useState<Ward[]>([])
  const [selectedWard, setSelectedWard] = useState<number | ''>('')
  const [optimizing, setOptimizing] = useState(false)
  const [loading, setLoading] = useState(true)

  const loadData = () => {
    Promise.all([
      routesApi.active(),
      routesApi.bins(undefined, false),
      adminApi.wards(),
    ]).then(([r, b, w]) => {
      setRoutes(r.data)
      setBins(b.data)
      setWards(w.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }

  useEffect(loadData, [])

  const triggerOptimization = async () => {
    if (!selectedWard) { toast.error('Select a ward first'); return }
    setOptimizing(true)
    try {
      const res = await agentsApi.optimizeRoute(Number(selectedWard))
      toast.success(`Route optimized: ${res.data.stop_count} stops, ${res.data.total_distance_km} km`)
      loadData()
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Optimization failed')
    } finally {
      setOptimizing(false)
    }
  }

  const overflowBins = bins.filter(b => b.is_overflow)
  const highFillBins = bins.filter(b => b.fill_level_pct >= 80)

  if (loading) return <div className="flex justify-center py-20"><Loader2 size={32} className="animate-spin text-green-500" /></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Route Optimization</h1>
        <p className="text-sm text-gray-500 mt-1">Priority-weighted nearest-neighbor algorithm</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
          <p className="text-2xl font-bold text-red-600">{overflowBins.length}</p>
          <p className="text-xs text-red-600 mt-1">Overflow Bins</p>
        </div>
        <div className="bg-orange-50 border border-orange-200 rounded-xl p-4 text-center">
          <p className="text-2xl font-bold text-orange-600">{highFillBins.length}</p>
          <p className="text-xs text-orange-600 mt-1">High Fill (≥80%)</p>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-center">
          <p className="text-2xl font-bold text-blue-600">{routes.length}</p>
          <p className="text-xs text-blue-600 mt-1">Active Routes</p>
        </div>
      </div>

      {/* Optimize action */}
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Generate Optimized Route</h2>
        <div className="flex gap-3">
          <select value={selectedWard} onChange={e => setSelectedWard(e.target.value ? Number(e.target.value) : '')}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500">
            <option value="">Select Ward</option>
            {wards.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
          </select>
          <button onClick={triggerOptimization} disabled={optimizing || !selectedWard}
            className="flex items-center gap-2 px-5 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50">
            {optimizing ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
            {optimizing ? 'Optimizing…' : 'Run Optimization'}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Algorithm: Priority-weighted nearest-neighbor. Overflow bins collected first, then high-fill bins, then nearest-neighbor traversal.
        </p>
      </div>

      {/* Recent routes */}
      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900 text-sm">Recent Planned Routes</h2>
        </div>
        {routes.length === 0 ? (
          <div className="text-center py-8 text-gray-400 text-sm">No routes planned yet. Select a ward and run optimization.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>{['Route Code', 'Ward', 'Stops', 'Distance', 'Est. Time', 'Status', 'Created'].map(h => (
                <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">{h}</th>
              ))}</tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {routes.map(r => (
                <tr key={r.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-xs">{r.route_code}</td>
                  <td className="px-4 py-3 text-xs">{r.ward_id}</td>
                  <td className="px-4 py-3 text-xs">{r.stop_count}</td>
                  <td className="px-4 py-3 text-xs">{r.total_distance_km ? `${r.total_distance_km} km` : '—'}</td>
                  <td className="px-4 py-3 text-xs">{r.estimated_duration_min ? `~${r.estimated_duration_min} min` : '—'}</td>
                  <td className="px-4 py-3"><span className="badge-assigned">{r.status}</span></td>
                  <td className="px-4 py-3 text-xs text-gray-500">{new Date(r.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
