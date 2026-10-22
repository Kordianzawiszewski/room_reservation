import { useEffect, useState } from 'react'

function GoogleCalendarPage() {
  const [connected, setConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchStatus() {
      const token = localStorage.getItem('access_token')

      try {
        const response = await fetch(
          'http://localhost:8000/integrations/google/status',
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        )

        const data = await response.json()

        if (response.ok) {
          setConnected(data.connected)
        } else {
          setError(data.detail || 'Failed to check Google Calendar status')
        }
      } catch {
        setError('Failed to connect to server')
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()
  }, [])

  async function handleConnect() {
    const token = localStorage.getItem('access_token')

    try {
      const response = await fetch(
        'http://localhost:8000/integrations/google/connect',
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      const data = await response.json()

      if (response.ok) {
        window.location.href = data.authorization_url
      } else {
        setError(data.detail || 'Failed to connect Google Calendar')
      }
    } catch {
      setError('Failed to connect to server')
    }
  }

  async function handleDisconnect() {
    const token = localStorage.getItem('access_token')

    try {
      const response = await fetch(
        'http://localhost:8000/integrations/google',
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      const data = await response.json()

      if (response.ok) {
        setConnected(false)
        setError('')
      } else {
        setError(data.detail || 'Failed to disconnect Google Calendar')
      }
    } catch {
      setError('Failed to connect to server')
    }
  }

  if (loading) {
    return <p>Loading...</p>
  }

  return (
    <div>
      <h1>Google Calendar</h1>

      {connected ? (
        <>
          <p>Google Calendar is connected.</p>

          <button onClick={handleDisconnect}>
            Disconnect Google Calendar
          </button>
        </>
      ) : (
        <>
          <p>
            Connect your Google Calendar to automatically sync reservations.
          </p>

          <button onClick={handleConnect}>
            Connect Google Calendar
          </button>
        </>
      )}

      {error && <p>{error}</p>}
    </div>
  )
}

export default GoogleCalendarPage