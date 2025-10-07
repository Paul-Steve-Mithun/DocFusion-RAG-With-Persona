import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../auth/AuthProvider'
import { Mail, Lock, LogIn } from 'lucide-react'
import logoImg from '../assets/DocFusion.png'

export default function Login() {
  const { setToken } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      const { data } = await api.post('/auth/login', { email, password })
      setToken(data.access_token)
      navigate('/')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <div className="min-h-dvh grid place-items-center bg-gradient-to-br from-slate-50 via-emerald-50 to-teal-50 p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-20 h-20 rounded-2xl bg-[#1e293b] p-1.5 flex items-center justify-center mx-auto mb-4 shadow-xl">
            <img src={logoImg} alt="DocFusion AI" className="w-full h-full object-contain" />
          </div>
          <h1 className="text-3xl font-bold text-[#1e293b] mb-2">DocFusion AI</h1>
          <p className="text-slate-600">Intelligent Document Assistant</p>
        </div>

        <form onSubmit={onSubmit} className="bg-white/80 backdrop-blur-xl p-8 rounded-2xl shadow-2xl border border-slate-200">
          <h2 className="text-2xl font-bold text-slate-800 mb-6">Welcome back</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm mb-4">
              {error}
            </div>
          )}
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Email address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input 
                  value={email} 
                  onChange={e=>setEmail(e.target.value)} 
                  type="email" 
                  required 
                  className="w-full pl-11 pr-4 py-3 border border-slate-300 rounded-xl bg-white hover:border-emerald-400 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100 outline-none transition-all" 
                  placeholder="you@example.com"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input 
                  value={password} 
                  onChange={e=>setPassword(e.target.value)} 
                  type="password" 
                  required 
                  className="w-full pl-11 pr-4 py-3 border border-slate-300 rounded-xl bg-white hover:border-emerald-400 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100 outline-none transition-all" 
                  placeholder="••••••••"
                />
              </div>
            </div>
          </div>

          <button className="w-full mt-6 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white py-3.5 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2">
            <LogIn className="w-5 h-5" />
            Sign in
          </button>

          <p className="text-sm text-slate-600 text-center mt-6">
            Don't have an account? <Link to="/register" className="text-emerald-600 hover:text-teal-600 font-semibold transition-colors">Create one</Link>
          </p>
        </form>
      </div>
    </div>
  )
}


