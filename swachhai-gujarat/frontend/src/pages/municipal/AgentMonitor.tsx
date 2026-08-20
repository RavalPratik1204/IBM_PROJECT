import React, { useEffect, useState, useRef } from 'react'
import { agentsApi, analyticsApi } from '../../services/api'
import type { AgentLog } from '../../types'
import { Loader2, RefreshCw, Activity } from 'lucide-react'

export default function AgentMonitor() {
  const [logs, setLogs] = useState<AgentLog[]>([])
  const [aiStats, setAiStats] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(true)
  const bottomRef = useRef<HTMLDivElement>(null)

  const load = () => {
    Promise.all([agentsApi.logs({ limit: 100 }), analyticsApi.aiProviders()]).then(([l, a]) => {
      setLogs(l.data)
      setAiStats(a.data)
      setLoading(false)
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 100)
    }).catch(() => setLoading(false))
  }

  useEffect(() => { load(); const iv = setInterval(load, 15000); return () => clearInterval(iv) }, [])

  const AGENT_COLORS: Record<string, string> = {
    ORCHESTRATOR: 'text-purple-400',
    GRIEVANCE_AGENT: 'text-blue-400',
    ROUTING_AGENT: 'text-yellow-400',
    ROUTE_AGENT: 'text-orange-400',
    SEGREGATION_AGENT: 'text-green-400',
    ANALYTICS_AGENT: 'text-teal-400',
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Agent Monitor</h1>
          <p className="text-sm text-gray-500 mt-1">Live agentic activity log — auto-refreshes every 15s</p>
        </div>
        <button onClick={load} className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
          <RefreshCw size={15} /> Refresh
        </button>
      </div>

      {/* AI Provider Stats */}
      <div className="grid grid-cols-3 gap-4">
        {Object.entries(aiStats).map(([provider, stats]: any) => (
          <div key={provider} className="bg-white border border-gray-200 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <Activity size={16} className="text-gray-400" />
              <span className="font-semibold text-sm capitalize">{provider.replace('_', ' ')}</span>
            </div>
            <dl className="space-y-1 text-xs">
              <div className="flex justify-between"><dt className="text-gray-500">Requests</dt><dd className="font-medium">{stats.total_requests}</dd></div>
              <div className="flex justify-between"><dt className="text-gray-500">Success rate</dt><dd className="font-medium text-green-600">{stats.success_rate_pct}%</dd></div>
              <div className="flex justify-between"><dt className="text-gray-500">Avg latency</dt><dd className="font-medium">{stats.avg_latency_ms}ms</dd></div>
              <div className="flex justify-between"><dt className="text-gray-500">Fallbacks</dt><dd className="font-medium text-orange-500">{stats.fallback_events}</dd></div>
            </dl>
          </div>
        ))}
        {Object.keys(aiStats).length === 0 && (
          <div className="col-span-3 text-center py-4 text-sm text-gray-400">No AI requests recorded yet. Submit a complaint to see live data.</div>
        )}
      </div>

      {/* Agent activity log terminal */}
      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <h2 className="font-semibold text-sm text-gray-900 mb-3">Agent Activity Log</h2>
        {loading ? (
          <div className="flex justify-center py-8"><Loader2 size={24} className="animate-spin text-green-500" /></div>
        ) : (
          <div className="agent-log">
            {logs.length === 0 ? (
              <span className="text-gray-500">No agent activity yet. Submit a complaint to start the pipeline.</span>
            ) : (
              [...logs].reverse().map((log: any, i) => (
                <div key={i} className="agent-log-entry">
                  <span className="agent-log-time">{log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : '—'}</span>
                  <span className={`agent-log-agent ${AGENT_COLORS[log.agent] || 'text-gray-400'}`}>[{log.agent}]</span>
                  <span className="agent-log-event">
                    {log.event}
                    {log.detail && <span className="text-gray-500"> — {log.detail}</span>}
                    {log.provider && <span className="text-gray-600 text-xs"> ({log.provider})</span>}
                  </span>
                </div>
              ))
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>
    </div>
  )
}
