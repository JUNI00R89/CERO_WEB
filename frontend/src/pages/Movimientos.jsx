import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import Layout from '../components/Layout'
import { IconSwap, IconPlus, IconEdit, IconTrash, IconTag } from '../components/icons'

const VACIO = { tipo: 'gasto', monto: '', descripcion: '', cuenta_id: '', categoria_id: '' }

export default function Movimientos() {
  const { usuario } = useAuth()
  const [lista, setLista] = useState([])
  const [cuentas, setCuentas] = useState([])
  const [categorias, setCategorias] = useState([])
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(VACIO)
  const [editId, setEditId] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const cargar = async () => {
    try {
      const [rm, rc, rcat] = await Promise.all([
        api.get('/movimientos?limit=100&order=desc'),
        api.get('/cuentas?limit=100'),
        api.get('/categorias?limit=100'),
      ])
      setLista(rm.data.data.items)
      setCuentas(rc.data.data.items)
      setCategorias(rcat.data.data.items)
    } catch { setLista([]) }
  }
  useEffect(() => { cargar() }, [])

  const abrirCrear = () => { setForm(VACIO); setError(''); setModal('crear') }
  const abrirEditar = (m) => {
    setForm({ tipo: m.tipo, monto: m.monto, descripcion: m.descripcion || '', cuenta_id: m.cuenta_id, categoria_id: m.categoria_id })
    setEditId(m.id); setError(''); setModal('editar')
  }
  const cerrar = () => { setModal(null); setEditId(null) }

  const guardar = async () => {
    setError(''); setLoading(true)
    try {
      const payload = {
        tipo: form.tipo,
        monto: parseFloat(form.monto),
        descripcion: form.descripcion || null,
        cuenta_id: parseInt(form.cuenta_id),
        categoria_id: parseInt(form.categoria_id),
        usuario_id: usuario.id,
      }
      if (modal === 'crear') await api.post('/movimientos', payload)
      else await api.put(`/movimientos/${editId}`, payload)
      await cargar(); cerrar()
    } catch (e) { setError(e.response?.data?.detail?.message || 'Error al guardar') }
    finally { setLoading(false) }
  }

  const eliminar = async (id) => {
    if (!confirm('¿Eliminar este movimiento?')) return
    try { await api.delete(`/movimientos/${id}`); await cargar() }
    catch (e) { alert(e.response?.data?.detail?.message || 'Error') }
  }

  const nombreCuenta = (id) => cuentas.find(c => c.id === id)?.nombre || id
  const nombreCategoria = (id) => categorias.find(c => c.id === id)?.nombre || id

  const ingresos = lista.filter(m => m.tipo === 'ingreso').reduce((a, m) => a + (parseFloat(m.monto) || 0), 0)
  const gastos = lista.filter(m => m.tipo === 'gasto').reduce((a, m) => a + (parseFloat(m.monto) || 0), 0)

  return (
    <Layout
      title="Movimientos"
      subtitle="Registra tus ingresos y gastos"
      icon={<IconSwap />}
      actions={
        <button onClick={abrirCrear} className="btn btn-primary"><IconPlus size={15} /> Nuevo movimiento</button>
      }
    >
      {lista.length > 0 && (
        <div className="summary-strip">
          <span><span className="badge badge-success" style={{ marginRight: 8 }}>+ ${ingresos.toFixed(2)}</span><span className="badge badge-danger">- ${gastos.toFixed(2)}</span></span>
          <span className="summary-total text-success">Neto ${(ingresos - gastos).toFixed(2)}</span>
        </div>
      )}

      {lista.length === 0
        ? (
          <div className="empty-state">
            <span className="empty-icon"><IconSwap /></span>
            <strong>Sin movimientos aún</strong>
            <p>Registra el primero para llevar el control de tu dinero.</p>
          </div>
        )
        : (
          <div className="table-wrap">
            <table className="data-table">
              <thead><tr>
                {['Tipo', 'Monto', 'Cuenta', 'Categoría', 'Descripción', 'Acciones'].map(h => <th key={h}>{h}</th>)}
              </tr></thead>
              <tbody>
                {lista.map(m => (
                  <tr key={m.id}>
                    <td>
                      <span className={`badge ${m.tipo === 'ingreso' ? 'badge-success' : 'badge-danger'}`}>
                        {m.tipo}
                      </span>
                    </td>
                    <td className={`${m.tipo === 'ingreso' ? 'text-success' : 'text-danger'}`}>
                      {m.tipo === 'ingreso' ? '+' : '-'}${parseFloat(m.monto).toFixed(2)}
                    </td>
                    <td>{nombreCuenta(m.cuenta_id)}</td>
                    <td>
                      <span className="table-muted"><IconTag size={12} /> {nombreCategoria(m.categoria_id)}</span>
                    </td>
                    <td>{m.descripcion || '—'}</td>
                    <td>
                      <button onClick={() => abrirEditar(m)} className="btn btn-sm"><IconEdit size={13} /> Editar</button>
                      <button onClick={() => eliminar(m.id)} className="btn btn-danger"><IconTrash size={13} /> Eliminar</button>
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
            <h2>{modal === 'crear' ? 'Nuevo movimiento' : 'Editar movimiento'}</h2>
            {error && <p className="field-error-box">{error}</p>}

            <label className="field-label">Tipo</label>
            <select className="field-input" value={form.tipo} onChange={e => setForm(f => ({ ...f, tipo: e.target.value }))}>
              <option value="ingreso">Ingreso</option>
              <option value="gasto">Gasto</option>
            </select>

            <label className="field-label">Monto</label>
            <input type="number" step="0.01" className="field-input" value={form.monto} onChange={e => setForm(f => ({ ...f, monto: e.target.value }))} />

            <label className="field-label">Cuenta</label>
            <select className="field-input" value={form.cuenta_id} onChange={e => setForm(f => ({ ...f, cuenta_id: e.target.value }))}>
              <option value="">— Selecciona una cuenta —</option>
              {cuentas.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
            </select>

            <label className="field-label">Categoría</label>
            <select className="field-input" value={form.categoria_id} onChange={e => setForm(f => ({ ...f, categoria_id: e.target.value }))}>
              <option value="">— Selecciona una categoría —</option>
              {categorias.map(c => <option key={c.id} value={c.id}>{c.nombre} ({c.tipo})</option>)}
            </select>

            <label className="field-label">Descripción (opcional)</label>
            <input className="field-input" value={form.descripcion} onChange={e => setForm(f => ({ ...f, descripcion: e.target.value }))} />

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