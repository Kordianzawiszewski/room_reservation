import { useState } from 'react'
import { Alert, AuthLayout, BackToLogin, EmailField, SubmitButton } from '../components/UI'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setMessage('')
    try {
      const response = await fetch('http://localhost:8000/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })
      const data = await response.json()
      if (response.ok) {
        setMessage(data.message)
      } else {
        setError(data.detail || 'Failed to send reset link')
      }
    } catch {
      setError('Failed to connect to server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout title="Forgot your password?" description="Enter your email and we’ll send you a reset link." icon="mail" footer={<BackToLogin />}>
      <form className="auth-form" onSubmit={handleSubmit}>
        <EmailField value={email} onChange={event => setEmail(event.target.value)} />
        <Alert>{error}</Alert>
        <Alert type="success">{message}</Alert>
        <SubmitButton loading={loading} loadingText="Sending…">Send reset link</SubmitButton>
      </form>
    </AuthLayout>
  )
}
