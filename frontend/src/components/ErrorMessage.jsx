import { AlertCircle } from 'lucide-react'
import './ErrorMessage.css'

function ErrorMessage({ message }) {
  return (
    <div className="error-box">
      <AlertCircle size={18} strokeWidth={1.75} />
      <div>
        <p className="error-title">Couldn't load data</p>
        <p className="error-detail">{message}</p>
      </div>
    </div>
  )
}

export default ErrorMessage