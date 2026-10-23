const paths = {
  door: <><rect x="5" y="2" width="14" height="20" rx="2" /><path d="M15 12h.01" /></>,
  room: <><rect x="5" y="8" width="14" height="8" rx="2" /><path d="M8 8V5a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v3m2 0V5a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v3M8 16v4m3-4v4m2-4v4m3-4v4M2 10v4h3m17-4v4h-3" /></>,
  users: <><circle cx="9" cy="8" r="4" /><path d="M2 21v-2a7 7 0 0 1 14 0v2M16 4a4 4 0 0 1 0 8m3 3a7 7 0 0 1 3 6" /></>,
  building: <><rect x="5" y="2" width="14" height="20" rx="1" /><path d="M9 6h.01M15 6h.01M9 10h.01M15 10h.01M9 14h.01M15 14h.01M10 22v-4h4v4" /></>,
  calendar: <><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M16 3v4M8 3v4M3 11h18M8 15h.01M12 15h.01M16 15h.01M8 18h.01M12 18h.01" /></>,
  clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
  logout: <><path d="M9 4H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4m5-13 5 5-5 5m-6-5h13" /></>,
  arrow: <path d="m10 5-7 7 7 7M3 12h18" />,
  mail: <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 6 9 7 9-7" /></>,
  lock: <><rect x="5" y="10" width="14" height="11" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3m-4 5v2" /></>,
  eye: <><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7S2 12 2 12Z" /><circle cx="12" cy="12" r="3" /></>,
  eyeOff: <><path d="m3 3 18 18M10.6 5.1 12 5c7 0 10 7 10 7a19 19 0 0 1-3 4M6 6a19 19 0 0 0-4 6s3 7 10 7a12 12 0 0 0 5-1" /><path d="M10 10a3 3 0 0 0 4 4" /></>,
  key: <><circle cx="16" cy="8" r="5" /><path d="m12 12-9 9v-5h4v-4h4M17 7h.01" /></>,
  search: <><circle cx="10.5" cy="10.5" r="7.5" /><path d="m16 16 6 6" /></>,
  sparkle: <><path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3ZM20 2v4m-2-2h4" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  alert: <><circle cx="12" cy="12" r="9" /><path d="M12 7v6m0 4h.01" /></>,
  trash: <><path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7m4-7v7" /></>,
  menu: <path d="M3 6h18M3 12h18M3 18h18" />,
  close: <path d="m6 6 12 12M6 18 18 6" />,
}

export default function Icon({ name, size = 20, className = '' }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className={className}>{paths[name] || paths.room}</svg>
}
