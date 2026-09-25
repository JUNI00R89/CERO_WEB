import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'
import Aurora from './Aurora'

export default function Register() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const [nombre, setNombre] = useState('')
  const [apellido, setApellido] = useState('')
  const [correo, setCorreo] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [errors, setErrors] = useState({})
  const [errorApi, setErrorApi] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [loading, setLoading] = useState(false)

  if (isAuthenticated) {
    return <Navigate to="/home" replace />
  }

  const validate = () => {
    const newErrors = {}

    if (!nombre.trim() || nombre.trim().length < 2) {
      newErrors.nombre = 'El nombre debe tener al menos 2 caracteres.'
    }

    if (!apellido.trim() || apellido.trim().length < 2) {
      newErrors.apellido = 'El apellido debe tener al menos 2 caracteres.'
    }

    if (!correo.trim()) {
      newErrors.correo = 'El correo es obligatorio.'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo.trim())) {
      newErrors.correo = 'Ingresa un correo electrónico válido.'
    }

    if (!password) {
      newErrors.password = 'La contraseña es obligatoria.'
    } else if (password.length < 8) {
      newErrors.password = 'La contraseña debe tener al menos 8 caracteres.'
    }

    if (confirmPassword !== password) {
      newErrors.confirmPassword = 'Las contraseñas no coinciden.'
    }

    return newErrors
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrorApi('')
    setSuccessMsg('')

    const newErrors = validate()
    setErrors(newErrors)
    if (Object.keys(newErrors).length > 0) return

    setLoading(true)
    try {
      await api.post('/usuarios', {
        nombre: nombre.trim(),
        apellido: apellido.trim(),
        correo: correo.trim(),
        password,
      })
      setSuccessMsg('Cuenta creada correctamente. Ya puedes iniciar sesión.')
      setTimeout(() => navigate('/login', { replace: true }), 1200)
    } catch (error) {
      const backendMessage = error.response?.data?.detail?.message || error.response?.data?.message
      setErrorApi(backendMessage || 'No se pudo crear la cuenta. Intenta nuevamente.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <Aurora />
      <form className="login-card" onSubmit={handleSubmit} noValidate>
        <h1 className="login-title">CERO</h1>
        <p className="form-subtitle">Crea tu cuenta</p>

        <div className="form-group">
          <label htmlFor="nombre">Nombre</label>
          <input
            id="nombre"
            type="text"
            autoComplete="given-name"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            className={errors.nombre ? 'input-error' : ''}
          />
          {errors.nombre && <p className="field-error">{errors.nombre}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="apellido">Apellido</label>
          <input
            id="apellido"
            type="text"
            autoComplete="family-name"
            value={apellido}
            onChange={(e) => setApellido(e.target.value)}
            className={errors.apellido ? 'input-error' : ''}
          />
          {errors.apellido && <p className="field-error">{errors.apellido}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="correo">Correo electrónico</label>
          <input
            id="correo"
            type="email"
            autoComplete="email"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            className={errors.correo ? 'input-error' : ''}
          />
          {errors.correo && <p className="field-error">{errors.correo}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="password">Contraseña</label>
          <input
            id="password"
            type="password"
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={errors.password ? 'input-error' : ''}
          />
          {errors.password && <p className="field-error">{errors.password}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">Confirmar contraseña</label>
          <input
            id="confirmPassword"
            type="password"
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className={errors.confirmPassword ? 'input-error' : ''}
          />
          {errors.confirmPassword && <p className="field-error">{errors.confirmPassword}</p>}
        </div>

        {errorApi && <p className="auth-error">{errorApi}</p>}
        {successMsg && <p className="success-msg">{successMsg}</p>}

        <button type="submit" className="btn-login" disabled={loading}>
          {loading ? 'Creando cuenta...' : 'Registrarme'}
        </button>

        <p className="form-footer">
          ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
        </p>
      </form>
    </div>
  )
}
