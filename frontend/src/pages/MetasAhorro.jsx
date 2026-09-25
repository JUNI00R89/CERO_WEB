import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import Layout from '../components/Layout'
import { IconTarget, IconPlus, IconEdit, IconTrash, IconCalendar } from '../components/icons'

const VACIO = { nombre: '', monto_objetivo: '', monto_actual: '0', fecha_objetivo: '' }

export default function MetasAhorro() {
  const { usuario } = useAuth()
  const [lista, setLista] = useState([])
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(VACIO)
  const [editId, setEditId] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const cargar = async () => {
    try { const r = await api.get('/metas-ahorro?limit=100'); setLista(r.data.data.items) }
    catch { setLista([]) }
  }
  useEffect(() => { cargar() }, [])

  const abrirCrear = () => { setForm(VACIO); setError(''); setModal('crear') }
  const abrirEditar = (m) => {
    setForm({ nombre: m.nombre, monto_objetivo: m.monto_objetivo, monto_actual: m.monto_actual, fecha_objetivo: m.fecha_objetivo })
    setEditId(m.id); setError(''); setModal('editar')
  }
  const cerrar = () => { setModal(null); setEditId(null) }

  const guardar = async () => {
    setError(''); setLoading(true)
    try {
      const payload = {
        nombre: form.nombre,
        monto_objetivo: parseFloat(form.monto_objetivo),
        monto_actual: parseFloat(form.monto_actual) || 0,
        fecha_objetivo: form.fecha_objetivo,
        usuario_id: usuario.id,
      }
      if (modal === 'crear') await api.post('/metas-ahorro', payload)
      else await api.put(`/metas-ahorro/${editId}`, payload)
      await cargar(); cerrar()
    } catch (e) { setError(e.response?.data?.detail?.message || 'Error al guardar') }
    finally { setLoading(false) }
  }

  const eliminar = async (id) => {
    if (!confirm('¿Eliminar esta meta?')) return
    try { await api.delete(`/metas-ahorro/${id}`); await cargar() }
    catch (e) { alert(e.response?.data?.detail?.message || 'Error') }
  }

  const progreso = (m) => {
    const pct = Math.min(100, (parseFloat(m.monto_actual) / parseFloat(m.monto_objetivo)) * 100)
    return isNaN(pct) ? 0 : pct
  }

  return (
    <Layout
      title="Metas de ahorro"
      subtitle="Alcanza tus objetivos financieros"
      icon={<IconTarget />}
      actions={
        <button onClick={abrirCrear} className="btn btn-primary"><IconPlus size={15} /> Nueva meta</button>
      }
    >
      {lista.length === 0
        ? (
          <div className="empty-state">
            <span className="empty-icon"><IconTarget /></span>
            <strong>Sin metas de ahorro aún</strong>
            <p>Define una meta y empieza a ahorrar para lograrla.</p>
          </div>
        )
        : (
          <div className="goal-grid">
            {lista.map(m => {
              const pct = progreso(m)
              return (
                <div key={m.id} className="goal-card">
                  <div className="goal-card-top">
                    <div className="goal-heading">
                      <span className="module-icon"><IconTarget /></span>
                      <strong>{m.nombre}</strong>
                    </div>
                    <span className="goal-date"><IconCalendar size={12} /> {m.fecha_objetivo}</span>
                  </div>
                  <div className="goal-amounts">
                    ${parseFloat(m.monto_actual).toFixed(2)} / ${parseFloat(m.monto_objetivo).toFixed(2)}
                  </div>
                  <div className="progress-track">
                    <div className={`progress-fill ${pct >= 100 ? 'complete' : ''}`} style={{ width: `${pct}%` }} />
                  </div>
                  <div className="progress-pct">{pct.toFixed(0)}% completado</div>
                  <div className="goal-actions">
                    <button onClick={() => abrirEditar(m)} className="btn btn-sm"><IconEdit size={13} /> Editar</button>
                    <button onClick={() => eliminar(m.id)} className="btn btn-danger"><IconTrash size={13} /> Eliminar</button>
                  </div>
                </div>
              )
            })}
          </div>
        )}

      {modal && (
        <div className="modal-overlay">
          <div className="modal-box">
            <h2>{modal === 'crear' ? 'Nueva meta de ahorro' : 'Editar meta de ahorro'}</h2>
            {error && <p className="field-error-box">{error}</p>}

            <label className="field-label">Nombre</label>
            <input className="field-input" value={form.nombre} onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))} />

            <label className="field-label">Monto objetivo</label>
            <input type="number" step="0.01" className="field-input" value={form.monto_objetivo} onChange={e => setForm(f => ({ ...f, monto_objetivo: e.target.value }))} />

            <label className="field-label">Monto actual</label>
            <input type="number" step="0.01" className="field-input" value={form.monto_actual} onChange={e => setForm(f => ({ ...f, monto_actual: e.target.value }))} />

            <label className="field-label">Fecha objetivo</label>
            <input type="date" className="field-input" value={form.fecha_objetivo} onChange={e => setForm(f => ({ ...f, fecha_objetivo: e.target.value }))} />

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