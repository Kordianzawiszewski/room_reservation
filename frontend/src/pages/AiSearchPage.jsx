import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import handleUnauthorized from '../utils/handleUnauthorized'

function AISearchPage() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()

    const token = localStorage.getItem('access_token')
    const navigate = useNavigate()

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch(
        'http://localhost:8000/ai/search-rooms',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            query: query,
          }),
        }
      )

      if (handleUnauthorized(response, navigate)) {
        return
      }

      const data = await response.json()

      if (response.ok) {
        setResult(data)
      } else {
        setError(data.detail || 'AI search failed')
      }
    } catch {
      setError('Failed to connect to server')
    } finally {
      setLoading(false)
    }
  }

  function renderResult() {
  if (!result) {
    return null
  }

  if (result.intent === 'rooms_search') {
    if (!result.rooms || result.rooms.length === 0) {
      return <p>No rooms found.</p>
    }

    return (
      <div>
        <h2>Available rooms</h2>

        {result.rooms.map((room) => (
          <div key={room.id}>
            <h3>{room.name}</h3>
            <p>Room number: {room.room_number}</p>
            <p>Capacity: {room.capacity}</p>
            <p>Floor: {room.floor}</p>
          </div>
        ))}
      </div>
    )
  }

  if (result.intent === 'room_availability') {
    return (
      <div>
        <h2>Room availability</h2>

        {result.available !== null && (
          <p>
            {result.available
              ? 'The room is available.'
              : 'The room is not available.'}
          </p>
        )}

        {result.free_slots && result.free_slots.length > 0 && (
          <div>
            <h3>Free slots</h3>

            {result.free_slots.map((slot, index) => (
              <p key={index}>
                {new Date(slot[0]).toLocaleString('pl-PL')}
                {' - '}
                {new Date(slot[1]).toLocaleString('pl-PL')}
              </p>
            ))}
          </div>
        )}
      </div>
    )
  }

      return <p>Unknown AI response.</p>
    }

  return (
  <div>
    <h1>AI Room Search</h1>

    <p>
      Describe what room you need using natural language.
    </p>

    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="e.g. Find a room for 10 people tomorrow from 12:00 to 14:00"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
      />

      <button type="submit">
        Search
      </button>
    </form>

    {loading && <p>Searching...</p>}

    {error && <p>{error}</p>}

    {result && renderResult()}
  </div>
    )
}

export default AISearchPage