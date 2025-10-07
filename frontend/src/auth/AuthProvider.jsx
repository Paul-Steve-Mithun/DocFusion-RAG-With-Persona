import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { setAuthToken } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token') || '')

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token)
      setAuthToken(token)
    } else {
      localStorage.removeItem('token')
      setAuthToken('')
    }
  }, [token])

  const value = useMemo(() => ({ token, setToken }), [token])

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}


