import { createContext, useContext, useEffect, useState } from 'react'
import api from '../api/axios'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchProfile = async () => {
    try {
      const { data } = await api.get('/profile/')
      setUser(data)
      return data
    } catch (err) {
      setUser(null)
      return null
    }
  }

  useEffect(() => {
    // On first load, check if the httpOnly cookies still represent a
    // valid session by asking the protected profile endpoint.
    fetchProfile().finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    await api.post('/login/', { email, password })
    const profile = await fetchProfile()
    return profile
  }

  const logout = async () => {
    try {
      await api.post('/logout/')
    } finally {
      setUser(null)
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshProfile: fetchProfile }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
