import React, { useEffect, useState } from 'react'
import { complaintsApi } from '../../services/api'
import type { Complaint } from '../../types'
import { Loader2, RefreshCw, Filter } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function LiveComplaints() {
  const [complaints, setComplaints] = useState<Complaint[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ status: '', priority: '', category: '' })
  const [offset, setOffset] = useState(0)
  const LIMIT = 20

  const load = () => {
    setLoading(true)
    const params: any = { limit: LIMIT, offset, ...filters }
    Object.keys(params).forEach(k => !params[k] && delete params[k])
    complaintsApi.list(params).then(res => {
      setComplaints(res.data.items)
      setTotal(res.data.total)
      setLoading(false)
    }).catch(() => setLoading(false))
  }

  useEffect(load, [offset, filters])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Live Complaints <span className="text-lg font-normal text-gray-500">({total})</span></h1>
        <button onClick={load} className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
          <RefreshCw size={15} /> Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        {[
          { key: 'status', opts: ['', 'new', 'assigned', 'in_progress', 'resolved'] },
          { key: 'priority', opts: ['', 'low', 'medium', 'high', 'critical'] },
          { key: 'category', opts: ['', 'waste_collection', 'overflow_bin', 'illegal_dumping', 'roadside_garbage', 'segregation_issue'] },
        ].map(({ key, opts }) => (
          <select key={key} value={(filters as any)[key]}
            onChange={e => { setFilters(f => ({ ...f, [key]: e.target.value })); setOffset(0) }}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 capitalize">
            {opts.map(o => <option key={o} value={o}>{o || `All ${key}`}</option>)}
          </select>
        ))}
      </div>

      {/* Table */}
      {loading ? (
        <div className="flex justify-center py-16"><Loader2 size={28} className="animate-spin text-green-500" /></div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                {['Ticket', 'Category', 'Priority', 'Status', 'Language', 'Ward', 'Created', 'Actions'].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {complaints.map(c => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-xs text-gray-700">{c.ticket_id}</td>
                  <td className="px-4 py-3 text-xs capitalize">{c.category?.replace('_', ' ') || '—'}</td>
                  <td className="px-4 py-3"><span className={`badge-${c.priority}`}>{c.priority}</span></td>
                  <td className="px-4 py-3"><span className={`badge-${c.status}`}>{c.status?.replace('_', ' ')}</span></td>
                  <td className="px-4 py-3 text-xs uppercase">{c.language}</td>
                  <td className="px-4 py-3 text-xs">{c.ward_id || '—'}</td>
                  <td className="px-4 py-3 text-xs text-gray-500">{new Date(c.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3">
                    <Link to={`/track/${c.ticket_id}`} className="text-xs text-green-600 hover:underline">View</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {complaints.length === 0 && <div className="text-center py-8 text-gray-400 text-sm">No complaints found</div>}
        </div>
      )}

      {/* Pagination */}
      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>Showing {offset + 1}–{Math.min(offset + LIMIT, total)} of {total}</span>
        <div className="flex gap-2">
          <button disabled={offset === 0} onClick={() => setOffset(o => Math.max(0, o - LIMIT))}
            className="px-3 py-1.5 border rounded-lg disabled:opacity-40 hover:bg-gray-50">Prev</button>
          <button disabled={offset + LIMIT >= total} onClick={() => setOffset(o => o + LIMIT)}
            className="px-3 py-1.5 border rounded-lg disabled:opacity-40 hover:bg-gray-50">Next</button>
        </div>
      </div>
    </div>
  )
}
