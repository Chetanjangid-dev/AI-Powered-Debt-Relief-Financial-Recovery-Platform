import { useState } from 'react'
import Card from '../components/ui/Card'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'
import api from '../services/api'
import './SettlementPredictor.css'

export default function SettlementPredictor() {
  const [form, setForm] = useState({
    creditor: '',
    originalBalance: '',
    currentBalance: '',
    monthsDelinquent: '',
    monthlyPaymentCapacity: '',
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const data = await api.settlement.predict({
        creditor: form.creditor,
        original_balance: parseFloat(form.originalBalance),
        current_balance: parseFloat(form.currentBalance),
        months_delinquent: parseInt(form.monthsDelinquent, 10),
        monthly_payment_capacity: parseFloat(form.monthlyPaymentCapacity),
      })
      setResult(data)
    } catch {
      const balance = parseFloat(form.currentBalance) || 0
      setResult({
        recommended_settlement: (balance * 0.45).toFixed(2),
        settlement_percentage: '45%',
        monthly_payment_plan: ((balance * 0.45) / 12).toFixed(2),
        confidence: 'Medium',
        strategy: 'Based on delinquency status and payment capacity, a lump-sum offer of 40–50% is typically accepted for accounts in collections. Consider starting at 35% and negotiating upward.',
        savings: (balance * 0.55).toFixed(2),
      })
      setError('Backend unavailable — showing sample prediction.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="settlement-page">
      <header className="page-header">
        <h1>Settlement Predictor</h1>
        <p>Enter loan details to receive AI-powered settlement recommendations.</p>
      </header>

      <div className="page-grid settlement-grid">
        <Card title="Loan Details" subtitle="Information used for prediction">
          <form onSubmit={handleSubmit}>
            <Input label="Creditor Name" value={form.creditor} onChange={handleChange('creditor')} placeholder="e.g. Capital One" required />
            <Input label="Original Balance ($)" type="number" value={form.originalBalance} onChange={handleChange('originalBalance')} placeholder="10000" required />
            <Input label="Current Balance ($)" type="number" value={form.currentBalance} onChange={handleChange('currentBalance')} placeholder="8200" required />
            <Input label="Months Delinquent" type="number" value={form.monthsDelinquent} onChange={handleChange('monthsDelinquent')} placeholder="6" required />
            <Input label="Monthly Payment Capacity ($)" type="number" value={form.monthlyPaymentCapacity} onChange={handleChange('monthlyPaymentCapacity')} placeholder="200" required />
            <Button type="submit" disabled={loading} fullWidth>
              {loading ? 'Analyzing...' : 'Predict Settlement'}
            </Button>
          </form>
        </Card>

        <Card title="Prediction Results" subtitle={result ? 'AI settlement recommendation' : 'Submit loan details to see results'}>
          {error && <div className="settlement-notice">{error}</div>}

          {!result && !loading && (
            <div className="settlement-empty">
              <span>🎯</span>
              <p>Fill in the form and click Predict Settlement to see your recommendation.</p>
            </div>
          )}

          {loading && <div className="settlement-loading">Running financial analysis...</div>}

          {result && (
            <div className="settlement-results">
              <div className="settlement-highlight">
                <span className="settlement-label">Recommended Offer</span>
                <span className="settlement-amount">${result.recommended_settlement}</span>
                <span className="settlement-pct">{result.settlement_percentage} of balance</span>
              </div>

              <div className="settlement-details">
                <div className="settlement-detail">
                  <span>Estimated Savings</span>
                  <strong>${result.savings}</strong>
                </div>
                <div className="settlement-detail">
                  <span>Monthly Plan (12 mo)</span>
                  <strong>${result.monthly_payment_plan}/mo</strong>
                </div>
                <div className="settlement-detail">
                  <span>Confidence</span>
                  <strong>{result.confidence}</strong>
                </div>
              </div>

              <div className="settlement-strategy">
                <h4>Negotiation Strategy</h4>
                <p>{result.strategy}</p>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
