import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import Layout from '../components/Layout'
import { IconWallet, IconPlus, IconEdit, IconTrash } from '../components/icons'

const TIPOS = ['efectivo', 'tarjeta', 'ahorro', 'inversion', 'credito']
const VACIO = { nombre: '', tipo: 'efectivo', saldo: '' }

export default function Cuentas() {
  const { usuario } = useAuth()
  const [cuentas, setCuentas] = useState([])
  const [modal, setModal] = useState(null)      // null | 'crear' | 'editar'
  const [form, setForm] = useState(VACIO)
  const [editId, setEditId] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const cargar = async () => {
    try {
      const res = await api.get('/cuentas?limit=100')
      setCuentas(res.data.data.items)
    } catch { setCuentas([]) }
  }

  useEffect(() => { cargar() }, [])

  const abrirCrear = () => { setForm(VACIO); setError(''); setModal('crear') }
  const abrirEditar = (c) => {
    setForm({ nombre: c.nombre, tipo: c.tipo, saldo: c.saldo })
    setEditId(c.id); setError(''); setModal('editar')
  }
  const cerrar = () => { setModal(null); setEditId(null) }

  const guardar = async () => {
    setError(''); setLoading(true)
    try {
      const payload = { nombre: form.nombre, tipo: form.tipo, saldo: parseFloat(form.saldo) || 0, usuario_id: usuario.id }
      if (modal === 'crear') await api.post('/cuentas', payload)
      else await api.put(`/cuentas/${editId}`, payload)
      await cargar(); cerrar()
    } catch (e) {
      setError(e.response?.data?.detail?.message || 'Error al guardar')
    } finally { setLoading(false) }
  }

  const eliminar = async (id) => {
    if (!confirm('¿Eliminar esta cuenta?')) return
    try { await api.delete(`/cuentas/${id}`); await cargar() }
    catch (e) { alert(e.response?.data?.detail?.message || 'Error al eliminar') }
  }

  const total = cuentas.reduce((acc, c) => acc + (parseFloat(c.saldo) || 0), 0)

  return (
    <Layout
      title="Cuentas"
      subtitle="Administra tus cuentas financieras"
      icon={<IconWallet />}
      actions={
        <button onClick={abrirCrear} className="btn btn-primary"><IconPlus size={15} /> Nueva cuenta</button>
      }
    >
      {cuentas.length > 1 && (
        <div className="summary-strip">
          <span>{cuentas.length} cuentas</span>
          <span className="summary-total text-success">Saldo total ${total.toFixed(2)}</span>
        </div>
      )}

      {cuentas.length === 0
        ? (
          <div className="empty-state">
            <span className="empty-icon"><IconWallet /></span>
            <strong>Sin cuentas todavía</strong>
            <p>Crea tu primera cuenta para empezar a organizar tu dinero.</p>
          </div>
        )
        : (
          <div className="table-wrap">
            <table className="data-table">
              <thead><tr>
                {['Nombre', 'Tipo', 'Saldo', 'Acciones'].map(h => <th key={h}>{h}</th>)}
              </tr></thead>
              <tbody>
                {cuentas.map(c => (
                  <tr key={c.id}>
                    <td>{c.nombre}</td>
                    <td><span className="badge">{c.tipo}</span></td>
                    <td className="text-success">${parseFloat(c.saldo).toFixed(2)}</td>
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
            <h2>{modal === 'crear' ? 'Nueva cuenta' : 'Editar cuenta'}</h2>
            {error && <p className="field-error-box">{error}</p>}
            <label className="field-label">Nombre</label>
            <input className="field-input" value={form.nombre} onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))} />
            <label className="field-label">Tipo</label>
            <select className="field-input" value={form.tipo} onChange={e => setForm(f => ({ ...f, tipo: e.target.value }))}>
              {TIPOS.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <label className="field-label">Saldo</label>
            <input type="number" className="field-input" value={form.saldo} onChange={e => setForm(f => ({ ...f, saldo: e.target.value }))} />
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