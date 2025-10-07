import { Bot, User } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeSanitize from 'rehype-sanitize'

export default function ChatBubble({ role, content, sources = [] }) {
  const isUser = role === 'user'
  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white grid place-items-center shadow-lg flex-shrink-0">
          <Bot className="w-5 h-5" />
        </div>
      )}
      <div className={`${isUser ? 'bg-gradient-to-br from-[#1e293b] to-slate-700 text-white' : 'bg-white text-slate-800 border border-slate-200'} rounded-2xl px-5 py-3.5 max-w-[75%] shadow-lg`}>
        <ReactMarkdown 
          className={`markdown ${isUser ? 'markdown-invert' : ''}`}
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeSanitize]}
        >
          {content}
        </ReactMarkdown>
        {!isUser && Array.isArray(sources) && sources.length > 0 && (
          <div className="mt-3 pt-2 border-t border-slate-200 text-xs text-slate-500 flex flex-wrap gap-2">
            {sources.map((s, i) => (
              <span key={i} className="inline-flex items-center gap-1 px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 cursor-default" title={(s.snippet || '').trim()}>
                <span className="font-medium text-slate-700 truncate max-w-[12rem]">{s.filename || 'Source'}</span>
                {typeof s.page !== 'undefined' && <span className="text-slate-400">p{s.page}</span>}
              </span>
            ))}
          </div>
        )}
      </div>
      {isUser && (
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-slate-200 to-slate-300 grid place-items-center shadow-lg flex-shrink-0">
          <User className="w-5 h-5 text-slate-600" />
        </div>
      )}
    </div>
  )
}


