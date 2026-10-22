import '../App.css'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  async function handleSubmit(event) {
    event.preventDefault()

    const response = await fetch('http://localhost:8000/login', {
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
      localStorage.setItem('access_token', data.access_token)
      navigate('/rooms')
    } else {
      console.log(data)
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

        <button type="submit">Login</button>
      </form>

      <p>
        Don't have an account? <Link to="/register">Register</Link>
      </p>
      <Link to="/forgot-password">
        Forgot password?
      </Link>
    </div>
  )
}

export default LoginPage
