import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

function getToken() {
  return localStorage.getItem('access_token')
}

function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem('usuario'))
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(getToken())
  const [usuario, setUsuario] = useState(getStoredUser())
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(getToken()))
  const [loading, setLoading] = useState(false)

  const login = useCallback(async ({ correo, password }) => {
    setLoading(true)
    try {
      const response = await api.post('/login', { correo, password })
      const { access_token } = response.data.data
      localStorage.setItem('access_token', access_token)
      setToken(access_token)
      setIsAuthenticated(true)
      await fetchUsuario()
      return { success: true }
    } catch (error) {
      setToken(null)
      setIsAuthenticated(false)
      localStorage.removeItem('access_token')
      localStorage.removeItem('usuario')
      const backendMessage = error.response?.data?.detail?.message || error.response?.data?.message
      const message = backendMessage || 'Correo o contraseña incorrectos.'
      return { success: false, message }
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchUsuario = useCallback(async () => {
    try {
      const response = await api.get('/usuarios/me')
      const data = response.data.data
      localStorage.setItem('usuario', JSON.stringify(data))
      setUsuario(data)
    } catch {
      setUsuario(null)
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('usuario')
    setToken(null)
    setUsuario(null)
    setIsAuthenticated(false)
  }, [])

  useEffect(() => {
    if (token && !usuario) {
      fetchUsuario()
    }
  }, [token, usuario, fetchUsuario])

  const value = {
    token,
    usuario,
    isAuthenticated,
    loading,
    rol: usuario?.rol || null,
    login,
    logout,
    fetchUsuario,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider')
  }
  return context
}