import { useEffect, useState } from 'react'
import Card from '../components/ui/Card'
import api from '../services/api'
import './KnowYourRights.css'

const RIGHTS_DATA = [
  {
    title: 'Fair Debt Collection Practices Act (FDCPA)',
    icon: '🛡️',
    summary: 'Protects you from abusive, unfair, or deceptive debt collection practices.',
    points: [
      'Collectors cannot call before 8 AM or after 9 PM',
      'You can request written validation of the debt within 30 days',
      'Collectors must stop contact if you send a cease-and-desist letter',
      'Harassment, threats, and false statements are prohibited',
    ],
  },
  {
    title: 'Right to Debt Validation',
    icon: '📄',
    summary: 'You have the right to request proof that you owe the debt.',
    points: [
      'Send a validation request within 30 days of first contact',
      'Collector must provide amount owed, creditor name, and verification',
      'Collection must pause until validation is provided',
      'Dispute inaccurate information in writing',
    ],
  },
  {
    title: 'Statute of Limitations',
    icon: '⏳',
    summary: 'Debts have a time limit after which they cannot be legally enforced.',
    points: [
      'Varies by state (typically 3–6 years for credit card debt)',
      'Making a payment may restart the clock in some states',
      'Expired debts can still appear on credit reports for 7 years',
      'You can still be contacted, but not sued after expiration',
    ],
  },
  {
    title: 'Credit Reporting Rights',
    icon: '📊',
    summary: 'You have rights regarding how debts appear on your credit report.',
    points: [
      'Request free credit reports from AnnualCreditReport.com',
      'Dispute inaccurate items with credit bureaus',
      'Settled debts should be reported as "Paid" or "Settled"',
      'Negative items must be removed after 7 years (10 for bankruptcy)',
    ],
  },
  {
    title: 'Settlement Agreement Protections',
    icon: '🤝',
    summary: 'Always get settlement terms in writing before paying.',
    points: [
      'Require written confirmation of "payment in full" status',
      'Specify how the account will be reported to credit bureaus',
      'Keep copies of all correspondence and payment records',
      'Never give collectors access to your bank account',
    ],
  },
  {
    title: 'Bankruptcy Considerations',
    icon: '⚖️',
    summary: 'Bankruptcy may be an option for overwhelming debt situations.',
    points: [
      'Chapter 7 can discharge unsecured debts in 3–6 months',
      'Chapter 13 creates a 3–5 year repayment plan',
      'Consult a qualified bankruptcy attorney before filing',
      'Bankruptcy stays on credit report for 7–10 years',
    ],
  },
]

export default function KnowYourRights() {
  const [rights, setRights] = useState(RIGHTS_DATA)
  const [expanded, setExpanded] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchRights() {
      try {
        const data = await api.rights.getAll()
        if (data?.rights?.length) setRights(data.rights)
      } catch {
        // use static fallback data
      } finally {
        setLoading(false)
      }
    }
    fetchRights()
  }, [])

  if (loading) {
    return <div className="page-loading">Loading rights information...</div>
  }

  return (
    <div className="rights-page">
      <header className="page-header">
        <h1>Know Your Rights</h1>
        <p>Understand your legal protections as a borrower during debt collection and settlement.</p>
      </header>

      <div className="rights-grid">
        {rights.map((right, index) => (
          <Card key={right.title} className="rights-card">
            <button
              type="button"
              className="rights-card-header"
              onClick={() => setExpanded(expanded === index ? null : index)}
              aria-expanded={expanded === index}
            >
              <span className="rights-icon">{right.icon}</span>
              <div className="rights-title-wrap">
                <h3>{right.title}</h3>
                <p>{right.summary}</p>
              </div>
              <span className="rights-chevron">{expanded === index ? '▲' : '▼'}</span>
            </button>

            {expanded === index && (
              <ul className="rights-points">
                {right.points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            )}
          </Card>
        ))}
      </div>

      <div className="rights-disclaimer">
        <strong>Disclaimer:</strong> This information is for educational purposes only and does not constitute legal advice.
        Consult a qualified attorney for guidance specific to your situation.
      </div>
    </div>
  )
}
