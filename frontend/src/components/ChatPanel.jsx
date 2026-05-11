import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, ChevronDown, FileText, Sparkles } from 'lucide-react'
import { sendMessage } from '../api'

const TypingDots = () => (
  <div className="flex items-center gap-1 py-1">
    {[0, 1, 2].map(i => (
      <span
        key={i}
        className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse-dot"
        style={{ animationDelay: `${i * 0.16}s` }}
      />
    ))}
  </div>
)

const SourceCard = ({ source }) => (
  <div className="glass-light rounded-xl p-3 text-xs space-y-1 hover:border-ink-600 transition-all duration-200">
    <div className="flex items-center gap-2">
      <FileText size={11} className="text-accent shrink-0" />
      <span className="text-ink-300 font-body truncate">{source.filename}</span>
      <span className="tag ml-auto shrink-0">{source.file_type}</span>
    </div>
    <p className="text-ink-500 font-mono text-[10px] leading-relaxed line-clamp-2">
      {source.content_preview}
    </p>
  </div>
)

const Message = ({ msg }) => {
  const [showSources, setShowSources] = useState(false)
  const isUser = msg.role === 'user'

  return (
    <div className={`flex gap-3 animate-fade-up ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`
        w-8 h-8 rounded-xl shrink-0 flex items-center justify-center text-xs font-display font-bold
        ${isUser
          ? 'bg-accent text-ink-950'
          : 'bg-ink-800 text-accent border border-ink-700'
        }
      `}>
        {isUser ? <User size={14} /> : <Bot size={14} />}
      </div>

      {/* Bubble */}
      <div className={`flex-1 max-w-[80%] space-y-2 ${isUser ? 'items-end flex flex-col' : ''}`}>
        <div className={`
          px-4 py-3 rounded-2xl text-sm font-body leading-relaxed
          ${isUser
            ? 'bg-accent text-ink-950 rounded-tr-sm'
            : 'glass rounded-tl-sm text-ink-100'
          }
        `}>
          {msg.content}
        </div>

        {/* Sources toggle */}
        {!isUser && msg.sources?.length > 0 && (
          <div className="space-y-2 w-full">
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex items-center gap-1.5 text-xs text-ink-500 hover:text-accent transition-colors duration-200"
            >
              <Sparkles size={11} />
              {msg.sources.length} source{msg.sources.length > 1 ? 's' : ''} used
              <ChevronDown
                size={11}
                className={`transition-transform duration-200 ${showSources ? 'rotate-180' : ''}`}
              />
            </button>

            {showSources && (
              <div className="space-y-1.5 animate-fade-in">
                {[...new Map(msg.sources.map(s => [s.file_id + s.content_preview, s])).values()].map((src, i) => (
                  <SourceCard key={i} source={src} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Model badge */}
        {!isUser && msg.model && (
          <span className="text-[10px] text-ink-700 font-mono">{msg.model}</span>
        )}
      </div>
    </div>
  )
}

const SUGGESTIONS = [
  'What is this document about?',
  'Summarize the key points',
  'What are the main topics covered?',
  'Explain the most important concepts',
]

export default function ChatPanel({ hasFiles }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef()
  const inputRef = useRef()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = async (text) => {
    const question = text || input.trim()
    if (!question || loading) return

    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: question }])
    setLoading(true)

    try {
      const res = await sendMessage(question)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.answer,
        sources: res.sources,
        model: res.model_used,
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: err.response?.data?.detail || 'Something went wrong. Please try again.',
        sources: [],
      }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6 min-h-0">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center space-y-6 animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-ink-800 border border-ink-700 flex items-center justify-center">
              <Bot size={28} className="text-accent" />
            </div>
            <div>
              <h3 className="font-display font-semibold text-ink-100 text-lg">
                Ask anything about your documents
              </h3>
              <p className="text-ink-500 text-sm mt-1 font-body">
                {hasFiles
                  ? 'Your files are indexed and ready to search'
                  : 'Upload documents from the left panel to get started'
                }
              </p>
            </div>

            {hasFiles && (
              <div className="grid grid-cols-2 gap-2 w-full max-w-md">
                {SUGGESTIONS.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(s)}
                    className="glass-light rounded-xl px-3 py-2.5 text-left text-xs text-ink-300
                               hover:text-ink-100 hover:border-ink-600 transition-all duration-200
                               font-body leading-relaxed"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <>
            {messages.map((msg, i) => <Message key={i} msg={msg} />)}
            {loading && (
              <div className="flex gap-3 animate-fade-up">
                <div className="w-8 h-8 rounded-xl bg-ink-800 border border-ink-700 flex items-center justify-center">
                  <Bot size={14} className="text-accent" />
                </div>
                <div className="glass px-4 py-3 rounded-2xl rounded-tl-sm">
                  <TypingDots />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </>
        )}
      </div>

      {/* Input */}
      <div className="px-6 pb-6 pt-3 border-t border-ink-800/50">
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder={hasFiles ? 'Ask a question about your documents...' : 'Upload documents first...'}
              disabled={!hasFiles || loading}
              rows={1}
              className="input-field resize-none overflow-hidden min-h-[48px] max-h-32 pr-12
                         disabled:opacity-40 disabled:cursor-not-allowed"
              style={{ height: 'auto' }}
              onInput={(e) => {
                e.target.style.height = 'auto'
                e.target.style.height = Math.min(e.target.scrollHeight, 128) + 'px'
              }}
            />
          </div>
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || !hasFiles || loading}
            className="btn-primary h-12 w-12 flex items-center justify-center rounded-xl shrink-0"
          >
            <Send size={16} />
          </button>
        </div>
        <p className="text-ink-700 text-xs mt-2 font-mono text-center">
          Press Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}
