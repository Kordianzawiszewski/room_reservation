import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  const token = searchParams.get('token')

  const [newPassword, setNewPassword] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()

    const response = await fetch('http://localhost:8000/reset-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: token,
        new_password: newPassword,
      }),
    })

    const data = await response.json()

    if (response.ok) {
      navigate('/login')
    } else {
      setError(data.detail || 'Failed to reset password')
    }
  }

  return (
    <div>
      <h1>Reset password</h1>

      <form onSubmit={handleSubmit}>
        <input
          type="password"
          placeholder="New password"
          value={newPassword}
          onChange={(event) => setNewPassword(event.target.value)}
        />

        <button type="submit">
          Change password
        </button>
      </form>

      {error && <p>{error}</p>}
    </div>
  )
}

export default ResetPasswordPage