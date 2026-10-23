import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import handleUnauthorized from '../utils/handleUnauthorized'
import { Alert, EmptyState, PageHeader, RoomCard, Skeletons } from '../components/UI'

export default function RoomsPage() {
  const [rooms, setRooms] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const controller = new AbortController()
    async function fetchRooms() {
      try {
        const response = await fetch('http://localhost:8000/rooms', {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
          signal: controller.signal,
        })
        if (handleUnauthorized(response, navigate)) return
        if (!response.ok) throw new Error('Failed to fetch rooms')
        setRooms(await response.json())
      } catch (error) {
        if (error.name !== 'AbortError') setError(error.message)
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }
    fetchRooms()
    return () => controller.abort()
  }, [navigate])

  return (
    <section>
      <PageHeader title="Rooms" description="Find the right space for your next meeting." />
      {loading ? <Skeletons /> : error ? <Alert>{error}</Alert> : rooms.length ? <div className="rooms-grid">{rooms.map(room => <RoomCard key={room.id} room={room} reservable />)}</div> : <EmptyState icon="room" title="No rooms to display" description="Rooms will appear here when they are available in the booking system." />}
    </section>
  )
}
