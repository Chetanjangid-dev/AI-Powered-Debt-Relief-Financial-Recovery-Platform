import { useEffect, useState } from 'react'
import MetricCard from '../components/ui/MetricCard'
import Card from '../components/ui/Card'
import api from '../services/api'
import './Dashboard.css'

const PLACEHOLDER_DATA = {
  totalDebt: '$24,500',
  monthlyIncome: '$4,200',
  monthlyExpenses: '$3,100',
  disposableIncome: '$1,100',
  debtToIncomeRatio: '58%',
  financialHealthScore: 42,
  loans: [
    { creditor: 'Capital One', balance: '$8,200', interestRate: '22.9%', status: 'Delinquent' },
    { creditor: 'Medical Collections', balance: '$6,300', interestRate: '0%', status: 'In Collections' },
    { creditor: 'Personal Loan', balance: '$10,000', interestRate: '15.5%', status: 'Current' },
  ],
}

export default function Dashboard() {
  const [data, setData] = useState(PLACEHOLDER_DATA)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchDashboard() {
      try {
        const result = await api.dashboard.getOverview()
        setData(result)
      } catch {
        setError('Using sample data — connect backend to load live metrics.')
        setData(PLACEHOLDER_DATA)
      } finally {
        setLoading(false)
      }
    }
    fetchDashboard()
  }, [])

  if (loading) {
    return <div className="page-loading">Loading dashboard...</div>
  }

  const healthColor =
    data.financialHealthScore >= 70
      ? 'health-good'
      : data.financialHealthScore >= 40
        ? 'health-fair'
        : 'health-poor'

  return (
    <div className="dashboard">
      <header className="page-header">
        <h1>Financial Overview</h1>
        <p>Your debt profile, income analysis, and financial health at a glance.</p>
      </header>

      {error && <div className="dashboard-notice">{error}</div>}

      <div className="page-grid page-grid-3 dashboard-metrics">
        <MetricCard label="Total Debt" value={data.totalDebt} icon="💳" trend="down" change="↓ 12% from last month" />
        <MetricCard label="Monthly Income" value={data.monthlyIncome} icon="💵" />
        <MetricCard label="Monthly Expenses" value={data.monthlyExpenses} icon="📋" />
        <MetricCard label="Disposable Income" value={data.disposableIncome} icon="✅" trend="up" change="Available for settlements" />
        <MetricCard label="Debt-to-Income" value={data.debtToIncomeRatio} icon="📉" />
        <MetricCard
          label="Financial Health"
          value={`${data.financialHealthScore}/100`}
          icon="❤️"
          change={data.financialHealthScore >= 70 ? 'Good standing' : data.financialHealthScore >= 40 ? 'Needs attention' : 'Critical'}
        />
      </div>

      <div className="page-grid page-grid-2 dashboard-bottom">
        <Card title="Health Score" subtitle="Based on income, expenses, and debt ratio">
          <div className={`health-score-ring ${healthColor}`}>
            <span className="health-score-value">{data.financialHealthScore}</span>
            <span className="health-score-label">/ 100</span>
          </div>
          <div className="health-bar">
            <div
              className={`health-bar-fill ${healthColor}`}
              style={{ width: `${data.financialHealthScore}%` }}
            />
          </div>
        </Card>

        <Card title="Active Loans" subtitle="Your current debt accounts">
          <div className="loan-list">
            {data.loans?.map((loan) => (
              <div key={loan.creditor} className="loan-item">
                <div className="loan-info">
                  <strong>{loan.creditor}</strong>
                  <span className="loan-rate">{loan.interestRate} APR</span>
                </div>
                <div className="loan-meta">
                  <span className="loan-balance">{loan.balance}</span>
                  <span className={`loan-status status-${loan.status.toLowerCase().replace(/\s+/g, '-')}`}>
                    {loan.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
