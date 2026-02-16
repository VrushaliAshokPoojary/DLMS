import { useEffect, useMemo, useState } from 'react'
import { createInstance, fetchSummary, listTemplates, runWorkflow } from './components/api.js'

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const apiKey = import.meta.env.VITE_API_KEY

const initialForm = {
  vendor: '',
  model: '',
  ip_address: '127.0.0.1',
  port: '4059',
}

export default function App() {
  const [summary, setSummary] = useState({ templates: 0, instances: 0, profiles: 0 })
  const [templates, setTemplates] = useState([])
  const [form, setForm] = useState(initialForm)
  const [meter, setMeter] = useState(null)
  const [workflowResult, setWorkflowResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function refreshData() {
    try {
      const [summaryData, templateData] = await Promise.all([
        fetchSummary(apiUrl, apiKey),
        listTemplates(apiUrl, apiKey),
      ])
      setSummary(summaryData)
      setTemplates(templateData)
      if (templateData.length > 0) {
        setForm((prev) => ({
          ...prev,
          vendor: prev.vendor || templateData[0].vendor,
          model: prev.model || templateData[0].model,
        }))
      }
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    refreshData()
  }, [])

  const filteredModels = useMemo(
    () => templates.filter((t) => t.vendor === form.vendor).map((t) => t.model),
    [templates, form.vendor],
  )

  async function onCreateInstance(event) {
    event.preventDefault()
    setError('')
    setLoading(true)
    setWorkflowResult(null)
    try {
      const instance = await createInstance(apiUrl, apiKey, form)
      setMeter(instance)
      await refreshData()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function onRunWorkflow() {
    if (!meter?.meter_id) {
      return
    }
    setError('')
    setLoading(true)
    try {
      const data = await runWorkflow(apiUrl, apiKey, meter.meter_id)
      setWorkflowResult(data)
      await refreshData()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>DLMS Universal Lab</h1>
        <p className="sidebar-note">One-screen flow for emulator setup, discovery workflow, and profile generation.</p>
      </aside>

      <main className="content">
        <h2>Software-Defined DLMS Auto-Discovery & Fingerprinting</h2>
        <p className="muted">API URL: {apiUrl}</p>

        <div className="card-grid">
          <div className="card"><h3>Templates</h3><span className="badge">{summary.templates}</span></div>
          <div className="card"><h3>Instances</h3><span className="badge">{summary.instances}</span></div>
          <div className="card"><h3>Profiles</h3><span className="badge">{summary.profiles}</span></div>
        </div>

        <div className="card" style={{ marginTop: 20 }}>
          <h3>Step 1: Create Virtual Meter</h3>
          <form className="form-grid" onSubmit={onCreateInstance}>
            <label>
              Vendor
              <select
                value={form.vendor}
                onChange={(e) => {
                  const vendor = e.target.value
                  const firstModel = templates.find((t) => t.vendor === vendor)?.model || ''
                  setForm((prev) => ({ ...prev, vendor, model: firstModel }))
                }}
              >
                {[...new Set(templates.map((t) => t.vendor))].map((v) => (
                  <option key={v} value={v}>{v}</option>
                ))}
              </select>
            </label>

            <label>
              Model
              <select value={form.model} onChange={(e) => setForm((prev) => ({ ...prev, model: e.target.value }))}>
                {filteredModels.map((m) => <option key={m} value={m}>{m}</option>)}
              </select>
            </label>

            <label>
              IP Address
              <input value={form.ip_address} onChange={(e) => setForm((prev) => ({ ...prev, ip_address: e.target.value }))} />
            </label>

            <label>
              Port
              <input value={form.port} onChange={(e) => setForm((prev) => ({ ...prev, port: e.target.value }))} />
            </label>

            <button className="button" type="submit" disabled={loading}>Create Instance</button>
          </form>

          {meter && (
            <p className="success">Created meter: <strong>{meter.meter_id}</strong> ({meter.vendor} {meter.model})</p>
          )}
        </div>

        <div className="card" style={{ marginTop: 20 }}>
          <h3>Step 2: Run End-to-End Workflow</h3>
          <p className="muted">Runs fingerprint → profile → association → association objects → OBIS normalize → vendor classify.</p>
          <button className="button" onClick={onRunWorkflow} disabled={loading || !meter}>Run Workflow</button>

          {error && <p className="error">Error: {error}</p>}

          {workflowResult && (
            <pre className="result">{JSON.stringify(workflowResult, null, 2)}</pre>
          )}
        </div>
      </main>
    </div>
  )
}
