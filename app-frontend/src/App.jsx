import React, { useEffect, useState, useRef } from 'react'
import axios from 'axios'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js'
import { Line, Bar, Pie } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend)

export default function App() {
    const [status, setStatus] = useState('checking')
    const [file, setFile] = useState(null)
    const [jsonInput, setJsonInput] = useState('')
    const [result, setResult] = useState(null)
    const fileRef = useRef()
    const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

    useEffect(() => {
        axios.get(`${API_BASE}/health`)
            .then(r => setStatus(r.data.status))
            .catch(() => setStatus('offline'))
    }, [])

    async function sendJSON() {
        try {
            const payload = { data: JSON.parse(jsonInput) }
            const r = await axios.post(`${API_BASE}/analyze`, payload)
            setResult(r.data)
        } catch (e) {
            alert('Invalid JSON input or server error')
        }
    }

    async function uploadFile() {
        if (!file) return alert('Select a file first')
        const fd = new FormData()
        fd.append('file', file)
        try {
            const r = await axios.post(`${API_BASE}/analyze_file`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
            setResult(r.data)
        } catch (e) {
            alert('Upload failed')
        }
    }

    return (
        <div style={{ fontFamily: 'Arial', padding: 20 }}>
            <h1>AI Decision Intelligence</h1>
            <p><strong>Backend:</strong> {status}</p>

            <section style={{ marginTop: 20 }}>
                <h2>Upload CSV/JSON file</h2>
                <input ref={fileRef} type="file" accept=".csv,.json,.ndjson" onChange={e => setFile(e.target.files[0])} />
                <button onClick={uploadFile} style={{ marginLeft: 10 }}>Upload & Analyze</button>
            </section>

            <section style={{ marginTop: 20 }}>
                <h2>Or paste JSON</h2>
                <textarea value={jsonInput} onChange={e => setJsonInput(e.target.value)} rows={8} cols={80} placeholder='{"data": [{"a":1}]}' />
                <br />
                <button onClick={sendJSON}>Analyze JSON</button>
            </section>

            <section style={{ marginTop: 20 }}>
                <h2>Results</h2>
                {result ? (
                    <div>
                        <h3>Executive Summary</h3>
                        <p>{result.executive_summary}</p>

                        <h3>Surface Insights</h3>
                        <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(result.surface_insights, null, 2)}</pre>

                        {/* Quick sample charts from data */}
                        {result.surface_insights && result.surface_insights.sample && result.surface_insights.sample.length > 0 ? (
                            (() => {
                                const sample = result.surface_insights.sample
                                const first = sample[0]
                                const numericKeys = Object.keys(first).filter(k => typeof first[k] === 'number')
                                const categoryKeys = Object.keys(first).filter(k => typeof first[k] === 'string')
                                const chartElements = []

                                if (numericKeys.length >= 1) {
                                    const key = numericKeys[0]
                                    const labels = sample.map((_, i) => `r${i + 1}`)
                                    const data = sample.map(r => (typeof r[key] === 'number' ? r[key] : null))
                                    const cfg = {
                                        labels,
                                        datasets: [{
                                            label: key,
                                            data,
                                            borderColor: 'rgba(75,192,192,1)',
                                            backgroundColor: 'rgba(75,192,192,0.2)',
                                            tension: 0.3,
                                        }],
                                    }
                                    chartElements.push(
                                        <div key="line" style={{ maxWidth: 700, marginBottom: 24 }}>
                                            <h4>Sample Trend — {key}</h4>
                                            <Line data={cfg} />
                                        </div>,
                                    )
                                }

                                if (numericKeys.length >= 2) {
                                    const yKey = numericKeys[1]
                                    const labels = sample.map((_, i) => `r${i + 1}`)
                                    const barCfg = {
                                        labels,
                                        datasets: [{
                                            label: yKey,
                                            data: sample.map(r => (typeof r[yKey] === 'number' ? r[yKey] : 0)),
                                            backgroundColor: 'rgba(54, 162, 235, 0.5)',
                                        }],
                                    }
                                    chartElements.push(
                                        <div key="bar" style={{ maxWidth: 700, marginBottom: 24 }}>
                                            <h4>Sample Bar — {yKey}</h4>
                                            <Bar data={barCfg} />
                                        </div>,
                                    )
                                }

                                if (categoryKeys.length >= 1) {
                                    const catKey = categoryKeys[0]
                                    const counts = sample.reduce((acc, row) => {
                                        const value = row[catKey] || 'Unknown'
                                        acc[value] = (acc[value] || 0) + 1
                                        return acc
                                    }, {})
                                    const pieCfg = {
                                        labels: Object.keys(counts),
                                        datasets: [{
                                            label: catKey,
                                            data: Object.values(counts),
                                            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'],
                                        }],
                                    }
                                    chartElements.push(
                                        <div key="pie" style={{ maxWidth: 700, marginBottom: 24 }}>
                                            <h4>Sample Distribution — {catKey}</h4>
                                            <Pie data={pieCfg} />
                                        </div>,
                                    )
                                }

                                return chartElements
                            })()
                        ) : null}

                        <h3>Deep Insights</h3>
                        <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(result.deep_insights, null, 2)}</pre>

                        <h3>Strategic Insights</h3>
                        <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(result.strategic_insights, null, 2)}</pre>

                        <h3>Recommended Actions</h3>
                        <ul>{(result.recommended_actions || []).map((r, i) => (<li key={i}>{r}</li>))}</ul>
                    </div>
                ) : (
                    <p>No results yet — upload a file or send JSON.</p>
                )}
            </section>
        </div>
    )
}
