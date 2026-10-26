import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Alert, AuthLayout, EmailField, PasswordField, SubmitButton } from '../components/UI'
import { API_URL } from '../config'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = await response.json()
      if (response.ok) {
        localStorage.setItem('access_token', data.access_token)
        navigate('/rooms')
      } else {
        setError(data.detail || 'Unable to sign in. Check your email and password.')
      }
    } catch {
      setError('Failed to connect to server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout title="Welcome back" description="Sign in to book your next meeting room." footer={<p className="auth-footer-bordered">Don’t have an account? <Link to="/register">Register</Link></p>}>
      <form className="auth-form" onSubmit={handleSubmit}>
        <EmailField value={email} onChange={event => setEmail(event.target.value)} />
        <PasswordField value={password} onChange={event => setPassword(event.target.value)} />
        <div className="forgot-link"><Link to="/forgot-password">Forgot password?</Link></div>
        <Alert>{error}</Alert>
        <SubmitButton loading={loading} loadingText="Signing in…">Login</SubmitButton>
      </form>
    </AuthLayout>
  )
}
