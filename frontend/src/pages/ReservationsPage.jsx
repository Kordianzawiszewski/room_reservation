import { useEffect, useState } from 'react'

function ReservationsPage() {
  const [reservations, setReservations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchReservations() {
      const token = localStorage.getItem('access_token')

      try {
        const response = await fetch('http://localhost:8000/reservations/me', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (!response.ok) {
          throw new Error('Failed to fetch reservations')
        }

        const data = await response.json()
        setReservations(data)
      } catch (error) {
        setError(error.message)
      } finally {
        setLoading(false)
      }
    }

    fetchReservations()
  }, [])

  if (loading) {
    return <p>Loading reservations...</p>
  }

  if (error) {
    return <p>{error}</p>
  }

  async function handleCancel(reservationId) {
      const token = localStorage.getItem('access_token')

      const response = await fetch(
        `http://localhost:8000/reservations/${reservationId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      const data = await response.json()

      if (response.ok) {
        setReservations((currentReservations) =>
          currentReservations.filter(
            (reservation) => reservation.id !== reservationId
          )
        )
      } else {
        setError(data.detail || 'Failed to cancel reservation')
      }
    }

  return (
    <div>
        <h1>My reservations</h1>

        {reservations.map((reservation) => (
        <div key={reservation.id}>
            <p>Room: {reservation.room.name}</p>
            <p>Room number: {reservation.room.room_number}</p>
            <p>
              Start: {new Date(reservation.start_time).toLocaleString('pl-PL', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
            <p>
              End: {new Date(reservation.end_time).toLocaleString('pl-PL', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
            <button onClick={() => handleCancel(reservation.id)}>
              Cancel
            </button>
        </div>
        ))}
    </div>
    )
}

export default ReservationsPage