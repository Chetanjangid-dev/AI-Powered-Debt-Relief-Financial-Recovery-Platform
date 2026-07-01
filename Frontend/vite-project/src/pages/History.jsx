import { useEffect, useState } from 'react'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import api from '../services/api'
import './History.css'

const PLACEHOLDER_HISTORY = [
  {
    id: 1,
    type: 'settlement',
    title: 'Capital One Settlement Prediction',
    date: '2026-06-28',
    summary: 'Recommended offer: $3,690 (45% of $8,200 balance)',
    details: 'Confidence: Medium. Strategy: Start at 35%, negotiate to 45%.',
  },
  {
    id: 2,
    type: 'letter',
    title: 'Medical Collections — Negotiation Letter',
    date: '2026-06-25',
    summary: 'Settlement offer of $2,800 on $6,300 balance',
    details: 'Generated via Gemini AI. Hardship: unexpected medical expenses.',
  },
  {
    id: 3,
    type: 'settlement',
    title: 'Personal Loan Settlement Prediction',
    date: '2026-06-20',
    summary: 'Recommended offer: $5,500 (55% of $10,000 balance)',
    details: 'Confidence: High. Account is current — lower settlement likelihood.',
  },
]

const TYPE_LABELS = {
  settlement: { label: 'Settlement', className: 'badge-settlement' },
  letter: { label: 'Letter', className: 'badge-letter' },
}

export default function History() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedId, setExpandedId] = useState(null)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    async function fetchHistory() {
      try {
        const data = await api.history.getAll()
        setItems(data.items || data)
      } catch {
        setItems(PLACEHOLDER_HISTORY)
        setError('Showing sample history — connect backend for live data.')
      } finally {
        setLoading(false)
      }
    }
    fetchHistory()
  }, [])

  const filtered =
    filter === 'all' ? items : items.filter((item) => item.type === filter)

  if (loading) {
    return <div className="page-loading">Loading history...</div>
  }

  return (
    <div className="history-page">
      <header className="page-header">
        <h1>History</h1>
        <p>Review your past AI-generated settlement predictions and negotiation letters.</p>
      </header>

      {error && <div className="history-notice">{error}</div>}

      <div className="history-filters">
        {['all', 'settlement', 'letter'].map((f) => (
          <button
            key={f}
            type="button"
            className={`history-filter ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f === 'all' ? 'All' : f === 'settlement' ? 'Predictions' : 'Letters'}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <Card>
          <div className="history-empty">
            <span>📜</span>
            <p>No history yet. Use Settlement Predictor or Negotiation Email to generate entries.</p>
          </div>
        </Card>
      ) : (
        <div className="history-list">
          {filtered.map((item) => {
            const badge = TYPE_LABELS[item.type] || TYPE_LABELS.settlement
            return (
              <Card key={item.id} className="history-item">
                <div className="history-item-header">
                  <div>
                    <span className={`history-badge ${badge.className}`}>{badge.label}</span>
                    <h3>{item.title}</h3>
                    <span className="history-date">{item.date}</span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setExpandedId(expandedId === item.id ? null : item.id)}
                  >
                    {expandedId === item.id ? 'Hide' : 'View'}
                  </Button>
                </div>
                <p className="history-summary">{item.summary}</p>
                {expandedId === item.id && (
                  <div className="history-details">{item.details}</div>
                )}
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
