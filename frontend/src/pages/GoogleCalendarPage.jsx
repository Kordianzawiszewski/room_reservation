import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import handleUnauthorized from '../utils/handleUnauthorized'
import Icon from '../components/Icon'
import { Alert, PageHeader, Skeletons } from '../components/UI'
import { API_URL } from '../config'

function GoogleCalendarIcon() {
  return <svg className="google-calendar-logo" viewBox="0 0 64 64" aria-hidden="true"><path fill="#4285f4" d="M8 4h48a4 4 0 0 1 4 4v36L44 60H8a4 4 0 0 1-4-4V8a4 4 0 0 1 4-4Z" /><path fill="#fff" d="M16 16h32v32H16z" /><path fill="#1967d2" d="M48 16h12v28L48 48z" /><path fill="#fbbc04" d="M48 16h12v28H48z" /><path fill="#34a853" d="M4 48h40v12H8a4 4 0 0 1-4-4z" /><path fill="#ea4335" d="M44 44h16L44 60z" /><path fill="#188038" d="M44 48v12l4-12z" /><text x="32" y="39" fill="#4285f4" textAnchor="middle" fontSize="25" fontFamily="Arial, sans-serif" fontWeight="600">31</text></svg>
}

export default function GoogleCalendarPage() {
  const [connected, setConnected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [pending, setPending] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const controller = new AbortController()
    async function fetchStatus() {
      try {
        const response = await fetch(`${API_URL}/integrations/google/status`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
          signal: controller.signal,
        })
        if (handleUnauthorized(response, navigate)) return
        const data = await response.json()
        if (response.ok) {
          setConnected(data.connected)
        } else {
          setError(data.detail || 'Failed to check Google Calendar status')
        }
      } catch (error) {
        if (error.name !== 'AbortError') setError('Failed to connect to server. Please try again.')
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }
    fetchStatus()
    return () => controller.abort()
  }, [navigate])

  async function handleConnect() {
    setPending('connect')
    setError('')
    let redirecting = false
    try {
      const response = await fetch(`${API_URL}/integrations/google/connect`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      })
      if (handleUnauthorized(response, navigate)) return
      const data = await response.json()
      if (response.ok) {
        window.location.href = data.authorization_url
        redirecting = true
      } else {
        setError(data.detail || 'Failed to connect Google Calendar')
      }
    } catch {
      setError('Failed to connect to server. Please try again.')
    } finally {
      if (!redirecting) setPending('')
    }
  }

  async function handleDisconnect() {
    setPending('disconnect')
    setError('')
    try {
      const response = await fetch(`${API_URL}/integrations/google`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      })
      if (handleUnauthorized(response, navigate)) return
      const data = await response.json()
      if (response.ok) {
        setConnected(false)
      } else {
        setError(data.detail || 'Failed to disconnect Google Calendar')
      }
    } catch {
      setError('Failed to connect to server. Please try again.')
    } finally {
      setPending('')
    }
  }

  return (
    <section>
      <PageHeader title="Google Calendar" description="Manage your calendar connection." />
      {loading ? <div className="integration-skeleton"><Skeletons count={1} rows /></div> : connected === null ? <div className="integration-unavailable surface"><Alert>{error || 'Unable to check your calendar connection.'}</Alert></div> : (
        <div className="integration-card surface">
          <div className="integration-heading">
            <span className="google-icon"><GoogleCalendarIcon /></span>
            <div><h2>Google Calendar</h2><span className={`badge ${connected ? 'badge-success' : 'badge-neutral'}`}>{connected && <Icon name="check" size={16} />}{connected ? 'Connected' : 'Not connected'}</span></div>
          </div>
          <p className="integration-description">{connected ? <>New reservations are added to your calendar.<br />Cancelling a reservation also removes its calendar event.</> : 'Connect your account to add new room reservations to your Google Calendar automatically.'}</p>
          <Alert>{error}</Alert>
          <button className={`button button-full ${connected ? 'button-danger' : 'button-primary'}`} disabled={Boolean(pending)} aria-busy={Boolean(pending)} onClick={connected ? handleDisconnect : handleConnect}>
            {pending ? <span className="spinner" /> : connected ? <Icon name="trash" /> : <Icon name="calendar" />}
            {pending === 'connect' ? 'Connecting…' : pending === 'disconnect' ? 'Disconnecting…' : connected ? 'Disconnect' : 'Connect Google Calendar'}
          </button>
          <p className="integration-footer"><Icon name="calendar" size={18} />Events are saved to your primary calendar.</p>
        </div>
      )}
    </section>
  )
}
