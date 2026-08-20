import { Link } from 'react-router-dom'
import { MessageSquare, ClipboardList, Recycle, Mic, ArrowRight, Trash2, MapPin } from 'lucide-react'

export default function CitizenHome() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Hero */}
      <div className="bg-gradient-to-br from-green-600 to-emerald-700 rounded-2xl p-8 text-white">
        <div className="flex items-center gap-3 mb-4">
          <Trash2 size={32} />
          <div>
            <h1 className="text-2xl font-bold">SwachhAI Gujarat</h1>
            <p className="text-green-100 text-sm">Agentic AI for Smarter Waste Management</p>
          </div>
        </div>
        <p className="text-green-50 text-sm leading-relaxed">
          Report waste issues in <strong>Gujarati, Hindi, or English</strong>. Our AI agents automatically
          classify your complaint, route it to the right department, and update you with progress.
        </p>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 gap-4">
        <Link to="/report" className="group bg-white border border-gray-200 rounded-xl p-6 hover:border-green-300 hover:shadow-sm transition-all">
          <ClipboardList className="text-green-600 mb-3" size={28} />
          <h3 className="font-semibold text-gray-900 mb-1">Report Issue</h3>
          <p className="text-xs text-gray-500">Submit a waste complaint with text or voice</p>
          <ArrowRight size={14} className="text-green-500 mt-3 group-hover:translate-x-1 transition-transform" />
        </Link>

        <Link to="/chat" className="group bg-white border border-gray-200 rounded-xl p-6 hover:border-blue-300 hover:shadow-sm transition-all">
          <MessageSquare className="text-blue-600 mb-3" size={28} />
          <h3 className="font-semibold text-gray-900 mb-1">Chat Assistant</h3>
          <p className="text-xs text-gray-500">Talk to our AI in your language</p>
          <ArrowRight size={14} className="text-blue-500 mt-3 group-hover:translate-x-1 transition-transform" />
        </Link>

        <Link to="/segregation" className="group bg-white border border-gray-200 rounded-xl p-6 hover:border-emerald-300 hover:shadow-sm transition-all">
          <Recycle className="text-emerald-600 mb-3" size={28} />
          <h3 className="font-semibold text-gray-900 mb-1">Segregation Guide</h3>
          <p className="text-xs text-gray-500">Learn which bin for which waste</p>
          <ArrowRight size={14} className="text-emerald-500 mt-3 group-hover:translate-x-1 transition-transform" />
        </Link>

        <Link to="/my-complaints" className="group bg-white border border-gray-200 rounded-xl p-6 hover:border-purple-300 hover:shadow-sm transition-all">
          <MapPin className="text-purple-600 mb-3" size={28} />
          <h3 className="font-semibold text-gray-900 mb-1">Track Complaint</h3>
          <p className="text-xs text-gray-500">View status of your complaints</p>
          <ArrowRight size={14} className="text-purple-500 mt-3 group-hover:translate-x-1 transition-transform" />
        </Link>
      </div>

      {/* How it works */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="font-semibold text-gray-900 mb-4">How SwachhAI Works</h2>
        <div className="space-y-3">
          {[
            { step: '1', text: 'You report a waste issue — in any language, by text or voice' },
            { step: '2', text: 'Grievance AI Agent classifies your complaint instantly' },
            { step: '3', text: 'Routing Agent assigns it to the right municipal department' },
            { step: '4', text: 'Route Optimization Agent schedules collection if needed' },
            { step: '5', text: 'You receive a tracking ID and live updates' },
          ].map(({ step, text }) => (
            <div key={step} className="flex items-start gap-3">
              <div className="w-6 h-6 bg-green-100 text-green-700 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                {step}
              </div>
              <p className="text-sm text-gray-600">{text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
