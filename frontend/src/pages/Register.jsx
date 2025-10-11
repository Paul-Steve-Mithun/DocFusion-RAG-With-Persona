import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../auth/AuthProvider'
import { Mail, Lock, UserPlus, User, CheckCircle2, XCircle } from 'lucide-react'
import logoImg from '../assets/DocFusion.png'

export default function Register() {
  const { setToken } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  
  // Password strength requirements
  const requirements = [
    { label: 'At least 8 characters', test: (pwd) => pwd.length >= 8 },
    { label: 'One uppercase letter', test: (pwd) => /[A-Z]/.test(pwd) },
    { label: 'One lowercase letter', test: (pwd) => /[a-z]/.test(pwd) },
    { label: 'One number', test: (pwd) => /[0-9]/.test(pwd) },
    { label: 'One special character', test: (pwd) => /[!@#$%^&*(),.?":{}|<>]/.test(pwd) }
  ]
  
  const getPasswordStrength = () => {
    const passed = requirements.filter(req => req.test(password)).length
    if (passed === 0) return { label: '', color: '' }
    if (passed <= 2) return { label: 'Weak', color: 'text-red-600' }
    if (passed <= 3) return { label: 'Fair', color: 'text-orange-600' }
    if (passed <= 4) return { label: 'Good', color: 'text-yellow-600' }
    return { label: 'Strong', color: 'text-green-600' }
  }

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    
    // Check if all password requirements are met
    const allRequirementsMet = requirements.every(req => req.test(password))
    if (!allRequirementsMet) {
      setError('Please meet all password requirements')
      return
    }
    
    try {
      await api.post('/auth/register', { name, email, password })
      // Show success message and redirect to login after 2 seconds
      setError('')
      setSuccess(true)
      setTimeout(() => navigate('/login'), 2000)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Registration failed')
    }
  }

  return (
    <div className="min-h-dvh grid place-items-center bg-gradient-to-br from-slate-50 via-emerald-50 to-teal-50 p-4">
      <div className="w-full max-w-4xl">
        <div className="text-center mb-4">
          <div className="w-20 h-20 sm:w-28 sm:h-28 mx-auto mb-1">
            <img src={logoImg} alt="DocFusion AI" className="w-full h-full object-contain" />
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-teal-700 mb-2 tracking-tight">DocFusion AI</h1>
          <p className="text-sm sm:text-base text-teal-600 font-medium">Intelligent Document Assistant</p>
        </div>

        <form onSubmit={onSubmit} className="bg-white/80 backdrop-blur-xl p-6 sm:p-8 rounded-2xl shadow-2xl border border-slate-200">
          <h2 className="text-xl sm:text-2xl font-bold text-slate-800 mb-6">Create your account</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm mb-4">
              {error}
            </div>
          )}
          
          {success && (
            <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-xl text-sm mb-4 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
              <div className="font-semibold">Account created successfully!</div>
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column: Name & Email */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input 
                    value={name} 
                    onChange={e=>setName(e.target.value)} 
                    type="text" 
                    required 
                    className="w-full pl-11 pr-4 py-3 border border-slate-300 rounded-xl bg-white hover:border-emerald-400 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100 outline-none transition-all" 
                    placeholder="John Doe"
                  />
                </div>
              </div>
              
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
            </div>
            
            {/* Right Column: Password & Strength Tracker */}
            <div className="space-y-4">
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
                
                {password && (
                  <div className="mt-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-slate-600">Password Strength:</span>
                      <span className={`text-xs font-bold ${getPasswordStrength().color}`}>
                        {getPasswordStrength().label}
                      </span>
                    </div>
                    <div className="space-y-1.5">
                      {requirements.map((req, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-xs">
                          {req.test(password) ? (
                            <CheckCircle2 className="w-3.5 h-3.5 text-green-600" />
                          ) : (
                            <XCircle className="w-3.5 h-3.5 text-slate-300" />
                          )}
                          <span className={req.test(password) ? 'text-slate-700' : 'text-slate-400'}>
                            {req.label}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <button className="w-full mt-6 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white py-3.5 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2">
            <UserPlus className="w-5 h-5" />
            Create account
          </button>

          <p className="text-sm text-slate-600 text-center mt-6">
            Already have an account? <Link to="/login" className="text-emerald-600 hover:text-teal-600 font-semibold transition-colors">Sign in</Link>
          </p>
        </form>
      </div>
    </div>
  )
}


