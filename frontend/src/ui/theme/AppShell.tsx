import { PropsWithChildren } from 'react'
import { RoleBadge } from '../components/RoleBadge'

export function AppShell ({ children }: PropsWithChildren): JSX.Element {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-brand">
          <span className="app-logo" aria-hidden>⚙️</span>
          <span className="app-title">ProcureAI</span>
        </div>
        <div className="app-header-meta">
          <RoleBadge role="Buyer" />
        </div>
      </header>
      <div className="app-body">
        <nav className="app-nav" aria-label="Primary">
          <ul>
            <li><a className="active" href="#">Dashboard</a></li>
            <li><a href="#">Requests</a></li>
            <li><a href="#">Negotiations</a></li>
          </ul>
        </nav>
        <div className="app-content">
          {children}
        </div>
      </div>
    </div>
  )
}
