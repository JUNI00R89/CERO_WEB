import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Aurora from './Aurora'

export default function Login() {
  const { isAuthenticated, login, loading } = useAuth()
  const navigate = useNavigate()

  const [correo, setCorreo] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})
  const [errorAuth, setErrorAuth] = useState('')

  if (isAuthenticated) {
    return <Navigate to="/home" replace />
  }

  const validate = () => {
    const newErrors = {}

    if (!correo.trim()) {
      newErrors.correo = 'El correo es obligatorio.'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo.trim())) {
      newErrors.correo = 'Ingresa un correo electrónico válido.'
    }

    if (!password) {
      newErrors.password = 'La contraseña es obligatoria.'
    }

    return newErrors
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrorAuth('')

    const newErrors = validate()
    setErrors(newErrors)
    if (Object.keys(newErrors).length > 0) return

    const result = await login({ correo: correo.trim(), password })
    if (result.success) {
      navigate('/home', { replace: true })
    } else {
      setErrorAuth(result.message)
    }
  }

  return (
    <div className="login-container">
      <Aurora />
      <form className="login-card" onSubmit={handleSubmit} noValidate>
        <h1 className="login-title">CERO</h1>

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
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={errors.password ? 'input-error' : ''}
          />
          {errors.password && <p className="field-error">{errors.password}</p>}
        </div>

        {errorAuth && <p className="auth-error">{errorAuth}</p>}

        <button type="submit" className="btn-login" disabled={loading}>
          {loading ? 'Ingresando...' : 'Ingresar'}
        </button>

        <p className="form-footer">
          ¿No tienes cuenta? <Link to="/register">Regístrate</Link>
        </p>
      </form>
    </div>
  )
}
