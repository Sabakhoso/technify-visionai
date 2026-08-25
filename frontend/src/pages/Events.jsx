import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../supabaseClient.js'
import StatusBadge from '../components/StatusBadge.jsx'
import './Events.css'
import Spinner from '../components/Spinner.jsx'
import ErrorMessage from '../components/ErrorMessage.jsx'
import { formatDuration } from '../utils/format.js'

function Events() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [cameraFilter, setCameraFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')

  const navigate = useNavigate()

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

  if (loading) return <Spinner label="Loading events" />
  if (error) return <ErrorMessage message={error} />

  const cameraOptions = [...new Set(events.map((e) => e.camera_id))]
  const typeOptions = [...new Set(events.map((e) => e.event_type))]
  const statusOptions = [...new Set(events.map((e) => e.status))]

  const filteredEvents = events.filter((e) => {
    return (
      (cameraFilter === 'all' || e.camera_id === cameraFilter) &&
      (typeFilter === 'all' || e.event_type === typeFilter) &&
      (statusFilter === 'all' || e.status === statusFilter)
    )
  })

  return (
    <div className="page-fade">
      <div className="page-header">
        <h1>Events</h1>
        <p>All detected events</p>
      </div>

      <div className="filters">
        <select value={cameraFilter} onChange={(e) => setCameraFilter(e.target.value)}>
          <option value="all">All Cameras</option>
          {cameraOptions.map((cam) => (
            <option key={cam} value={cam}>{cam}</option>
          ))}
        </select>

        <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
          <option value="all">All Event Types</option>
          {typeOptions.map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>

        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">All Statuses</option>
          {statusOptions.map((status) => (
            <option key={status} value={status}>{status}</option>
          ))}
        </select>

        {(cameraFilter !== 'all' || typeFilter !== 'all' || statusFilter !== 'all') && (
          <button
            className="clear-filters-btn"
            onClick={() => {
              setCameraFilter('all')
              setTypeFilter('all')
              setStatusFilter('all')
            }}
          >
            Clear filters
          </button>
        )}
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>Camera</th>
            <th>Event Type</th>
            <th>Status</th>
            <th>Severity</th>
            <th>Start Time</th>
            <th>Zone</th>
          </tr>
        </thead>
        <tbody>
          {filteredEvents.map((event) => (
            <tr
              key={event.id}
              className="clickable-row"
              onClick={() => navigate(`/events/${event.event_id}`)}
            >
              <td>{event.camera_id}</td>
              <td>{event.event_type}</td>
              <td><StatusBadge status={event.status} /></td>
              <td>{event.severity}</td>
              <td className="mono">{formatDuration(event.start_time)}</td>
              <td>{event.zone}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {filteredEvents.length === 0 && (
        <p className="empty-state">No events match these filters.</p>
      )}
    </div>
  )
}

export default Events