import { useEffect, useRef, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../auth/AuthProvider'
import ChatBubble from '../components/ChatBubble'
import TypingDots from '../components/TypingDots'
import Spinner from '../components/Spinner'
import { Upload, FileText, LogOut, Send, Plus, MoreHorizontal, Trash2, User } from 'lucide-react'
import logoImg from '../assets/DocFusion.png'

export default function Chat() {
  const { token, setToken } = useAuth()
  const [sessionId, setSessionId] = useState('')
  const [messages, setMessages] = useState([])
  const [sessions, setSessions] = useState([])
  const [openMenu, setOpenMenu] = useState(null)
  const menuHideDelayMs = 400
  const [input, setInput] = useState('')
  const [error, setError] = useState('')
  const [typing, setTyping] = useState(false)
  const [docs, setDocs] = useState([])
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const fileRef = useRef(null)
  const [fileName, setFileName] = useState('')
  const bottomRef = useRef(null)
  const [userName, setUserName] = useState('')
  const [userEmail, setUserEmail] = useState('')

  useEffect(() => {
    if (!token) return
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    fetchUserInfo()
  }, [token])
  
  async function fetchUserInfo() {
    try {
      const { data } = await api.get('/auth/me')
      setUserName(data.name || 'User')
      setUserEmail(data.email || '')
    } catch (error) {
      console.error('Failed to fetch user info:', error)
    }
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function logout() { setToken('') }

  async function refreshDocs(activeId = sessionId) {
    try {
      if (activeId) {
        const { data } = await api.get('/documents', { params: { session_id: activeId } })
        setDocs(data)
      }
    } catch {}
  }

  useEffect(() => { refreshDocs(); refreshSessions() }, [])

  async function refreshSessions(){
    try{
      const r = await api.get('/sessions')
      if (r.data && r.data.length) {
        setSessions(r.data)
        if (!sessionId) {
          const first = r.data[0].name
          setSessionId(first)
          refreshDocs(first)
          try{ const h = await api.get('/chat/history', { params: { session_id: first } }); setMessages(h.data) }catch{}
        }
        return
      }
      // No session exists yet → create "Session 1"
      const created = await api.post('/sessions/new', { name: 'Session 1' })
      const r2 = await api.get('/sessions')
      setSessions(r2.data)
      setSessionId('Session 1')
    }catch{}
  }

  async function send() {
    if (!input.trim()) return
    const userMsg = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setError('')
    try {
      setTyping(true)
      // Call streaming endpoint for future enhancement; for now use normal and rename session if needed
      const { data } = await api.post('/chat/ask', { session_id: sessionId, message: userMsg.content })
      const aiText = data.answer
      const sources = data.sources || []
      setMessages(prev => [...prev, { role: 'assistant', content: aiText, sources }])
      setTyping(false) // Clear typing animation before session rename
      // If session uses the default sequential name (e.g., "Session 1"), rename it after first Q&A
      if (/^Session\s+\d+$/i.test(sessionId)) {
        try {
          const suggest = await api.post('/sessions/suggest_from_chat', { messages: [
            ...messages.slice(-4),
            userMsg,
            { role: 'assistant', content: aiText }
          ]})
          const newName = suggest.data.name || sessionId
          if (newName && newName !== sessionId) {
            try {
              await api.post('/sessions/rename_by_name', { old_name: sessionId, new_name: newName })
            } catch {}
            setSessionId(newName)
            // Optimistically update local list to improve UX
            setSessions(prev => prev.map(s => s.name === sessionId ? { ...s, name: newName } : s))
            refreshSessions()
          }
        } catch (e) {}
      }
    } catch (err) {
      setError(err?.response?.data?.detail || 'Chat failed')
    } finally {
      setTyping(false)
    }
  }

  async function onUpload(e) {
    e.preventDefault()
    const file = fileRef.current?.files?.[0]
    if (!file) return
    setFileName(file.name)
    setUploading(true); setProgress(0)
    const form = new FormData()
    form.append('file', file)
    if (sessionId) form.append('session_id', sessionId)
    try {
      await api.post('/documents/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (ev) => {
          if (!ev.total) return
          setProgress(Math.round((ev.loaded / ev.total) * 100))
        }
      })
      if (fileRef.current) fileRef.current.value = ''
      setFileName('') // Clear the filename display after successful upload
      // Fetch docs only for current session
      try { const r = await api.get('/documents', { params: { session_id: sessionId } }); setDocs(r.data) } catch {}
    } catch (err) {
      setError(err?.response?.data?.detail || 'Upload failed')
      setFileName('') // Clear filename on error too
    } finally {
      setUploading(false)
    }
  }

  async function openDocument(docId, filename) {
    try {
      // Fetch PDF with auth headers
      const response = await api.get(`/documents/${docId}/view`, {
        responseType: 'blob'
      })
      
      // Create a blob URL and open in new tab
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const newWindow = window.open(url, '_blank')
      
      // Clean up the blob URL after a delay
      setTimeout(() => window.URL.revokeObjectURL(url), 100)
    } catch (err) {
      setError('Failed to open document')
    }
  }

  return (
    <div className="min-h-dvh bg-gradient-to-br from-slate-50 via-emerald-50 to-teal-50">
      <div className="h-dvh grid grid-cols-[280px_1fr_280px]">
        <aside className="h-full border-r border-emerald-200/50 bg-gradient-to-r from-emerald-100/50 to-teal-100/50 backdrop-blur-xl shadow-xl flex flex-col overflow-y-auto">
          <div className="p-6 border-b border-emerald-200/50">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-16 h-16">
                <img src={logoImg} alt="DocFusion AI" className="w-full h-full object-contain" />
              </div>
              <div>
                <div className="text-2xl font-black text-teal-700 tracking-tight">DocFusion AI</div>
                {/* <div className="text-xs text-teal-600 font-semibold">Your Document Assistant</div> */}
              </div>
            </div>
          </div>

          <div className="flex-1 overflow-auto p-4 space-y-4">
            <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-lg">
              <div className="flex items-center justify-between mb-3">
                <div className="text-sm font-semibold text-slate-700">Chat History</div>
                <button onClick={async ()=>{
                  try {
                    const r = await api.post('/sessions/new')
                    const name = r.data.name
                    setSessionId(name)
                    refreshSessions()
                  } catch {}
                  setDocs([])
                  setMessages([])
                  setInput('')
                  setFileName('')
                  if (fileRef.current) fileRef.current.value = ''
                }} className="flex items-center gap-1 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white px-2 py-1 text-xs font-medium shadow-sm hover:shadow transition-all">
                  <Plus className="w-3.5 h-3.5"/> New
                </button>
              </div>
              <ul className="space-y-2">
                {sessions.map(s => (
                  <li key={s._id} className={`p-2 rounded-lg border ${sessionId===s.name? 'border-emerald-400 bg-emerald-50' : 'border-slate-200 hover:bg-slate-50'}`}>
                    <div className="flex items-center gap-2">
                      <button className="flex-1 text-left text-sm truncate" onClick={async ()=>{
                        setSessionId(s.name)
                        setFileName('')
                        if (fileRef.current) fileRef.current.value = ''
                        try{ const r = await api.get('/documents', { params: { session_id: s.name } }); setDocs(r.data) }catch{}
                        try{ const r2 = await api.get('/chat/history', { params: { session_id: s.name } }); setMessages(r2.data) }catch{}
                      }}>{s.name}</button>
                      <div className="relative">
                        <button className="p-1 rounded hover:bg-slate-100" onClick={()=> setOpenMenu(openMenu===s.name? null : s.name)}>
                          <MoreHorizontal className="w-4 h-4" />
                        </button>
                        {openMenu===s.name && (
                          <div 
                            className="absolute right-0 mt-1 bg-white border border-slate-200 rounded shadow-md z-10 transition-opacity duration-200 ease-out animate-fadeIn"
                            onMouseEnter={()=> {/* keep open */}}
                            onMouseLeave={()=> { setTimeout(()=>{ setOpenMenu(null) }, menuHideDelayMs) }}
                          >
                            <button onClick={async ()=>{ await api.delete(`/sessions/${encodeURIComponent(s.name)}`); setOpenMenu(null); refreshSessions(); if(sessionId===s.name){ setSessionId(''); setDocs([]); setMessages([]); } }} className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-slate-50 w-full">
                              <Trash2 className="w-4 h-4 text-red-500" /> Delete
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </li>
                ))}
                {!sessions.length && <li className="text-xs text-slate-500">No sessions yet.</li>}
              </ul>
            </div>
          </div>

          <div className="p-4 border-t border-emerald-200/50">
            {/* User Profile Section - Minimal */}
            <div className="flex items-center gap-3 mb-3 px-1">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-emerald-600 to-teal-600 flex items-center justify-center text-white shadow-sm">
                <User className="w-4 h-4" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-large font-bold text-teal-700 truncate">{userName}</div>
              </div>
            </div>
            
            {/* Sign Out Button */}
            <button onClick={logout} className="w-full flex items-center justify-center gap-2 text-sm text-red-500 hover:text-red-700 hover:bg-red-50 py-2.5 rounded-xl transition-all font-medium">
              <LogOut className="w-4 h-4" />
              Sign out
            </button>
          </div>
        </aside>

        <main className="h-full flex flex-col overflow-hidden">

          <div className="flex-1 overflow-auto chat-scroll">
            <div className="max-w-4xl mx-auto p-8 space-y-6">
              {!messages.length && (
                <div className="text-center py-20">
                  <div className="w-20 h-20 mx-auto mb-4">
                    <img src={logoImg} alt="DocFusion AI" className="w-full h-full object-contain" />
                  </div>
                  <h2 className="text-3xl font-black text-teal-700 mb-3">Welcome, {userName}! 👋</h2>
                  <p className="text-slate-600 text-lg mb-2">Your Intelligent Document Assistant</p>
                  <p className="text-slate-500 max-w-2xl mx-auto">
                    Upload your PDF documents and interact with them using natural language. Ask questions, extract insights, and get AI-powered answers with source references instantly.
                  </p>
                </div>
              )}
              {messages.map((m, i) => (
                <ChatBubble key={i} role={m.role} content={m.content} sources={m.sources} />
              ))}
              {typing && (
                <div className="flex justify-start">
                  <div className="bg-white border border-slate-200 rounded-2xl px-5 py-4 shadow-lg">
                    <TypingDots />
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          </div>

          {error && (
            <div className="px-8 py-2">
              <div className="max-w-4xl mx-auto bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
                {error}
              </div>
            </div>
          )}

          <footer className="p-6 border-t border-emerald-200/30 bg-gradient-to-br from-emerald-50/90 to-teal-50/90 backdrop-blur-xl sticky bottom-0">
            <div className="max-w-4xl mx-auto">
              <div className="relative flex items-center gap-3 p-2 bg-white rounded-2xl shadow-xl border-2 border-emerald-200/50 hover:border-emerald-300 transition-all">
                <input 
                  value={input} 
                  onChange={e=>setInput(e.target.value)} 
                  onKeyDown={e=>e.key==='Enter'&&!e.shiftKey&&send()} 
                  placeholder="Ask anything about your documents..." 
                  className="flex-1 px-4 py-3 bg-transparent outline-none text-slate-700 placeholder:text-slate-400" 
                />
                <button 
                  onClick={send} 
                  className="rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg hover:shadow-xl transition-all font-semibold" 
                  disabled={typing || !input.trim()}
                >
                  <Send className="w-4 h-4" />
                  {typing ? 'Thinking...' : 'Send'}
                </button>
              </div>
            </div>
          </footer>
        </main>

        {/* Right Sidebar - Documents */}
        <aside className="h-full border-l border-emerald-200/50 bg-gradient-to-r from-emerald-100/50 to-teal-100/50 backdrop-blur-xl shadow-xl flex flex-col overflow-y-auto">
          <div className="p-6 border-b border-emerald-200/50">
            <div className="text-lg font-bold text-teal-700">Documents</div>
            <div className="text-xs text-teal-600 mt-1">Manage your PDFs</div>
          </div>

          <div className="flex-1 overflow-auto p-4 space-y-4">
            {/* Upload Document Card */}
            <form onSubmit={onUpload} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-lg hover:shadow-xl transition-all">
              <div className="flex items-center gap-2 mb-4">
                <Upload className="w-4 h-4 text-emerald-600" />
                <div className="text-sm font-semibold text-slate-700">Upload Document</div>
              </div>
              <input ref={fileRef} type="file" accept="application/pdf" className="hidden" onChange={(e)=> setFileName(e.target.files?.[0]?.name || '')} />
              
              {/* Choose File Button */}
              <button 
                type="button" 
                onClick={()=>fileRef.current?.click()} 
                className="w-full rounded-xl border-2 border-dashed border-emerald-300 bg-emerald-50/50 hover:bg-emerald-50 hover:border-emerald-400 text-emerald-700 px-4 py-6 text-sm font-medium transition-all flex flex-col items-center justify-center gap-2"
              >
                <Upload className="w-6 h-6" />
                <span>Choose File</span>
              </button>
              
              {/* File Preview */}
              {fileName && (
                <div className="mt-3 p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-slate-500 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-slate-700 truncate">{fileName}</div>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Upload Progress */}
              {uploading && (
                <div className="mt-3">
                  <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 transition-all" style={{ width: `${progress}%` }} />
                  </div>
                  <div className="text-xs text-slate-500 mt-1 text-center">{progress}%</div>
                </div>
              )}
              
              {/* Upload Button */}
              <button 
                disabled={uploading || !fileName} 
                className="mt-3 w-full rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white py-3 text-sm font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all"
              >
                {uploading ? <Spinner size={16} /> : <Upload className="w-4 h-4" />}
                {uploading ? 'Uploading...' : 'Upload PDF'}
              </button>
            </form>

            {/* Your Documents Card */}
            <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-lg">
              <div className="flex items-center gap-2 mb-3">
                <FileText className="w-4 h-4 text-slate-600" />
                <div className="text-sm font-semibold text-slate-700">Your Documents</div>
              </div>
              <ul className="space-y-2">
                {docs.map(d => (
                  <li key={d._id} onClick={() => openDocument(d._id, d.filename)} className="p-3 rounded-xl bg-gradient-to-br from-slate-50 to-slate-100 hover:from-emerald-50 hover:to-teal-50 border border-slate-200 hover:border-emerald-200 transition-all cursor-pointer group">
                    <div className="flex items-start gap-2">
                      <FileText className="w-4 h-4 text-slate-400 group-hover:text-emerald-500 mt-0.5 transition-colors" />
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm text-slate-700 truncate">{d.filename}</div>
                        <div className="text-xs text-slate-500">{(d.size / 1024).toFixed(1)} KB</div>
                      </div>
                    </div>
                  </li>
                ))}
                {!docs.length && (
                  <li className="text-xs text-slate-500 text-center py-8">
                    <FileText className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                    No documents yet. Upload your first PDF!
                  </li>
                )}
              </ul>
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}


