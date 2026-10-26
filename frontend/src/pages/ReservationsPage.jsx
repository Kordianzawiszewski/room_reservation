import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import handleUnauthorized from '../utils/handleUnauthorized'
import Icon from '../components/Icon'
import { Alert, EmptyState, PageHeader, Skeletons } from '../components/UI'
import { API_URL } from '../config'

const dateLabel = value => new Date(value).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
const timeLabel = value => new Date(value).toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' })

export default function ReservationsPage() {
  const [reservations, setReservations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionError, setActionError] = useState('')
  const [cancelling, setCancelling] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    const controller = new AbortController()
    async function fetchReservations() {
      try {
        const response = await fetch(`${API_URL}/reservations/me`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
          signal: controller.signal,
        })
        if (handleUnauthorized(response, navigate)) return
        if (!response.ok) throw new Error('Failed to fetch reservations')
        setReservations(await response.json())
      } catch (error) {
        if (error.name !== 'AbortError') setError(error.message)
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }
    fetchReservations()
    return () => controller.abort()
  }, [navigate])

  async function handleCancel(reservationId) {
    setCancelling(current => [...current, reservationId])
    setActionError('')
    try {
      const response = await fetch(`${API_URL}/reservations/${reservationId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      })
      if (handleUnauthorized(response, navigate)) return
      const data = await response.json()
      if (response.ok) {
        setReservations(current => current.filter(reservation => reservation.id !== reservationId))
      } else {
        setActionError(data.detail || 'Failed to cancel reservation')
      }
    } catch {
      setActionError('Failed to connect to server. Please try again.')
    } finally {
      setCancelling(current => current.filter(id => id !== reservationId))
    }
  }

  return (
    <section>
      <PageHeader title="My reservations" description="View and manage your room bookings." />
      {actionError && <div className="page-alert"><Alert>{actionError}</Alert></div>}
      {loading ? <Skeletons rows count={3} /> : error ? <Alert>{error}</Alert> : reservations.length ? (
        <div className="reservation-list">
          {reservations.map(reservation => {
            const busy = cancelling.includes(reservation.id)
            const sameDay = new Date(reservation.start_time).toDateString() === new Date(reservation.end_time).toDateString()
            return (
              <article className="reservation-card surface" key={reservation.id}>
                <div className="room-heading"><span className="icon-tile"><Icon name="room" size={34} /></span><div><h2>{reservation.room.name}</h2><p className="muted">Room {reservation.room.room_number}</p></div></div>
                <div className="reservation-date"><Icon name="calendar" size={25} /><span>{dateLabel(reservation.start_time)}</span></div>
                <div className="reservation-hours"><Icon name="clock" size={25} /><span><span>{timeLabel(reservation.start_time)} – {timeLabel(reservation.end_time)}</span>{!sameDay && <small>Ends {dateLabel(reservation.end_time)}</small>}</span></div>
                <button className="button button-danger" disabled={busy} aria-busy={busy} aria-label={`Cancel reservation for ${reservation.room.name} on ${dateLabel(reservation.start_time)}`} onClick={() => handleCancel(reservation.id)}>{busy && <span className="spinner" />}{busy ? 'Cancelling…' : 'Cancel'}</button>
              </article>
            )
          })}
        </div>
      ) : <EmptyState title="No reservations yet" description="Your reservations will appear here."><Link className="button button-primary" to="/rooms">Browse rooms</Link></EmptyState>}
    </section>
  )
}
