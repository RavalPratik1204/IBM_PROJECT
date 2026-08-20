import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { complaintsApi } from '../../services/api'
import type { Complaint, AgentLog } from '../../types'
import { Loader2, CheckCircle, Clock } from 'lucide-react'

const STATUS_STEPS = ['new', 'assigned', 'in_progress', 'resolved']

export default function ComplaintTracking() {
  const { ticketId } = useParams<{ ticketId: string }>()
  const [complaint, setComplaint] = useState<Complaint | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!ticketId) return
    complaintsApi.get(ticketId).then(res => {
      setComplaint(res.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [ticketId])

  if (loading) return <div className="flex justify-center py-20"><Loader2 size={32} className="animate-spin text-green-500" /></div>
  if (!complaint) return <div className="text-center py-16 text-gray-500">Complaint not found.</div>

  const currentStep = STATUS_STEPS.indexOf(complaint.status || 'new')

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Complaint Tracking</h1>
        <p className="text-sm text-gray-500 mt-1 font-mono">{complaint.ticket_id}</p>
      </div>

      {/* Progress steps */}
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <div className="flex items-center justify-between mb-2">
          {STATUS_STEPS.map((step, i) => (
            <React.Fragment key={step}>
              <div className="flex flex-col items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                  i <= currentStep ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-400'
                }`}>
                  {i < currentStep ? <CheckCircle size={16} /> : i + 1}
                </div>
                <span className="text-xs text-gray-500 mt-1 capitalize">{step.replace('_', ' ')}</span>
              </div>
              {i < STATUS_STEPS.length - 1 && (
                <div className={`flex-1 h-0.5 mx-2 mb-5 ${i < currentStep ? 'bg-green-600' : 'bg-gray-200'}`} />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Details */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-3">
        <h2 className="font-semibold text-gray-900">Complaint Details</h2>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <div><dt className="text-gray-500">Category</dt><dd className="font-medium capitalize">{complaint.category?.replace('_', ' ') || '—'}</dd></div>
          <div><dt className="text-gray-500">Priority</dt><dd className="font-medium capitalize">{complaint.priority || '—'}</dd></div>
          <div><dt className="text-gray-500">Language</dt><dd className="font-medium uppercase">{complaint.language}</dd></div>
          <div><dt className="text-gray-500">AI Confidence</dt><dd className="font-medium">{complaint.ai_confidence ? `${(complaint.ai_confidence * 100).toFixed(0)}%` : '—'}</dd></div>
          <div className="col-span-2"><dt className="text-gray-500">Description</dt><dd className="font-medium mt-1">{complaint.description || complaint.original_text}</dd></div>
          {complaint.routing_reason && (
            <div className="col-span-2"><dt className="text-gray-500">Routing Reason</dt><dd className="text-xs text-gray-600 mt-1">{complaint.routing_reason}</dd></div>
          )}
        </dl>
      </div>

      {/* Agent log */}
      {complaint.agent_logs && complaint.agent_logs.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h2 className="font-semibold text-gray-900 mb-3">Agent Activity Log</h2>
          <div className="agent-log">
            {complaint.agent_logs.map((log: AgentLog, i: number) => (
              <div key={i} className="agent-log-entry">
                <span className="agent-log-time">{log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : ''}</span>
                <span className="agent-log-agent">[{log.agent}]</span>
                <span className="agent-log-event">{log.event}{log.detail ? ` — ${log.detail}` : ''}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
