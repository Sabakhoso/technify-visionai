import './Spinner.css'

function Spinner({ label = 'Loading' }) {
  return (
    <div className="spinner-container">
      <div className="spinner"></div>
      <span className="spinner-label">{label}</span>
    </div>
  )
}

export default Spinner