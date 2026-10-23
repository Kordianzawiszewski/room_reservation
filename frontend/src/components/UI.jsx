import { useState } from 'react'
import { Link } from 'react-router-dom'
import Icon from './Icon'

export function Brand() {
  return (
    <span className="brand">
      <span className="brand-mark"><Icon name="door" size={25} /></span>
      <span>Room Booking</span>
    </span>
  )
}

export function PageHeader({ title, description }) {
  return <header className="page-header"><h1>{title}</h1><p>{description}</p></header>
}

export function Alert({ children, type = 'error' }) {
  if (!children) return null
  const message = typeof children === 'string'
    ? children
    : Array.isArray(children)
      ? children.map(item => item.msg || String(item)).join('. ')
      : 'Something went wrong. Please try again.'

  return (
    <div className={`alert alert-${type}`} role={type === 'error' ? 'alert' : 'status'}>
      <Icon name={type === 'success' ? 'check' : 'alert'} />
      <span>{message}</span>
    </div>
  )
}

export function SubmitButton({ loading, children, loadingText, className = '', ...props }) {
  return (
    <button type="submit" className={`button button-primary ${className}`} disabled={loading} aria-busy={loading} {...props}>
      {loading && <span className="spinner" />}
      {loading ? loadingText : children}
    </button>
  )
}

export function PasswordField({ id = 'password', label = 'Password', value, onChange, autoComplete = 'current-password' }) {
  const [visible, setVisible] = useState(false)
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <div className="input-wrap">
        <Icon name="lock" />
        <input id={id} name={id} type={visible ? 'text' : 'password'} value={value} onChange={onChange} placeholder="Enter your password" autoComplete={autoComplete} required />
        <button type="button" className="input-action" aria-label={visible ? 'Hide password' : 'Show password'} aria-pressed={visible} onClick={() => setVisible(!visible)}>
          <Icon name={visible ? 'eyeOff' : 'eye'} />
        </button>
      </div>
    </div>
  )
}

export function EmailField({ value, onChange }) {
  return (
    <div className="field">
      <label htmlFor="email">Email</label>
      <div className="input-wrap">
        <Icon name="mail" />
        <input id="email" name="email" type="email" placeholder="you@company.com" autoComplete="email" value={value} onChange={onChange} required />
      </div>
    </div>
  )
}

export function AuthLayout({ title, description, icon, children, footer }) {
  return (
    <main className="auth-page">
      <div className="auth-content">
        <Brand />
        <section className="auth-card surface">
          {icon && <div className="auth-icon icon-tile"><Icon name={icon} size={30} /></div>}
          <header className="auth-header"><h1>{title}</h1><p>{description}</p></header>
          {children}
          {footer && <div className="auth-footer">{footer}</div>}
        </section>
      </div>
    </main>
  )
}

export function BackToLogin() {
  return <Link className="back-link" to="/login"><Icon name="arrow" />Back to login</Link>
}

export function RoomCard({ room, reservable = false }) {
  return (
    <article className="room-card surface">
      <div className="room-heading">
        <span className="icon-tile"><Icon name="room" size={30} /></span>
        <div><h2>{room.name}</h2><p className="muted">Room {room.room_number}</p></div>
      </div>
      <dl className="room-details">
        <div><dt><Icon name="users" /><span className="sr-only">Capacity</span></dt><dd>{room.capacity} people</dd></div>
        <div><dt><Icon name="building" /><span className="sr-only">Floor</span></dt><dd>Floor {room.floor}</dd></div>
      </dl>
      {reservable && <Link className="button button-primary button-full" to={`/rooms/${room.id}/reserve`} state={{ room }}>Reserve</Link>}
    </article>
  )
}

export function EmptyState({ icon = 'calendar', title, description, children }) {
  return (
    <div className="empty-state surface">
      <span className="icon-tile"><Icon name={icon} size={30} /></span>
      <h2>{title}</h2>
      <p>{description}</p>
      {children}
    </div>
  )
}

export function Skeletons({ rows = false, count = 6 }) {
  return (
    <div className={rows ? 'reservation-list' : 'rooms-grid'} role="status" aria-label="Loading">
      <span className="sr-only">Loading…</span>
      {Array.from({ length: count }, (_, i) => (
        <div className={`surface skeleton-card ${rows ? 'skeleton-row' : ''}`} key={i} aria-hidden="true">
          <div className="skeleton skeleton-icon" />
          <div className="skeleton skeleton-title" />
          <div className="skeleton skeleton-line" />
          <div className="skeleton skeleton-line short" />
          {!rows && <div className="skeleton skeleton-button" />}
        </div>
      ))}
    </div>
  )
}
