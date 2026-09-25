import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import Layout from '../components/Layout'
import { IconTag, IconPlus, IconEdit, IconTrash } from '../components/icons'

const TIPOS = ['ingreso', 'gasto']
const VACIO = { nombre: '', tipo: 'gasto' }

export default function Categorias() {
  const { usuario } = useAuth()
  const [lista, setLista] = useState([])
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(VACIO)
  const [editId, setEditId] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const cargar = async () => {
    try { const r = await api.get('/categorias?limit=100'); setLista(r.data.data.items) }
    catch { setLista([]) }
  }
  useEffect(() => { cargar() }, [])

  const abrirCrear = () => { setForm(VACIO); setError(''); setModal('crear') }
  const abrirEditar = (c) => { setForm({ nombre: c.nombre, tipo: c.tipo }); setEditId(c.id); setError(''); setModal('editar') }
  const cerrar = () => { setModal(null); setEditId(null) }

  const guardar = async () => {
    setError(''); setLoading(true)
    try {
      const payload = { ...form, usuario_id: usuario.id }
      if (modal === 'crear') await api.post('/categorias', payload)
      else await api.put(`/categorias/${editId}`, payload)
      await cargar(); cerrar()
    } catch (e) { setError(e.response?.data?.detail?.message || 'Error al guardar') }
    finally { setLoading(false) }
  }

  const eliminar = async (id) => {
    if (!confirm('¿Eliminar esta categoría?')) return
    try { await api.delete(`/categorias/${id}`); await cargar() }
    catch (e) { alert(e.response?.data?.detail?.message || 'Error al eliminar') }
  }

  const ingresos = lista.filter(c => c.tipo === 'ingreso').length
  const gastos = lista.filter(c => c.tipo === 'gasto').length

  return (
    <Layout
      title="Categorías"
      subtitle="Organiza tus finanzas con categorías claras"
      icon={<IconTag />}
      actions={
        <button onClick={abrirCrear} className="btn btn-primary"><IconPlus size={15} /> Nueva categoría</button>
      }
    >
      {lista.length > 1 && (
        <div className="summary-strip">
          <span>{lista.length} categorías</span>
          <span><span className="badge badge-success" style={{ marginRight: 8 }}>{ingresos} de ingreso</span><span className="badge badge-danger">{gastos} de gasto</span></span>
        </div>
      )}

      {lista.length === 0
        ? (
          <div className="empty-state">
            <span className="empty-icon"><IconTag /></span>
            <strong>Sin categorías todavía</strong>
            <p>Crea categorías para clasificar tus movimientos.</p>
          </div>
        )
        : (
          <div className="table-wrap">
            <table className="data-table">
              <thead><tr>
                {['Nombre', 'Tipo', 'Acciones'].map(h => <th key={h}>{h}</th>)}
              </tr></thead>
              <tbody>
                {lista.map(c => (
                  <tr key={c.id}>
                    <td>{c.nombre}</td>
                    <td>
                      <span className={`badge ${c.tipo === 'ingreso' ? 'badge-success' : 'badge-danger'}`}>
                        {c.tipo}
                      </span>
                    </td>
                    <td>
                      <button onClick={() => abrirEditar(c)} className="btn btn-sm"><IconEdit size={13} /> Editar</button>
                      <button onClick={() => eliminar(c.id)} className="btn btn-danger"><IconTrash size={13} /> Eliminar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

      {modal && (
        <div className="modal-overlay">
          <div className="modal-box">
            <h2>{modal === 'crear' ? 'Nueva categoría' : 'Editar categoría'}</h2>
            {error && <p className="field-error-box">{error}</p>}
            <label className="field-label">Nombre</label>
            <input className="field-input" value={form.nombre} onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))} />
            <label className="field-label">Tipo</label>
            <select className="field-input" value={form.tipo} onChange={e => setForm(f => ({ ...f, tipo: e.target.value }))}>
              {TIPOS.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
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