import { useParams } from 'react-router-dom'
import { useState } from 'react'

function ReservationPage() {
    const { roomId } = useParams()
    const [startTime, setStartTime] = useState('')
    const [endTime, setEndTime] = useState('')
    const [message, setMessage] = useState('')
    const [error, setError] = useState('')

    async function handleSubmit(event) {
        event.preventDefault()

        const token = localStorage.getItem('access_token')

        const response = await fetch('http://localhost:8000/reservations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          room_id: Number(roomId),
          start_time: startTime,
          end_time: endTime,
        }),
        })

        const data = await response.json()

        if (response.ok) {
          setMessage('Reservation created successfully')
          setError('')
        } else {
          setError(data.detail || 'Failed to create reservation')
          setMessage('')
        }
    }

    return (
        <div>
            <h1>Create Reservation</h1>
            <form onSubmit={handleSubmit}>
              <label>
                Start:
                <input
                  type="datetime-local"
                  value={startTime}
                  onChange={(event) => setStartTime(event.target.value)}
                />
              </label>

              <label>
                End:
                <input
                  type="datetime-local"
                  value={endTime}
                  onChange={(event) => setEndTime(event.target.value)}
                />
              </label>

              <button type="submit">
                Create reservation
              </button>
            </form>
            {message && <p>{message}</p>}
            {error && <p>{error}</p>}
        </div>
    )
}

export default ReservationPage