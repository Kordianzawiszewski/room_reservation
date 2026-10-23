import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Alert, AuthLayout, EmailField, PasswordField, SubmitButton } from '../components/UI'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setMessage('')
    try {
      const response = await fetch('http://localhost:8000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = await response.json()
      if (response.ok) {
        setMessage('Account created. You can now sign in.')
      } else {
        setError(data.detail || 'Registration failed')
      }
    } catch {
      setError('Failed to connect to server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout title="Create your account" description="Book meeting rooms in one place." footer={<p>Already have an account? <Link to="/login">Login</Link></p>}>
      <form className="auth-form" onSubmit={handleSubmit}>
        <EmailField value={email} onChange={event => setEmail(event.target.value)} />
        <PasswordField value={password} onChange={event => setPassword(event.target.value)} autoComplete="new-password" />
        <Alert>{error}</Alert>
        <Alert type="success">{message}</Alert>
        <SubmitButton loading={loading} loadingText="Creating account…">Register</SubmitButton>
      </form>
    </AuthLayout>
  )
}
