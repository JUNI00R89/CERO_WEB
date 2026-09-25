import { Navigate, Route, Routes } from 'react-router-dom'
import Login from '../pages/Login'
import Register from '../pages/Register'
import Home from '../pages/Home'
import Cuentas from '../pages/Cuentas'
import Categorias from '../pages/Categorias'
import Movimientos from '../pages/Movimientos'
import Presupuestos from '../pages/Presupuestos'
import MetasAhorro from '../pages/MetasAhorro'
import Perfil from '../pages/Perfil'
import Usuarios from '../pages/Usuarios'
import { useAuth } from '../context/AuthContext'

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

function AdminRoute({ children }) {
  const { isAuthenticated, rol } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (rol !== 'admin') return <Navigate to="/home" replace />
  return children
}

export default function AppRoutes() {
  const { isAuthenticated } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to="/home" replace /> : <Login />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to="/home" replace /> : <Register />} />
      <Route path="/home" element={<ProtectedRoute><Home /></ProtectedRoute>} />
      <Route path="/cuentas" element={<ProtectedRoute><Cuentas /></ProtectedRoute>} />
      <Route path="/categorias" element={<ProtectedRoute><Categorias /></ProtectedRoute>} />
      <Route path="/movimientos" element={<ProtectedRoute><Movimientos /></ProtectedRoute>} />
      <Route path="/presupuestos" element={<ProtectedRoute><Presupuestos /></ProtectedRoute>} />
      <Route path="/metas-ahorro" element={<ProtectedRoute><MetasAhorro /></ProtectedRoute>} />
      <Route path="/perfil" element={<ProtectedRoute><Perfil /></ProtectedRoute>} />
      <Route path="/admin/usuarios" element={<AdminRoute><Usuarios /></AdminRoute>} />
      <Route path="*" element={<Navigate to={isAuthenticated ? '/home' : '/login'} replace />} />
    </Routes>
  )
}