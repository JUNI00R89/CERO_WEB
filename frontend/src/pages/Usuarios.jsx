import { useEffect, useState } from 'react'
import api from '../services/api'
import Layout from '../components/Layout'
import { IconShield, IconPower, IconEdit, IconTrash } from '../components/icons'

const VACIO_EDIT = { nombre: '', apellido: '', correo: '', rol: 'usuario', activo: true, password: '' }

export default function Usuarios() {
  const [lista, setLista] = useState([])
  const [modal, setModal] = useState(false)
  const [form, setForm] = useState(VACIO_EDIT)
  const [editId, setEditId] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [pagina, setPagina] = useState(1)
  const [total, setTotal] = useState(0)
  const LIMIT = 10

  const cargar = async (p = pagina) => {
    try {
      const r = await api.get(`/usuarios?page=${p}&limit=${LIMIT}`)
      setLista(r.data.data.items)
      setTotal(r.data.data.total)
    } catch { setLista([]) }
  }
  useEffect(() => { cargar() }, [pagina])

  const abrirEditar = (u) => {
    setForm({ nombre: u.nombre, apellido: u.apellido, correo: u.correo, rol: u.rol, activo: u.activo, password: '' })
    setEditId(u.id); setError(''); setModal(true)
  }
  const cerrar = () => { setModal(false); setEditId(null) }

  const guardar = async () => {
    setError(''); setLoading(true)
    try {
      const payload = { nombre: form.nombre, apellido: form.apellido, correo: form.correo, rol: form.rol, activo: form.activo }
      if (form.password) payload.password = form.password
      await api.put(`/usuarios/${editId}`, payload)
      await cargar(); cerrar()
    } catch (e) { setError(e.response?.data?.detail?.message || 'Error al guardar') }
    finally { setLoading(false) }
  }

  const toggleActivo = async (u) => {
    try { await api.put(`/usuarios/${u.id}`, { activo: !u.activo }); await cargar() }
    catch (e) { alert(e.response?.data?.detail?.message || 'Error') }
  }

  const eliminar = async (id) => {
    if (!confirm('¿Eliminar este usuario? Esta acción no se puede deshacer.')) return
    try { await api.delete(`/usuarios/${id}`); await cargar() }
    catch (e) { alert(e.response?.data?.detail?.message || 'Error al eliminar') }
  }

  const totalPaginas = Math.ceil(total / LIMIT)

  return (
    <Layout
      title="Usuarios"
      subtitle={`${total} usuario${total !== 1 ? 's' : ''} registrados en la plataforma`}
      icon={<IconShield />}
    >
      <div className="table-wrap">
        <table className="data-table">
          <thead><tr>
            {['Nombre', 'Correo', 'Rol', 'Estado', 'Miembro desde', 'Acciones'].map(h => <th key={h}>{h}</th>)}
          </tr></thead>
          <tbody>
            {lista.map(u => (
              <tr key={u.id}>
                <td><strong>{u.nombre} {u.apellido}</strong></td>
                <td>{u.correo}</td>
                <td>
                  <span className={`badge ${u.rol === 'admin' ? 'badge-purple' : 'badge-neutral'}`}>
                    {u.rol}
                  </span>
                </td>
                <td>
                  <span className={`badge ${u.activo ? 'badge-success' : 'badge-danger'}`}>
                    {u.activo ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td>{u.fecha_creacion?.slice(0, 10)}</td>
                <td>
                  <button onClick={() => abrirEditar(u)} className="btn btn-sm"><IconEdit size={13} /> Editar</button>
                  <button onClick={() => toggleActivo(u)} className="btn btn-warning"><IconPower size={13} /> {u.activo ? 'Desactivar' : 'Activar'}</button>
                  <button onClick={() => eliminar(u.id)} className="btn btn-danger"><IconTrash size={13} /> Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {lista.length === 0 && (
        <div className="empty-state">
          <span className="empty-icon"><IconShield /></span>
          <strong>No se encontraron usuarios</strong>
        </div>
      )}

      {totalPaginas > 1 && (
        <div className="pagination">
          <button onClick={() => setPagina(p => Math.max(1, p - 1))} disabled={pagina === 1} className="btn btn-secondary">‹ Anterior</button>
          <span>Página {pagina} de {totalPaginas}</span>
          <button onClick={() => setPagina(p => Math.min(totalPaginas, p + 1))} disabled={pagina === totalPaginas} className="btn btn-secondary">Siguiente ›</button>
        </div>
      )}

      {modal && (
        <div className="modal-overlay">
          <div className="modal-box">
            <h2>Editar usuario</h2>
            {error && <p className="field-error-box">{error}</p>}

            <label className="field-label">Nombre</label>
            <input className="field-input" value={form.nombre} onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))} />

            <label className="field-label">Apellido</label>
            <input className="field-input" value={form.apellido} onChange={e => setForm(f => ({ ...f, apellido: e.target.value }))} />

            <label className="field-label">Correo</label>
            <input type="email" className="field-input" value={form.correo} onChange={e => setForm(f => ({ ...f, correo: e.target.value }))} />

            <label className="field-label">Rol</label>
            <select className="field-input" value={form.rol} onChange={e => setForm(f => ({ ...f, rol: e.target.value }))}>
              <option value="usuario">usuario</option>
              <option value="admin">admin</option>
            </select>

            <label className="field-label" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <input type="checkbox" checked={form.activo} onChange={e => setForm(f => ({ ...f, activo: e.target.checked }))} />
              Usuario activo
            </label>

            <label className="field-label" style={{ marginTop: 12 }}>Nueva contraseña <span className="field-hint">(opcional)</span></label>
            <input type="password" className="field-input" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} />

            <div className="modal-actions">
              <button onClick={cerrar} className="btn btn-secondary">Cancelar</button>
              <button onClick={guardar} disabled={loading} className="btn btn-primary">{loading ? 'Guardando...' : 'Guardar'}</button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}