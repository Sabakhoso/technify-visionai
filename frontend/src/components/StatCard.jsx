import './StatCard.css'

function StatCard({ label, value }) {
  return (
    <div className="stat-card">
      <div className="stat-card-label-row">
        <span className="stat-card-dot"></span>
        <span className="stat-card-label">{label}</span>
      </div>
      <span className="stat-card-value">{value}</span>
    </div>
  )
}

export default StatCard