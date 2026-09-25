import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import Layout from '../components/Layout'
import { IconBank, IconSwap, IconTag, IconChart, IconTarget, IconUser, IconShield, IconArrow } from '../components/icons'

const MODULOS = [
  { to: '/cuentas',      Icono: IconBank,   label: 'Cuentas',         desc: 'Gestiona tus cuentas' },
  { to: '/movimientos',  Icono: IconSwap,   label: 'Movimientos',     desc: 'Ingresos y gastos' },
  { to: '/categorias',   Icono: IconTag,    label: 'Categorías',      desc: 'Organiza tus finanzas' },
  { to: '/presupuestos', Icono: IconChart,  label: 'Presupuestos',    desc: 'Controla tu gasto' },
  { to: '/metas-ahorro', Icono: IconTarget, label: 'Metas de ahorro', desc: 'Alcanza tus objetivos' },
  { to: '/perfil',       Icono: IconUser,   label: 'Perfil',          desc: 'Tus datos personales' },
]

const fmt = (v) => `$${parseFloat(v).toFixed(2)}`

export default function Home() {
  const { usuario, rol } = useAuth()
  const [movs, setMovs] = useState([])
  const [categorias, setCategorias] = useState([])

  useEffect(() => {
    const cargar = async () => {
      try {
        const [rm, rcat] = await Promise.all([
          api.get('/movimientos?limit=100&order=desc&sort_by=fecha'),
          api.get('/categorias?limit=100'),
        ])
        setMovs(rm.data.data.items)
        setCategorias(rcat.data.data.items)
      } catch { setMovs([]) }
    }
    cargar()
  }, [])

  const iniciales = `${usuario?.nombre?.[0] || ''}${usuario?.apellido?.[0] || ''}`.toUpperCase()

  const hoy = new Date()
  const esDelMes = (fecha) => {
    const d = new Date(fecha)
    return d.getMonth() === hoy.getMonth() && d.getFullYear() === hoy.getFullYear()
  }
  const delMes = movs.filter(m => esDelMes(m.fecha))
  const ingresos = delMes.filter(m => m.tipo === 'ingreso').reduce((a, m) => a + parseFloat(m.monto), 0)
  const gastos = delMes.filter(m => m.tipo === 'gasto').reduce((a, m) => a + parseFloat(m.monto), 0)
  const balance = ingresos - gastos
  const recientes = movs.slice(0, 5)

  const nombreCategoria = (id) => categorias.find(c => c.id === id)?.nombre || 'Sin categoría'
  const fechaCorta = (fecha) => new Date(fecha).toLocaleDateString('es-ES', { day: '2-digit', month: 'short' })
  const mesNombre = hoy.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })

  return (
    <Layout>
      <div className="greeting-card">
        <div className="user-avatar user-avatar-lg">{iniciales}</div>
        <div className="greeting-text">
          <h1>Hola, {usuario?.nombre} {usuario?.apellido}</h1>
          <p>{usuario?.correo}</p>
        </div>
        <span className={`badge ${rol === 'admin' ? 'badge-purple' : 'badge-neutral'} role-badge`}>
          {rol}
        </span>
      </div>

      <div className="section-label">Módulos</div>

      <div className="card-grid">
        {MODULOS.map(({ to, Icono, label, desc }) => (
          <Link key={to} to={to} className="module-card">
            <span className="module-icon"><Icono /></span>
            <div className="module-text">
              <strong>{label}</strong>
              <span className="module-desc">{desc}</span>
            </div>
            <IconArrow className="module-arrow" />
          </Link>
        ))}

        {rol === 'admin' && (
          <Link to="/admin/usuarios" className="module-card module-card-admin">
            <span className="module-icon"><IconShield /></span>
            <div className="module-text">
              <strong>Usuarios</strong>
              <span className="module-desc">Panel de admin</span>
            </div>
            <IconArrow className="module-arrow" />
          </Link>
        )}
      </div>

      {movs.length > 0 && (
        <section className="quick-section">
          <div className="section-label">Vista rápida · {mesNombre}</div>

          <div className="quick-grid">
            <div className="quick-card">
              <span className="quick-label">Ingresos del mes</span>
              <span className={`quick-value ${ingresos > 0 ? 'text-success' : ''}`}>{ingresos > 0 ? '+' : ''}{fmt(ingresos)}</span>
            </div>
            <div className="quick-card">
              <span className="quick-label">Gastos del mes</span>
              <span className={`quick-value ${gastos > 0 ? 'text-danger' : ''}`}>-{fmt(gastos)}</span>
            </div>
            <div className="quick-card">
              <span className="quick-label">Balance del mes</span>
              <span className={`quick-value ${balance >= 0 ? 'text-success' : 'text-danger'}`}>
                {balance >= 0 ? '+' : '-'}{fmt(Math.abs(balance))}
              </span>
            </div>
          </div>

          <div className="section-label" style={{ marginTop: 28 }}>Movimientos recientes</div>

          <ul className="quick-list">
            {recientes.map(m => (
              <li key={m.id} className="quick-item">
                <span className={`quick-dot ${m.tipo === 'ingreso' ? 'quick-dot-success' : 'quick-dot-danger'}`} />
                <div className="quick-item-main">
                  <strong>{m.descripcion || nombreCategoria(m.categoria_id)}</strong>
                  <span>{nombreCategoria(m.categoria_id)} · {fechaCorta(m.fecha)}</span>
                </div>
                <span className={`quick-amount ${m.tipo === 'ingreso' ? 'text-success' : 'text-danger'}`}>
                  {m.tipo === 'ingreso' ? '+' : '-'}{fmt(m.monto)}
                </span>
              </li>
            ))}
          </ul>

          <Link to="/movimientos" className="quick-link">Ver todos los movimientos →</Link>
        </section>
      )}
    </Layout>
  )
}