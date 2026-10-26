import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Alert, AuthLayout, BackToLogin, PasswordField, SubmitButton } from '../components/UI'
import { API_URL } from '../config'

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')
  const [newPassword, setNewPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_URL}/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: newPassword }),
      })
      const data = await response.json()
      if (response.ok) {
        navigate('/login')
      } else {
        setError(data.detail || 'Failed to reset password')
      }
    } catch {
      setError('Failed to connect to server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout title="Set a new password" description="Enter your new password to regain access." icon="key" footer={<BackToLogin />}>
      <form className="auth-form" onSubmit={handleSubmit}>
        <PasswordField id="new-password" label="New password" value={newPassword} onChange={event => setNewPassword(event.target.value)} autoComplete="new-password" />
        <Alert>{error}</Alert>
        <SubmitButton loading={loading} loadingText="Changing password…">Change password</SubmitButton>
      </form>
    </AuthLayout>
  )
}
