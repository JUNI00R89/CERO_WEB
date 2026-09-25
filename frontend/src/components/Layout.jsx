import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Aurora from '../pages/Aurora'
import { IconLogout } from './icons'

export default function Layout({ title, subtitle, icon, actions, children }) {
  const { usuario, logout } = useAuth()
  const navigate = useNavigate()

  const iniciales = `${usuario?.nombre?.[0] || ''}${usuario?.apellido?.[0] || ''}`.toUpperCase()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="home-container">
      <Aurora />

      <header className="home-header">
        <Link to="/home" className="home-logo">CERO</Link>
        <div className="header-user">
          <span className="header-user-name">{usuario?.nombre} {usuario?.apellido}</span>
          <span className="user-avatar">{iniciales}</span>
          <button type="button" className="btn-logout" onClick={handleLogout}>
            <IconLogout size={14} />
            Salir
          </button>
        </div>
      </header>

      <main className="home-main">
        {(title || actions) && (
          <div className="page-header">
            <div className="page-heading">
              <h1 className="page-title">
                {icon && <span className="page-title-icon">{icon}</span>}
                {title}
              </h1>
              {subtitle && <p className="page-subtext">{subtitle}</p>}
            </div>
            {actions && <div className="page-actions">{actions}</div>}
          </div>
        )}
        {children}
      </main>
    </div>
  )
}