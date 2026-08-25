import './StatusBadge.css'

function StatusBadge({ status }) {
  const normalized = (status || '').toLowerCase()

  return (
    <span className={`status-badge status-badge--${normalized}`}>
      {status}
    </span>
  )
}

export default StatusBadge