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
      <div className="w-full p-4">
        <div className="flex items-center justify-between py-4">
          <h1 className="text-xl font-semibold">Dashboard</h1>
          <div className="flex items-center gap-3">
            <Link to="/chat" className="underline">Chat</Link>
            <button onClick={logout} className="text-sm underline">Logout</button>
          </div>
        </div>
        <form onSubmit={onUpload} className="bg-white p-4 rounded-xl shadow mb-4 border border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="font-medium">Upload PDF</div>
              <div className="text-xs text-gray-500">Drag & drop or choose a file</div>
            </div>
            {uploading && <Spinner />}
          </div>
          <input ref={fileRef} type="file" accept="application/pdf" className="w-full border rounded px-3 py-2" />
          {uploading && (
            <div className="mt-3">
              <ProgressBar value={progress} />
              <div className="text-xs text-gray-500 mt-1">{progress}%</div>
            </div>
          )}
          {error && <div className="text-red-600 text-sm mt-2">{error}</div>}
          <button disabled={uploading} className="mt-3 bg-black text-white py-2 px-4 rounded disabled:opacity-50">{uploading ? 'Uploading...' : 'Upload'}</button>
        </form>
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b font-medium">Your documents</div>
          <ul>
            {docs.map(d => (
              <li key={d._id} className="p-4 border-b last:border-b-0">
                <div className="font-medium">{d.filename}</div>
                <div className="text-xs text-gray-500">{d.size} bytes</div>
              </li>
            ))}
            {!docs.length && <li className="p-4 text-sm text-gray-500">No documents yet.</li>}
          </ul>
        </div>
      </div>
    </div>
  )
}


