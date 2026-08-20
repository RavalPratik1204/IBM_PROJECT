import React, { useState, useRef } from 'react'
import { complaintsApi } from '../../services/api'
import toast from 'react-hot-toast'
import { Mic, MicOff, Send, CheckCircle, Loader2 } from 'lucide-react'

const CATEGORIES = [
  { value: '', label: 'Let AI detect' },
  { value: 'waste_collection', label: 'Missed Garbage Collection' },
  { value: 'overflow_bin', label: 'Overflowing Bin' },
  { value: 'illegal_dumping', label: 'Illegal Dumping' },
  { value: 'roadside_garbage', label: 'Roadside Garbage' },
  { value: 'segregation_issue', label: 'Segregation Issue' },
  { value: 'other', label: 'Other' },
]

// Multilingual placeholder examples
const PLACEHOLDER_EXAMPLES = [
  'मेरे इलाके में तीन दिनों से कचरा नहीं उठाया गया है।',
  'મારા વિસ્તારમાં ત્રણ દિવસથી કચરો ઉપાડવામાં આવ્યો નથી.',
  'Garbage has not been collected for 3 days in my area.',
  'The waste bin near the park is overflowing.',
]

export default function ReportIssue() {
  const [text, setText] = useState('')
  const [language, setLanguage] = useState('en')
  const [address, setAddress] = useState('')
  const [listening, setListening] = useState(false)
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState<string | null>(null)
  const recognitionRef = useRef<any>(null)
  const [placeholder] = useState(() => PLACEHOLDER_EXAMPLES[Math.floor(Math.random() * PLACEHOLDER_EXAMPLES.length)])

  const startVoice = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) {
      toast.error('Voice input not supported in this browser. Please use Chrome.')
      return
    }
    const rec = new SpeechRecognition()
    rec.lang = language === 'gu' ? 'gu-IN' : language === 'hi' ? 'hi-IN' : 'en-IN'
    rec.continuous = false
    rec.interimResults = false
    rec.onresult = (e: any) => {
      setText(e.results[0][0].transcript)
      setListening(false)
    }
    rec.onerror = () => {
      toast.error('Voice recognition failed. Please type your complaint.')
      setListening(false)
    }
    rec.onend = () => setListening(false)
    rec.start()
    recognitionRef.current = rec
    setListening(true)
  }

  const stopVoice = () => {
    recognitionRef.current?.stop()
    setListening(false)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!text.trim()) { toast.error('Please describe the issue'); return }
    setLoading(true)
    try {
      const res = await complaintsApi.submit({ original_text: text, language, address: address || null })
      setSubmitted(res.data.ticket_id)
      toast.success(`Complaint submitted! Ticket: ${res.data.ticket_id}`)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Submission failed')
    } finally {
      setLoading(false)
    }
  }

  if (submitted) {
    return (
      <div className="max-w-xl mx-auto text-center py-16">
        <CheckCircle size={64} className="text-green-500 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-gray-900 mb-2">Complaint Submitted!</h2>
        <p className="text-gray-500 mb-4">Your ticket ID is:</p>
        <div className="bg-green-50 border border-green-200 rounded-xl px-6 py-4 inline-block mb-6">
          <span className="text-2xl font-mono font-bold text-green-700">{submitted}</span>
        </div>
        <p className="text-sm text-gray-500 mb-6">
          Our AI agents are processing your complaint. You'll receive updates shortly.
        </p>
        <div className="flex gap-3 justify-center">
          <button onClick={() => setSubmitted(null)} className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">
            Submit Another
          </button>
          <a href={`/track/${submitted}`} className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700">
            Track Complaint
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Report a Waste Issue</h1>
        <p className="text-gray-500 text-sm mt-1">Describe the problem in Gujarati, Hindi, or English</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6 space-y-5">
        {/* Language selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
          <select value={language} onChange={e => setLanguage(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500">
            <option value="en">English</option>
            <option value="hi">Hindi — हिन्दी</option>
            <option value="gu">Gujarati — ગુજરાતી</option>
          </select>
        </div>

        {/* Voice + text area */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Complaint Description
          </label>
          <div className="relative">
            <textarea
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder={placeholder}
              rows={5}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
            />
            <button
              type="button"
              onClick={listening ? stopVoice : startVoice}
              className={`absolute bottom-3 right-3 p-2 rounded-lg transition-colors ${
                listening ? 'bg-red-100 text-red-600 animate-pulse' : 'bg-gray-100 text-gray-500 hover:bg-green-100 hover:text-green-600'
              }`}
              title={listening ? 'Stop recording' : 'Start voice input'}
            >
              {listening ? <MicOff size={18} /> : <Mic size={18} />}
            </button>
          </div>
          {listening && (
            <p className="text-xs text-red-500 mt-1 flex items-center gap-1">
              <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse inline-block" />
              Listening… speak your complaint
            </p>
          )}
        </div>

        {/* Address */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Location / Address (optional)</label>
          <input
            type="text"
            value={address}
            onChange={e => setAddress(e.target.value)}
            placeholder="e.g. Near Bus Stop, Navrangpura"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading || !text.trim()}
          className="w-full flex items-center justify-center gap-2 bg-green-600 text-white py-2.5 rounded-lg font-medium text-sm hover:bg-green-700 disabled:opacity-60 transition-colors"
        >
          {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
          {loading ? 'Processing with AI…' : 'Submit Complaint'}
        </button>
      </form>

      <div className="text-xs text-center text-gray-400">
        Your complaint will be processed by our AI agents and routed to the appropriate municipal department.
      </div>
    </div>
  )
}
