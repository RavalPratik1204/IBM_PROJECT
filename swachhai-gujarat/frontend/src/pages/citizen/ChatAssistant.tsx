import React, { useState, useRef, useEffect } from 'react'
import { agentsApi } from '../../services/api'
import { Send, Mic, MicOff, Loader2, Bot, User } from 'lucide-react'
import clsx from 'clsx'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

const INITIAL_MESSAGE: Message = {
  role: 'assistant',
  content: 'Hello! I am the SwachhAI Waste Assistant. You can report waste issues or ask questions in Gujarati, Hindi, or English.\n\nનમસ્તે! કચરા સંબંધિત સમસ્યા જણાવો.\nनमस्ते! कचरे की समस्या बताएं।',
  timestamp: new Date().toISOString(),
}

export default function ChatAssistant() {
  const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE])
  const [input, setInput] = useState('')
  const [language, setLanguage] = useState('en')
  const [loading, setLoading] = useState(false)
  const [listening, setListening] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const recognitionRef = useRef<any>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text: string) => {
    if (!text.trim()) return
    const userMsg: Message = { role: 'user', content: text, timestamp: new Date().toISOString() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const history = messages.slice(-6).map(m => ({ role: m.role, content: m.content }))
      const res = await agentsApi.chat(text, language, history)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data.response,
        timestamp: new Date().toISOString(),
      }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I am having trouble processing your request. Please try again.',
        timestamp: new Date().toISOString(),
      }])
    } finally {
      setLoading(false)
    }
  }

  const startVoice = () => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SR) { alert('Voice not supported. Use Chrome.'); return }
    const rec = new SR()
    rec.lang = language === 'gu' ? 'gu-IN' : language === 'hi' ? 'hi-IN' : 'en-IN'
    rec.onresult = (e: any) => {
      sendMessage(e.results[0][0].transcript)
      setListening(false)
    }
    rec.onerror = () => setListening(false)
    rec.onend = () => setListening(false)
    rec.start()
    recognitionRef.current = rec
    setListening(true)
  }

  return (
    <div className="max-w-2xl mx-auto flex flex-col" style={{ height: 'calc(100vh - 160px)' }}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900">AI Chat Assistant</h1>
          <p className="text-xs text-gray-500">Powered by IBM Granite + Groq</p>
        </div>
        <select value={language} onChange={e => setLanguage(e.target.value)}
          className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500">
          <option value="en">English</option>
          <option value="hi">हिन्दी</option>
          <option value="gu">ગુજરાતી</option>
        </select>
      </div>

      {/* Messages */}
      <div className="flex-1 bg-white border border-gray-200 rounded-xl overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={clsx('flex gap-3', msg.role === 'user' && 'flex-row-reverse')}>
            <div className={clsx(
              'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
              msg.role === 'assistant' ? 'bg-green-100' : 'bg-blue-100'
            )}>
              {msg.role === 'assistant' ? <Bot size={16} className="text-green-600" /> : <User size={16} className="text-blue-600" />}
            </div>
            <div className={clsx(
              'max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap',
              msg.role === 'assistant' ? 'bg-gray-100 text-gray-800' : 'bg-green-600 text-white'
            )}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
              <Bot size={16} className="text-green-600" />
            </div>
            <div className="bg-gray-100 px-4 py-3 rounded-2xl">
              <Loader2 size={16} className="animate-spin text-gray-400" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="mt-3 flex gap-2">
        <button
          onClick={listening ? () => { recognitionRef.current?.stop(); setListening(false) } : startVoice}
          className={clsx(
            'p-3 rounded-xl border transition-colors',
            listening ? 'bg-red-50 border-red-300 text-red-500 animate-pulse' : 'border-gray-300 text-gray-500 hover:border-green-400 hover:text-green-600'
          )}
        >
          {listening ? <MicOff size={18} /> : <Mic size={18} />}
        </button>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage(input)}
          placeholder="Type your message or use voice…"
          className="flex-1 px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
        />
        <button
          onClick={() => sendMessage(input)}
          disabled={loading || !input.trim()}
          className="p-3 bg-green-600 text-white rounded-xl hover:bg-green-700 disabled:opacity-50 transition-colors"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  )
}
