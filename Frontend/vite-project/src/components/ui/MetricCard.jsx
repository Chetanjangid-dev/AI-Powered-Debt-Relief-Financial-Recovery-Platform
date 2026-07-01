import './MetricCard.css'

export default function MetricCard({ label, value, change, trend, icon }) {
  const trendClass = trend === 'up' ? 'metric-up' : trend === 'down' ? 'metric-down' : ''

  return (
    <div className="metric-card">
      <div className="metric-top">
        <span className="metric-label">{label}</span>
        {icon && <span className="metric-icon">{icon}</span>}
      </div>
      <div className="metric-value">{value}</div>
      {change && (
        <div className={`metric-change ${trendClass}`}>{change}</div>
      )}
    </div>
  )
}
