import { useEffect, useState } from 'react'
import { fetchSummary } from './components/api.js'

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [summary, setSummary] = useState({ templates: 0, instances: 0, profiles: 0 })

  useEffect(() => {
    fetchSummary(apiUrl).then(setSummary).catch(() => setSummary(summary))
  }, [])

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>DLMS Control Plane</h1>
        <nav>
          <span>Discovery</span>
          <span>Emulators</span>
          <span>Fingerprints</span>
          <span>Profiles</span>
          <span>Integrations</span>
        </nav>
      </aside>
      <main className="content">
        <h2>Auto-Discovery & Fingerprinting Overview</h2>
        <p>
          Orchestrate virtual DLMS meters, scan IP ranges, and export profiles for
          utility onboarding.
        </p>
        <div className="card-grid">
          <div className="card">
            <h3>Emulator Templates</h3>
            <span className="badge">{summary.templates} templates</span>
          </div>
          <div className="card">
            <h3>Active Virtual Meters</h3>
            <span className="badge">{summary.instances} instances</span>
          </div>
          <div className="card">
            <h3>Profiles Generated</h3>
            <span className="badge">{summary.profiles} profiles</span>
          </div>
        </div>

        <div className="card" style={{ marginTop: '24px' }}>
          <h3>Next Actions</h3>
          <table className="table">
            <thead>
              <tr>
                <th>Module</th>
                <th>Status</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Discovery Engine</td>
                <td>Ready</td>
                <td>Supports bulk scans and auto-retry logic.</td>
              </tr>
              <tr>
                <td>Authentication</td>
                <td>Ready</td>
                <td>LLS/HLS negotiation simulation enabled.</td>
              </tr>
              <tr>
                <td>Fingerprinting</td>
                <td>Ready</td>
                <td>Vendor signatures and feature vectors stored.</td>
              </tr>
            </tbody>
          </table>
          <button className="button" style={{ marginTop: '16px' }}>
            Start New Discovery
          </button>
        </div>
      </main>
    </div>
  )
}
