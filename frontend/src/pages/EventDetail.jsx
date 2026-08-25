import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { supabase } from '../supabaseClient.js'
import StatusBadge from '../components/StatusBadge.jsx'
import './EventDetail.css'
import Spinner from '../components/Spinner.jsx'
import ErrorMessage from '../components/ErrorMessage.jsx'
import { formatDateTime, formatDuration } from '../utils/format.js'

function EventDetail() {
  const { eventId } = useParams()
  const [event, setEvent] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchEvent() {
      const { data, error } = await supabase
        .from('events')
        .select('*')
        .eq('event_id', eventId)
        .single()

      if (error) {
        setError(error.message)
      } else {
        setEvent(data)
      }
      setLoading(false)
    }

    fetchEvent()
  }, [eventId])

  if (loading) return <Spinner label="Loading event" />
  if (error) return <ErrorMessage message={error} />
  if (!event) return <ErrorMessage message="No event found with this ID." />

  return (
    <div className="page-fade">
      <Link to="/events" className="back-link">
        <ArrowLeft size={16} strokeWidth={1.75} />
        <span>Back to Events</span>
      </Link>

      <div className="page-header">
        <h1>Event Detail</h1>
        <span className="detail-value mono">{event.event_id}</span>
      </div>

      <div className="detail-grid">
        <div className="detail-field">
          <span className="detail-label">Event ID</span>
          <span className="detail-value mono">{formatDuration(event.start_time)}</span>
        </div>
        <div className="detail-field">
          <span className="detail-label">Camera ID</span>
          <span className="detail-value mono">{event.camera_id}</span>
        </div>
        <div className="detail-field">
          <span className="detail-label">Event Type</span>
          <span className="detail-value">{event.event_type}</span>
        </div>
        <div className="detail-field">
          <span className="detail-label">Track ID</span>
          <span className="detail-value mono">{event.track_id}</span>
        </div>
        <div className="detail-field">
          <span className="detail-label">Severity</span>
          <span className="detail-value">{event.severity}</span>
        </div>
        <div className="detail-field">
          <span className="detail-label">Confidence</span>
          <span className="detail-value mono">{event.confidence ?? '—'}</span>
        </div>
        <div className="detail-field">
          <span className="detail-label">Start Time</span>
          <span className="detail-value mono">{event.start_time}</span>
        </div>
        <div className="detail-field">
          <span className="detail-label">Frame Number</span>
          <span className="detail-value mono">{event.frame_number}</span>
        </div>
        <div className="detail-field">
          <span className="detail-label">Status</span>
          <span className="detail-value"><StatusBadge status={event.status} /></span>
        </div>
        <div className="detail-field">
          <span className="detail-label">Zone</span>
          <span className="detail-value">{event.zone}</span>
        </div>
        <div className="detail-field">
          <span className="detail-label">Created At</span>
          <span className="detail-value mono">{formatDateTime(event.created_at)}</span>
        </div>
      </div>

      <div className="evidence-section">
        <h2>Evidence</h2>
        {event.evidence_video_path ? (
          <div className="evidence-placeholder">
            <p>Video path:</p>
            <code>{event.evidence_video_path}</code>
            <p className="evidence-note">Video playback coming in a future step.</p>
          </div>
        ) : (
          <p className="evidence-note">No evidence video available for this event.</p>
        )}
      </div>
    </div>
  )
}

export default EventDetail