import { Link, useParams, useNavigate, useLocation } from 'react-router-dom'
import { useState } from 'react'
import handleUnauthorized from '../utils/handleUnauthorized'
import Icon from '../components/Icon'
import { Alert, PageHeader, SubmitButton } from '../components/UI'
import { API_URL } from '../config'

export default function ReservationPage() {
  const { roomId } = useParams()
  const navigate = useNavigate()
  const { state } = useLocation()
  const room = String(state?.room?.id) === roomId ? state.room : null
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setMessage('')
    try {
      const response = await fetch(`${API_URL}/reservations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ room_id: Number(roomId), start_time: startTime, end_time: endTime }),
      })
      if (handleUnauthorized(response, navigate)) return
      const data = await response.json()
      if (response.ok) {
        setMessage('Reservation created successfully')
      } else {
        setError(data.detail || 'Failed to create reservation')
      }
    } catch {
      setError('Failed to connect to server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="reservation-content">
      <Link to="/rooms" className="back-link"><Icon name="arrow" />Back to rooms</Link>
      <PageHeader title="Create reservation" description="Choose a start and end time for your booking." />
      <form className="reservation-form surface" onSubmit={handleSubmit}>
        <div className="reservation-room"><span className="icon-tile"><Icon name="room" size={38} /></span><div><h2>{room ? `Room ${room.room_number}` : `Room #${roomId}`}</h2>{room && <p className="muted">{room.name}</p>}</div></div>
        <h2>Reservation time</h2>
        <p className="section-description">Choose a start and end time for your booking.</p>
        <div className="form-columns">
          <div className="field"><label htmlFor="start-time">Start</label><input id="start-time" type="datetime-local" value={startTime} onChange={event => setStartTime(event.target.value)} required /></div>
          <div className="field"><label htmlFor="end-time">End</label><input id="end-time" type="datetime-local" value={endTime} onChange={event => setEndTime(event.target.value)} required /></div>
        </div>
        <Alert>{error}</Alert>
        <Alert type="success">{message}</Alert>
        <div className="form-actions"><SubmitButton loading={loading} loadingText="Creating reservation…">Create reservation</SubmitButton></div>
      </form>
    </section>
  )
}
