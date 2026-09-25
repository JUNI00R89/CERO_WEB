import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import Layout from '../components/Layout'
import { IconChart, IconPlus, IconEdit, IconTrash, IconCalendar, IconTag } from '../components/icons'

const VACIO = { monto_limite: '', fecha_inicio: '', fecha_fin: '', categoria_id: '' }

export default function Presupuestos() {
  const { usuario } = useAuth()
  const [lista, setLista] = useState([])
  const [categorias, setCategorias] = useState([])
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(VACIO)
  const [editId, setEditId] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const cargar = async () => {
    try {
      const [rp, rc] = await Promise.all([
        api.get('/presupuestos?limit=100'),
        api.get('/categorias?limit=100'),
      ])
      setLista(rp.data.data.items)
      setCategorias(rc.data.data.items)
    } catch { setLista([]) }
  }
  useEffect(() => { cargar() }, [])

  const abrirCrear = () => { setForm(VACIO); setError(''); setModal('crear') }
  const abrirEditar = (p) => {
    setForm({ monto_limite: p.monto_limite, fecha_inicio: p.fecha_inicio, fecha_fin: p.fecha_fin, categoria_id: p.categoria_id })
    setEditId(p.id); setError(''); setModal('editar')
  }
  const cerrar = () => { setModal(null); setEditId(null) }

  const guardar = async () => {
    setError(''); setLoading(true)
    try {
      const payload = {
        monto_limite: parseFloat(form.monto_limite),
        fecha_inicio: form.fecha_inicio,
        fecha_fin: form.fecha_fin,
        categoria_id: parseInt(form.categoria_id),
        usuario_id: usuario.id,
      }
      if (modal === 'crear') await api.post('/presupuestos', payload)
      else await api.put(`/presupuestos/${editId}`, payload)
      await cargar(); cerrar()
    } catch (e) { setError(e.response?.data?.detail?.message || 'Error al guardar') }
    finally { setLoading(false) }
  }

  const eliminar = async (id) => {
    if (!confirm('¿Eliminar este presupuesto?')) return
    try { await api.delete(`/presupuestos/${id}`); await cargar() }
    catch (e) { alert(e.response?.data?.detail?.message || 'Error') }
  }

  const nombreCategoria = (id) => categorias.find(c => c.id === id)?.nombre || id
  const totalLimites = lista.reduce((a, p) => a + (parseFloat(p.monto_limite) || 0), 0)

  return (
    <Layout
      title="Presupuestos"
      subtitle="Controla tu gasto por categoría"
      icon={<IconChart />}
      actions={
        <button onClick={abrirCrear} className="btn btn-primary"><IconPlus size={15} /> Nuevo presupuesto</button>
      }
    >
      {lista.length > 1 && (
        <div className="summary-strip">
          <span>{lista.length} presupuestos activos</span>
          <span className="summary-total">Total límite ${totalLimites.toFixed(2)}</span>
        </div>
      )}

      {lista.length === 0
        ? (
          <div className="empty-state">
            <span className="empty-icon"><IconChart /></span>
            <strong>Sin presupuestos aún</strong>
            <p>Define límites por categoría para mantener el control.</p>
          </div>
        )
        : (
          <div className="table-wrap">
            <table className="data-table">
              <thead><tr>
                {['Categoría', 'Límite', 'Desde', 'Hasta', 'Acciones'].map(h => <th key={h}>{h}</th>)}
              </tr></thead>
              <tbody>
                {lista.map(p => (
                  <tr key={p.id}>
                    <td><span className="table-muted"><IconTag size={12} /> {nombreCategoria(p.categoria_id)}</span></td>
                    <td className="text-success">${parseFloat(p.monto_limite).toFixed(2)}</td>
                    <td><span className="table-muted"><IconCalendar size={12} /> {p.fecha_inicio}</span></td>
                    <td><span className="table-muted"><IconCalendar size={12} /> {p.fecha_fin}</span></td>
                    <td>
                      <button onClick={() => abrirEditar(p)} className="btn btn-sm"><IconEdit size={13} /> Editar</button>
                      <button onClick={() => eliminar(p.id)} className="btn btn-danger"><IconTrash size={13} /> Eliminar</button>
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
            <h2>{modal === 'crear' ? 'Nuevo presupuesto' : 'Editar presupuesto'}</h2>
            {error && <p className="field-error-box">{error}</p>}

            <label className="field-label">Categoría</label>
            <select className="field-input" value={form.categoria_id} onChange={e => setForm(f => ({ ...f, categoria_id: e.target.value }))}>
              <option value="">— Selecciona una categoría —</option>
              {categorias.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.tipo})</option>)}
            </select>

            <label className="field-label">Monto límite</label>
            <input type="number" step="0.01" className="field-input" value={form.monto_limite} onChange={e => setForm(f => ({ ...f, monto_limite: e.target.value }))} />

            <label className="field-label">Fecha inicio</label>
            <input type="date" className="field-input" value={form.fecha_inicio} onChange={e => setForm(f => ({ ...f, fecha_inicio: e.target.value }))} />

            <label className="field-label">Fecha fin</label>
            <input type="date" className="field-input" value={form.fecha_fin} onChange={e => setForm(f => ({ ...f, fecha_fin: e.target.value }))} />

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