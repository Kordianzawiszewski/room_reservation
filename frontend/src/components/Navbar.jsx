import { Link, useNavigate } from 'react-router-dom'

function Navbar() {
  const navigate = useNavigate()

  function handleLogout() {
    localStorage.removeItem('access_token')
    navigate('/login')
  }

  return (
    <nav>
      <Link to="/rooms">Rooms</Link>
      <Link to="/reservations">My reservations</Link>
      <Link to="/ai-search">AI Search</Link>
      <Link to="/google-calendar">Google Calendar</Link>

      <button onClick={handleLogout}>
        Logout
      </button>
    </nav>
  )
}

export default Navbar