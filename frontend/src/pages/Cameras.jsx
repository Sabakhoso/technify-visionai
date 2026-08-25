import { useEffect, useState } from 'react'
import { supabase } from '../supabaseClient.js'
import './Cameras.css'
import Spinner from '../components/Spinner.jsx'
import ErrorMessage from '../components/ErrorMessage.jsx'

function Cameras() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchEvents() {
      const { data, error } = await supabase
        .from('events')
        .select('camera_id')

      if (error) {
        setError(error.message)
      } else {
        setEvents(data)
      }
      setLoading(false)
    }

    fetchEvents()
  }, [])

  if (loading) return <Spinner label="Loading cameras" />
  if (error) return <ErrorMessage message={error} />

  const cameraCounts = events.reduce((acc, event) => {
    acc[event.camera_id] = (acc[event.camera_id] || 0) + 1
    return acc
  }, {})

  const cameras = Object.entries(cameraCounts).map(([cameraId, count]) => ({
    cameraId,
    count,
  }))

  return (
    <div className="page-fade">
      <div className="page-header">
        <h1>Cameras</h1>
        <p>Cameras derived from event data</p>
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>Camera ID</th>
            <th>Total Events</th>
          </tr>
        </thead>
        <tbody>
          {cameras.map((cam) => (
            <tr key={cam.cameraId}>
              <td>{cam.cameraId}</td>
              <td className="mono-count">{cam.count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default Cameras