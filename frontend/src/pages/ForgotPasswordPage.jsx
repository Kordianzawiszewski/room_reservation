import { useState } from 'react'

function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()

    try {
      const response = await fetch('http://localhost:8000/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setMessage(data.message)
        setError('')
      } else {
        setError(data.detail || 'Failed to send reset link')
        setMessage('')
      }
    } catch (error) {
      setError('Failed to connect to server')
      setMessage('')
    }
  }

  return (
    <div>
      <h1>Forgot password</h1>

      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />

        <button type="submit">
          Send reset link
        </button>
      </form>

      {message && <p>{message}</p>}
      {error && <p>{error}</p>}
    </div>
  )
}

export default ForgotPasswordPage