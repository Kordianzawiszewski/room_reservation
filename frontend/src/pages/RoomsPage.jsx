import { useEffect, useState } from 'react'
import {useNavigate} from "react-router-dom";

function RoomsPage() {
    const [rooms, setRooms] = useState([])
    const navigate = useNavigate()

    function handleLogout() {
        localStorage.removeItem('access_token')
        navigate('/login')
    }

    useEffect(() => {
        async function fetchRooms() {
            const token = localStorage.getItem('access_token')

            const response = await fetch('http://localhost:8000/rooms', {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            })

            const data = await response.json()
            setRooms(data)
            }

            fetchRooms()
    }, [])

    return (
    <div>
        <h1>Rooms</h1>

        <button onClick={handleLogout}>
          Logout
        </button>

        <pre>{JSON.stringify(rooms, null, 2)}</pre>
    </div>
    )
}

export default RoomsPage