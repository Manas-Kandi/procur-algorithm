import { type PropsWithChildren, useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { X } from 'lucide-react'
import { Navigation } from './Navigation'
import { ProcurSidebar } from '../../components/ui/ProcurSidebar'
// import { RoleBadge } from '../../ui/components/RoleBadge'

export function AppLayout({ children }: PropsWithChildren): JSX.Element {
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const selectedKey = useMemo(() => {
    const p = location.pathname
    if (p.startsWith('/portfolio')) return 'portfolio'
    if (p.startsWith('/requests/new')) return 'new-request'
    return 'dashboard'
  }, [location.pathname])

  const isDashboard = selectedKey === 'dashboard'

  return (
    <div className="min-h-screen bg-[var(--core-color-surface-background)] text-[var(--core-color-text-primary)]">
      <div className="flex min-h-screen">
        {/* Desktop sidebar (Procur variant) */}
        <div className="hidden lg:block">
          <ProcurSidebar
            open={sidebarOpen}
            onToggle={() => {
              setSidebarOpen((v) => !v)
            }}
            selectedKey={selectedKey}
            onSelect={(key) => {
              if (key === 'dashboard') void navigate('/')
              else if (key === 'new-request') void navigate('/requests/new')
              else if (key === 'portfolio') void navigate('/portfolio')
            }}
          />
        </div>

        {/* Mobile navigation */}
        {mobileNavOpen && (
          <div className="lg:hidden">
            <div className="fixed inset-0 z-40 flex">
              <div
                className="absolute inset-0 bg-slate-900/40"
                onClick={() => {
                  setMobileNavOpen(false)
                }}
              />
              <div className="relative ml-0 flex h-full w-72 flex-col bg-[var(--core-color-surface-canvas)] shadow-200">
                <div className="flex items-center justify-between border-b border-[var(--core-color-border-default)] px-4 py-3">
                  <span className="text-sm font-semibold uppercase tracking-wide text-[var(--core-color-text-muted)]">
                    Navigation
                  </span>
                  <button
                    type="button"
                    onClick={() => {
                      setMobileNavOpen(false)
                    }}
                    className="rounded-lg p-2 text-[var(--core-color-text-muted)] hover:bg-[var(--core-color-surface-subtle)]"
                    aria-label="Close navigation"
                  >
                    <X className="h-5 w-5" aria-hidden="true" />
                  </button>
                </div>
                <Navigation
                  variant="mobile"
                  onNavigate={() => {
                    setMobileNavOpen(false)
                  }}
                />
              </div>
            </div>
          </div>
        )}

        <div className="flex w-full flex-col">
          <main className={`flex-1 overflow-y-auto ${isDashboard ? 'bg-[#0A0A0A]' : ''}`}>
            <div className="mx-auto w-full max-w-[1320px] px-4 py-6 sm:px-6 lg:px-8">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
