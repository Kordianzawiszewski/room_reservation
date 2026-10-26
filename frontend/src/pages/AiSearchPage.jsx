import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import handleUnauthorized from '../utils/handleUnauthorized'
import Icon from '../components/Icon'
import { Alert, EmptyState, RoomCard, Skeletons, SubmitButton } from '../components/UI'
import { API_URL } from '../config'

export default function AISearchPage() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const response = await fetch(`${API_URL}/ai/search-rooms`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ query }),
      })
      if (handleUnauthorized(response, navigate)) return
      const data = await response.json()
      if (response.ok) {
        setResult(data)
      } else {
        setError(data.detail || 'AI search failed')
      }
    } catch {
      setError('Failed to connect to server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  function renderResult() {
    if (result.intent === 'rooms_search') {
      if (!result.rooms?.length) {
        return <EmptyState icon="search" title="No matching rooms found" description="Try a different time range or a smaller capacity." />
      }
      return <><h2>Matching rooms</h2><div className="rooms-grid">{result.rooms.map(room => <RoomCard key={room.id} room={room} />)}</div></>
    }
    if (result.intent === 'room_availability') {
      return (
        <div className="availability-panel surface">
          <h2>Room availability</h2>
          {typeof result.available === 'boolean' && <p className={`availability-status ${result.available ? 'available' : 'unavailable'}`}><Icon name={result.available ? 'check' : 'alert'} />{result.available ? 'The room is available.' : 'The room is not available.'}</p>}
          {result.free_slots?.length > 0 ? <div className="slots"><h3>Free slots</h3>{result.free_slots.map((slot, index) => <div className="slot" key={index}><Icon name="clock" /><span>{new Date(slot[0]).toLocaleString('pl-PL')} – {new Date(slot[1]).toLocaleString('pl-PL')}</span></div>)}</div> : result.available == null && <p className="muted">No free slots found for this day.</p>}
        </div>
      )
    }
    return <Alert>Unknown AI response. Please try another search.</Alert>
  }

  return (
    <section className="ai-content">
      <header className="ai-header">
        <span className="badge badge-ai">AI search</span>
        <h1>Find a room</h1>
        <p>Enter the number of people, date and time.</p>
      </header>
      <form className="search-card surface" onSubmit={handleSubmit}>
        <label htmlFor="ai-query">What are you looking for?</label>
        <div className="search-row">
          <div className="input-wrap"><Icon name="search" size={22} /><input id="ai-query" type="text" placeholder="Find a room for 10 people tomorrow from 12:00 to 14:00" value={query} onChange={event => setQuery(event.target.value)} required /></div>
          <SubmitButton loading={loading} loadingText="Searching…">Search</SubmitButton>
        </div>
        {!result && !loading && <p className="search-examples">You can also ask about a specific room, e.g. “When is room 201 available tomorrow?”</p>}
      </form>
      {error && <div className="search-feedback"><Alert>{error}</Alert></div>}
      {loading && <div className="search-results" aria-busy="true"><h2>Searching for rooms…</h2><Skeletons count={2} /></div>}
      {result && <div className="search-results" aria-live="polite">{renderResult()}</div>}
    </section>
  )
}
