import { useEffect, useRef, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../auth/AuthProvider'
import { Link } from 'react-router-dom'
import Spinner from '../components/Spinner'
import ProgressBar from '../components/ProgressBar'

export default function Dashboard() {
  const { token, setToken } = useAuth()
  const [docs, setDocs] = useState([])
  const [error, setError] = useState('')
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const fileRef = useRef(null)

  useEffect(() => {
    if (!token) return
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    api.get('/documents').then(r => setDocs(r.data)).catch(() => {})
  }, [token])

  async function onUpload(e) {
    e.preventDefault()
    setError('')
    const file = fileRef.current?.files?.[0]
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    try {
      setUploading(true)
      setProgress(0)
      const { data } = await api.post('/documents/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (!e.total) return
          setProgress(Math.round((e.loaded / e.total) * 100))
        }
      })
      setDocs(prev => [data, ...prev])
      if (fileRef.current) fileRef.current.value = ''
    } catch (err) {
      setError(err?.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  function logout() {
    setToken('')
  }

  return (
    <div className="min-h-dvh bg-gray-50">
      <div className="w-full p-4 sm:p-6 lg:p-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between py-4 gap-4">
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-800">Dashboard</h1>
            <div className="flex items-center gap-3">
              <Link to="/chat" className="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-medium transition-colors">Chat</Link>
              <button onClick={logout} className="px-4 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg font-medium transition-colors">Logout</button>
            </div>
          </div>
        <form onSubmit={onUpload} className="bg-white p-4 sm:p-6 rounded-xl shadow-lg mb-4 sm:mb-6 border border-gray-200">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
            <div>
              <div className="font-semibold text-lg text-slate-800">Upload PDF</div>
              <div className="text-xs text-gray-500">Drag & drop or choose a file</div>
            </div>
            {uploading && <Spinner />}
          </div>
          <input ref={fileRef} type="file" accept="application/pdf" className="w-full border-2 border-gray-200 rounded-lg px-3 py-3 text-sm focus:border-teal-500 focus:outline-none transition-colors" />
          {uploading && (
            <div className="mt-4">
              <ProgressBar value={progress} />
              <div className="text-xs text-gray-500 mt-2 text-center">{progress}%</div>
            </div>
          )}
          {error && <div className="text-red-600 text-sm mt-3 p-3 bg-red-50 rounded-lg border border-red-200">{error}</div>}
          <button disabled={uploading} className="mt-4 w-full sm:w-auto bg-teal-600 hover:bg-teal-700 text-white py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors">{uploading ? 'Uploading...' : 'Upload Document'}</button>
        </form>
        <div className="bg-white rounded-xl shadow-lg border border-gray-200">
          <div className="p-4 sm:p-6 border-b border-gray-200 font-semibold text-lg text-slate-800">Your Documents</div>
          <ul className="divide-y divide-gray-200">
            {docs.map(d => (
              <li key={d._id} className="p-4 sm:p-6 hover:bg-gray-50 transition-colors">
                <div className="font-medium text-slate-800 mb-1">{d.filename}</div>
                <div className="text-xs text-gray-500">{(d.size / 1024).toFixed(1)} KB</div>
              </li>
            ))}
            {!docs.length && <li className="p-8 text-sm text-gray-500 text-center">No documents yet. Upload your first PDF above!</li>}
          </ul>
        </div>
        </div>
      </div>
    </div>
  )
}


