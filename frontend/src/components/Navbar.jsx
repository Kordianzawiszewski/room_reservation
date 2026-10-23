import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { Brand } from './UI'
import Icon from './Icon'

export default function Navbar() {
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  function logout() {
    localStorage.removeItem('access_token')
    navigate('/login')
  }
  return (
    <header className="site-header">
      <div className="navbar">
        <NavLink to="/rooms" className="brand-link" aria-label="Room Booking home" onClick={() => setOpen(false)}><Brand /></NavLink>
        <button className="button button-ghost menu-toggle" aria-label={open ? 'Close navigation' : 'Open navigation'} aria-expanded={open} aria-controls="main-navigation" onClick={() => setOpen(!open)}><Icon name={open ? 'close' : 'menu'} /></button>
        <nav id="main-navigation" aria-label="Main navigation" className={`nav-links ${open ? 'is-open' : ''}`}>
          {[['/rooms', 'Rooms'], ['/reservations', 'My reservations'], ['/ai-search', 'AI Search'], ['/google-calendar', 'Google Calendar']].map(([to, label]) => <NavLink key={to} to={to} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} onClick={() => setOpen(false)}>{label}</NavLink>)}
          <button className="button button-ghost logout" onClick={logout}><Icon name="logout" />Logout</button>
        </nav>
      </div>
    </header>
  )
}
