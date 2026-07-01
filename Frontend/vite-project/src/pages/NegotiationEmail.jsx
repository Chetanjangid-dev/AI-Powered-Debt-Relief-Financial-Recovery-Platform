import { useState } from 'react'
import Card from '../components/ui/Card'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'
import api from '../services/api'
import './NegotiationEmail.css'

export default function NegotiationEmail() {
  const [form, setForm] = useState({
    creditorName: '',
    accountNumber: '',
    currentBalance: '',
    offerAmount: '',
    borrowerName: '',
    hardshipReason: '',
  })
  const [letter, setLetter] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
  }

  const handleGenerate = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setLetter('')

    try {
      const data = await api.negotiation.generate({
        creditor_name: form.creditorName,
        account_number: form.accountNumber,
        current_balance: parseFloat(form.currentBalance),
        offer_amount: parseFloat(form.offerAmount),
        borrower_name: form.borrowerName,
        hardship_reason: form.hardshipReason,
      })
      setLetter(data.letter || data.content)
    } catch {
      setLetter(generateSampleLetter(form))
      setError('Backend unavailable — showing sample letter. Connect Gemini AI for live generation.')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = async () => {
    await navigator.clipboard.writeText(letter)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="negotiation-page">
      <header className="page-header">
        <h1>Negotiation Email</h1>
        <p>Generate a professional settlement request letter powered by Google Gemini AI.</p>
      </header>

      <div className="page-grid negotiation-grid">
        <Card title="Letter Details" subtitle="Information for your settlement request">
          <form onSubmit={handleGenerate}>
            <Input label="Your Full Name" value={form.borrowerName} onChange={handleChange('borrowerName')} placeholder="John Doe" required />
            <Input label="Creditor Name" value={form.creditorName} onChange={handleChange('creditorName')} placeholder="Capital One" required />
            <Input label="Account Number (last 4 digits)" value={form.accountNumber} onChange={handleChange('accountNumber')} placeholder="1234" required />
            <Input label="Current Balance ($)" type="number" value={form.currentBalance} onChange={handleChange('currentBalance')} placeholder="8200" required />
            <Input label="Settlement Offer ($)" type="number" value={form.offerAmount} onChange={handleChange('offerAmount')} placeholder="3500" required />
            <div className="input-group">
              <label className="input-label">Hardship Reason</label>
              <textarea
                className="negotiation-textarea"
                value={form.hardshipReason}
                onChange={handleChange('hardshipReason')}
                placeholder="Describe your financial hardship (job loss, medical expenses, etc.)"
                rows={4}
                required
              />
            </div>
            <Button type="submit" disabled={loading} fullWidth>
              {loading ? 'Generating with AI...' : 'Generate Letter'}
            </Button>
          </form>
        </Card>

        <Card
          title="Generated Letter"
          subtitle="Review, edit, and send to your creditor"
          actions={
            letter && (
              <Button variant="secondary" size="sm" onClick={handleCopy}>
                {copied ? 'Copied!' : 'Copy to Clipboard'}
              </Button>
            )
          }
        >
          {error && <div className="negotiation-notice">{error}</div>}

          {!letter && !loading && (
            <div className="negotiation-empty">
              <span>✉️</span>
              <p>Complete the form and click Generate Letter to create your negotiation email.</p>
            </div>
          )}

          {loading && <div className="negotiation-loading">Gemini AI is drafting your letter...</div>}

          {letter && <pre className="negotiation-letter">{letter}</pre>}
        </Card>
      </div>
    </div>
  )
}

function generateSampleLetter(form) {
  const date = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
  return `[Your Name]
[Your Address]
[City, State ZIP]

${date}

${form.creditorName}
Collections Department
[Creditor Address]

Re: Account #****${form.accountNumber} — Settlement Offer

Dear ${form.creditorName} Collections Department,

I am writing regarding my account ending in ${form.accountNumber}, which currently shows an outstanding balance of $${form.currentBalance}.

Due to ${form.hardshipReason || 'significant financial hardship'}, I am unable to pay the full balance at this time. However, I am committed to resolving this debt and propose a lump-sum settlement of $${form.offerAmount} as payment in full.

This offer represents my best effort given my current financial situation. I respectfully request that, upon acceptance and receipt of payment, you report this account as "Paid in Full" or "Settled in Full" to all credit reporting agencies.

Please confirm acceptance of this offer in writing before I remit payment. I can provide payment within 30 days of your written acceptance.

Thank you for your consideration.

Sincerely,
${form.borrowerName}`
}
