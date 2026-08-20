import React, { useState } from 'react'
import { agentsApi } from '../../services/api'
import { Loader2, Recycle, AlertTriangle } from 'lucide-react'

const QUICK_QUESTIONS = [
  { q: 'Where do I put food waste?', lang: 'en' },
  { q: 'Where do I put old batteries?', lang: 'en' },
  { q: 'ખોરાકનો કચરો ક્યાં નાખવો?', lang: 'gu' },
  { q: 'पुरानी बैटरी कहाँ फेंकें?', lang: 'hi' },
  { q: 'Where do newspapers and cardboard go?', lang: 'en' },
]

const CATEGORY_GUIDE = [
  { name: 'Wet Waste', bin: 'Green Bin', icon: '🟢', examples: 'Food scraps, vegetable peels, cooked food, garden waste' },
  { name: 'Dry Waste', bin: 'Blue Bin', icon: '🔵', examples: 'Paper, cardboard, plastic bottles, glass, metal cans' },
  { name: 'Hazardous', bin: 'Red Bin', icon: '🔴', examples: 'Batteries, medicines, paint, chemicals, e-waste' },
  { name: 'Non-Recyclable', bin: 'Black Bin', icon: '⚫', examples: 'Soiled plastic, thermocol, sanitary waste, diapers' },
]

export default function SegregationGuide() {
  const [question, setQuestion] = useState('')
  const [language, setLanguage] = useState('en')
  const [guidance, setGuidance] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const ask = async (q: string, lang: string) => {
    setQuestion(q)
    setLanguage(lang)
    setLoading(true)
    setGuidance(null)
    try {
      const res = await agentsApi.segregation(q, lang)
      setGuidance(res.data.guidance)
    } catch {
      setGuidance('Unable to get guidance. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Waste Segregation Guide</h1>
        <p className="text-sm text-gray-500 mt-1">Ask our AI or browse the category guide below</p>
      </div>

      {/* Quick question input */}
      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <label className="block text-sm font-medium text-gray-700 mb-2">Ask a segregation question</label>
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && ask(question, language)}
            placeholder="e.g. Where do I put old batteries?"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          <select value={language} onChange={e => setLanguage(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500">
            <option value="en">EN</option>
            <option value="hi">HI</option>
            <option value="gu">GU</option>
          </select>
          <button onClick={() => ask(question, language)} disabled={loading || !question.trim()}
            className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50">
            Ask
          </button>
        </div>

        {/* Quick questions */}
        <div className="flex flex-wrap gap-2 mt-3">
          {QUICK_QUESTIONS.map(({ q, lang }, i) => (
            <button key={i} onClick={() => ask(q, lang)}
              className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-green-50 hover:text-green-700 rounded-full text-gray-600 transition-colors">
              {q}
            </button>
          ))}
        </div>

        {/* AI guidance */}
        {(loading || guidance) && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            {loading ? (
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Loader2 size={16} className="animate-spin" /> Getting AI guidance…
              </div>
            ) : (
              <>
                <div className="text-sm text-gray-800 whitespace-pre-wrap">{guidance}</div>
                <div className="flex items-center gap-1 mt-2 text-xs text-amber-600">
                  <AlertTriangle size={12} />
                  General Guidelines — Verify with your local municipality
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Category guide */}
      <div className="grid grid-cols-2 gap-4">
        {CATEGORY_GUIDE.map(cat => (
          <div key={cat.name} className="bg-white border border-gray-200 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xl">{cat.icon}</span>
              <div>
                <h3 className="font-semibold text-sm text-gray-900">{cat.name}</h3>
                <p className="text-xs text-gray-500">{cat.bin}</p>
              </div>
            </div>
            <p className="text-xs text-gray-600">{cat.examples}</p>
          </div>
        ))}
      </div>

      <p className="text-xs text-center text-amber-600 flex items-center justify-center gap-1">
        <AlertTriangle size={12} />
        All guidance is general. Always verify with your local municipal authority.
      </p>
    </div>
  )
}
