import React, { useEffect, useState } from 'react'
import { complaintsApi } from '../../services/api'
import { Link } from 'react-router-dom'
import type { Complaint } from '../../types'
import { Loader2, ExternalLink } from 'lucide-react'

function StatusBadge({ status }: { status: string | null }) {
  return <span className={`badge-${status || 'new'}`}>{status?.replace('_', ' ') || 'new'}</span>
}

function PriorityBadge({ priority }: { priority: string | null }) {
  return <span className={`badge-${priority || 'medium'}`}>{priority || 'medium'}</span>
}

export default function MyComplaints() {
  const [complaints, setComplaints] = useState<Complaint[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    complaintsApi.my().then(res => {
      setComplaints(res.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex justify-center py-20"><Loader2 size={32} className="animate-spin text-green-500" /></div>

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">My Complaints</h1>
      {complaints.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <p className="mb-4">No complaints submitted yet.</p>
          <Link to="/report" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700">
            Report an Issue
          </Link>
        </div>
      ) : (
        complaints.map(c => (
          <div key={c.id} className="bg-white border border-gray-200 rounded-xl p-5">
            <div className="flex items-start justify-between mb-2">
              <div>
                <span className="font-mono text-sm font-semibold text-gray-700">{c.ticket_id}</span>
                <div className="flex gap-2 mt-1">
                  <StatusBadge status={c.status} />
                  <PriorityBadge priority={c.priority} />
                  {c.category && <span className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full text-xs">{c.category.replace('_', ' ')}</span>}
                </div>
              </div>
              <Link to={`/track/${c.ticket_id}`} className="p-2 text-gray-400 hover:text-green-600">
                <ExternalLink size={16} />
              </Link>
            </div>
            <p className="text-sm text-gray-700 mt-2 line-clamp-2">{c.description || c.original_text}</p>
            <p className="text-xs text-gray-400 mt-2">{new Date(c.created_at).toLocaleDateString()}</p>
          </div>
        ))
      )}
    </div>
  )
}
