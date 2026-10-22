import { useEffect, useState } from 'react'
import {useNavigate} from "react-router-dom";

function RoomsPage() {
    const [rooms, setRooms] = useState([])
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    function handleLogout() {
        localStorage.removeItem('access_token')
        navigate('/login')
    }

    useEffect(() => {
        async function fetchRooms() {
            const token = localStorage.getItem('access_token')

            try {
                const response = await fetch('http://localhost:8000/rooms', {
                  headers: {
                    Authorization: `Bearer ${token}`,
                  },
                })

                if (!response.ok) {
                    throw new Error('Failed to fetch rooms')
                  }

                const data = await response.json()
                setRooms(data)
            } catch (error) {
                setError(error.message)
            } finally {
                setLoading(false)
            }
        }

            fetchRooms()
    }, [])

    if (loading) {
      return <p>Loading rooms...</p>
    }

    if (error) {
      return <p>{error}</p>
    }

    return (
    <div>
        <h1>Rooms</h1>

        <button onClick={handleLogout}>
          Logout
        </button>

        {rooms.map((room) => (
          <div key={room.id}>
            <h2>{room.name}</h2>
            <p>Room number: {room.room_number}</p>
            <p>Capacity: {room.capacity}</p>
            <p>Floor: {room.floor}</p>

            <button onClick={() => navigate(`/rooms/${room.id}/reserve`)}>
              Reserve
            </button>
          </div>
        ))}
    </div>
    )
}

export default RoomsPage