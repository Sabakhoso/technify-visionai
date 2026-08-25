import { useEffect, useState } from 'react'
import { supabase } from '../supabaseClient.js'
import StatCard from '../components/StatCard.jsx'
import StatusBadge from '../components/StatusBadge.jsx'
import './Dashboard.css'
import Spinner from '../components/Spinner.jsx'
import ErrorMessage from '../components/ErrorMessage.jsx'
import { formatDuration } from '../utils/format.js'

function Dashboard() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchEvents() {
      const { data, error } = await supabase
        .from('events')
        .select('*')
        .order('created_at', { ascending: false })

      if (error) {
        setError(error.message)
      } else {
        setEvents(data)
      }
      setLoading(false)
    }

    fetchEvents()
  }, [])

  if (loading) return <Spinner label="Loading dashboard" />
  if (error) return <ErrorMessage message={error} />

  const totalEvents = events.length
  const uniqueCameras = new Set(events.map((e) => e.camera_id)).size

  const today = new Date().toDateString()
  const eventsToday = events.filter(
    (e) => new Date(e.created_at).toDateString() === today
  ).length

  const recentEvents = events.slice(0, 5)

  return (
    <div className="page-fade">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of detection activity</p>
      </div>

      <div className="stat-grid">
        <StatCard label="Total Events" value={totalEvents} />
        <StatCard label="Total Cameras" value={uniqueCameras} />
        <StatCard label="Events Today" value={eventsToday} />
      </div>

      <div className="recent-events">
        <h2>Recent Events</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>Camera</th>
              <th>Event Type</th>
              <th>Status</th>
              <th>Start Time</th>
            </tr>
          </thead>
          <tbody>
            {recentEvents.map((event) => (
              <tr key={event.id}>
                <td>{event.camera_id}</td>
                <td>{event.event_type}</td>
                <td><StatusBadge status={event.status} /></td>
                <td className="mono">{formatDuration(event.start_time)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Dashboard