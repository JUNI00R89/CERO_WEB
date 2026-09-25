import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import Layout from '../components/Layout'
import { IconUser, IconEdit, IconMail, IconCheck, IconInfo } from '../components/icons'

export default function Perfil() {
  const { usuario, fetchUsuario } = useAuth()
  const [editando, setEditando] = useState(false)
  const [form, setForm] = useState({ nombre: '', apellido: '', correo: '', password: '' })
  const [error, setError] = useState('')
  const [ok, setOk] = useState('')
  const [loading, setLoading] = useState(false)

  const iniciarEdicion = () => {
    setForm({ nombre: usuario.nombre, apellido: usuario.apellido, correo: usuario.correo, password: '' })
    setError(''); setOk(''); setEditando(true)
  }

  const guardar = async () => {
    setError(''); setOk(''); setLoading(true)
    try {
      const payload = { nombre: form.nombre, apellido: form.apellido, correo: form.correo }
      if (form.password) payload.password = form.password
      await api.put(`/usuarios/${usuario.id}`, payload)
      await fetchUsuario()
      setOk('Perfil actualizado correctamente.')
      setEditando(false)
    } catch (e) { setError(e.response?.data?.detail?.message || 'Error al guardar') }
    finally { setLoading(false) }
  }

  if (!usuario) return null

  const iniciales = `${usuario.nombre?.[0] || ''}${usuario.apellido?.[0] || ''}`.toUpperCase()

  return (
    <Layout
      title="Mi perfil"
      subtitle="Tus datos personales y preferencias"
      icon={<IconUser />}
    >
      <div className="card profile-card">
        <div className="profile-head">
          <span className="user-avatar user-avatar-lg">{iniciales}</span>
          <div>
            <strong>{usuario.nombre} {usuario.apellido}</strong>
            <span className="profile-mail"><IconMail size={12} /> {usuario.correo}</span>
          </div>
        </div>

        {ok && <p className="field-ok-box"><IconCheck size={13} /> {ok}</p>}
        {error && <p className="field-error-box">{error}</p>}

        {!editando ? (
          <>
            <Row label="Nombre" value={`${usuario.nombre} ${usuario.apellido}`} />
            <Row label="Correo" value={usuario.correo} />
            <Row label="Rol" value={<span className={`badge ${usuario.rol === 'admin' ? 'badge-purple' : 'badge-neutral'}`}>{usuario.rol}</span>} />
            <Row label="Activo" value={usuario.activo ? 'Sí' : 'No'} />
            <Row label="Miembro desde" value={usuario.fecha_creacion?.slice(0, 10)} />
            <button onClick={iniciarEdicion} className="btn btn-primary" style={{ marginTop: 20 }}>
              <IconEdit size={15} /> Editar perfil
            </button>
          </>
        ) : (
          <>
            <label className="field-label">Nombre</label>
            <input className="field-input" value={form.nombre} onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))} />

            <label className="field-label">Apellido</label>
            <input className="field-input" value={form.apellido} onChange={e => setForm(f => ({ ...f, apellido: e.target.value }))} />

            <label className="field-label">Correo</label>
            <input type="email" className="field-input" value={form.correo} onChange={e => setForm(f => ({ ...f, correo: e.target.value }))} />

            <label className="field-label">Nueva contraseña <span className="field-hint">(dejar vacío para no cambiar)</span></label>
            <input type="password" className="field-input" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} />

            <div className="modal-actions" style={{ justifyContent: 'flex-start' }}>
              <button onClick={() => setEditando(false)} className="btn btn-secondary">Cancelar</button>
              <button onClick={guardar} disabled={loading} className="btn btn-primary">{loading ? 'Guardando...' : 'Guardar'}</button>
            </div>
          </>
        )}
      </div>

      <p className="profile-note"><IconInfo size={12} /> Tus credenciales están protegidas y se usan para autenticarte en cada operación.</p>
    </Layout>
  )
}

function Row({ label, value }) {
  return (
    <div className="profile-row">
      <span className="label">{label}</span>
      <span className="value">{value}</span>
    </div>
  )
}