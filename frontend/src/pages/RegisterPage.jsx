import '../App.css'
import { useState } from 'react'
import { Link } from 'react-router-dom'

function RegisterPage() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()

    const response = await fetch('http://localhost:8000/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email,
        password: password,
      })
    })

  const data = await response.json()

  if (response.ok) {
      setError('')
      console.log('Registered')
  } else {
      setError(data.detail || 'Registration failed')
    }
  }

  return (
      <div>
      <h1>Room Booking</h1>

      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />

        <button type="submit">Register</button>
      </form>

      <p>
        Already have an account? <Link to="/login">Login</Link>
      </p>

      {error && <p>{error}</p>}
    </div>
  )
}

export default RegisterPage
