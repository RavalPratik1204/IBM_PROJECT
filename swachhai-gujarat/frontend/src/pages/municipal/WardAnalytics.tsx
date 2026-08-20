import React, { useEffect, useState } from 'react'
import { analyticsApi } from '../../services/api'
import type { WardPerformance, CategoryCount } from '../../types'
import { Loader2 } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar } from 'recharts'

export default function WardAnalytics() {
  const [wardPerf, setWardPerf] = useState<WardPerformance[]>([])
  const [byCategory, setByCategory] = useState<CategoryCount[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([analyticsApi.wardPerformance(), analyticsApi.byCategory()]).then(([w, c]) => {
      setWardPerf(w.data)
      setByCategory(c.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex justify-center py-20"><Loader2 size={32} className="animate-spin text-green-500" /></div>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Ward Analytics</h1>

      {/* Ward performance chart */}
      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <h2 className="font-semibold text-sm text-gray-900 mb-4">Complaints per Ward</h2>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={wardPerf} margin={{ top: 0, right: 10, left: -10, bottom: 40 }}>
            <XAxis dataKey="ward_name" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" interval={0} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            <Bar dataKey="total_complaints" name="Total" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="resolved_complaints" name="Resolved" fill="#16a34a" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Ward performance table */}
      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-sm text-gray-900">Ward Performance Summary</h2>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>{['Ward', 'Total', 'Resolved', 'Resolution %', 'Overflow Bins'].map(h => (
              <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {wardPerf.sort((a, b) => b.total_complaints - a.total_complaints).map(w => (
              <tr key={w.ward_id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{w.ward_name}</td>
                <td className="px-4 py-3">{w.total_complaints}</td>
                <td className="px-4 py-3 text-green-600">{w.resolved_complaints}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                      <div className="bg-green-500 h-1.5 rounded-full" style={{ width: `${w.resolution_rate_pct}%` }} />
                    </div>
                    <span className="text-xs w-10 text-right">{w.resolution_rate_pct}%</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={w.overflow_bins > 0 ? 'text-red-600 font-semibold' : 'text-gray-400'}>{w.overflow_bins}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
