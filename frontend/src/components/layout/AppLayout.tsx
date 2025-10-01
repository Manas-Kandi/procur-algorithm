import { PropsWithChildren, useState } from 'react'
import { Menu, Bell, Search, Sparkles, X } from 'lucide-react'
import { Navigation } from './Navigation'
import { useAuthStore } from '../../store/auth'
import { RoleBadge } from '../../ui/components/RoleBadge'

export function AppLayout ({ children }: PropsWithChildren): JSX.Element {
  const { user } = useAuthStore()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  return (
    <div className="min-h-screen bg-[var(--core-color-surface-background)] text-[var(--core-color-text-primary)]">
      <div className="flex min-h-screen">
        {/* Desktop navigation */}
        <Navigation variant="desktop" />

        {/* Mobile navigation */}
        {mobileNavOpen && (
          <div className="lg:hidden">
            <div className="fixed inset-0 z-40 flex">
              <div
                className="absolute inset-0 bg-slate-900/40"
                onClick={() => setMobileNavOpen(false)}
              />
              <div className="relative ml-0 flex h-full w-72 flex-col bg-[var(--core-color-surface-canvas)] shadow-200">
                <div className="flex items-center justify-between border-b border-[var(--core-color-border-default)] px-4 py-3">
                  <span className="text-sm font-semibold uppercase tracking-wide text-[var(--core-color-text-muted)]">Navigation</span>
                  <button
                    type="button"
                    onClick={() => setMobileNavOpen(false)}
                    className="rounded-lg p-2 text-[var(--core-color-text-muted)] hover:bg-[var(--core-color-surface-subtle)]"
                    aria-label="Close navigation"
                  >
                    <X className="h-5 w-5" aria-hidden="true" />
                  </button>
                </div>
                <Navigation variant="mobile" onNavigate={() => setMobileNavOpen(false)} />
              </div>
            </div>
          </div>
        )}

        <div className="flex w-full flex-col">
          <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)] px-4 shadow-100 sm:px-6">
            <div className="flex items-center gap-3">
              <button
                type="button"
                className="rounded-lg bg-[var(--core-color-surface-subtle)] p-2 text-[var(--core-color-text-primary)] hover:bg-[var(--core-color-surface-background)] lg:hidden"
                onClick={() => setMobileNavOpen(true)}
                aria-label="Open navigation"
              >
                <Menu className="h-5 w-5" aria-hidden="true" />
              </button>

              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[var(--core-color-brand-primary)] to-[var(--core-color-brand-secondary)] text-sm font-semibold text-white">
                  PA
                </div>
                <div className="hidden md:block">
                  <p className="text-sm font-semibold text-[var(--core-color-text-primary)]">ProcureAI Workspace</p>
                  <p className="text-xs text-[var(--core-color-text-muted)]">{user?.organization_id ?? 'Global Operations'}</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="hidden lg:block w-72">
                <label htmlFor="global-search" className="sr-only">Search</label>
                <div className="relative">
                  <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--core-color-text-muted)]" aria-hidden="true" />
                  <input
                    id="global-search"
                    name="search"
                    type="search"
                    placeholder="Search requests, vendors, approvals…"
                    className="w-full rounded-lg border border-[var(--core-color-border-default)] bg-[var(--core-color-surface-subtle)] py-2 pl-10 pr-4 text-sm text-[var(--core-color-text-primary)] placeholder:text-[var(--core-color-text-muted)] focus:border-[var(--core-color-border-focus)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-border-focus)]/40"
                  />
                </div>
              </div>

              <div className="hidden md:flex items-center gap-2 rounded-full bg-[var(--core-color-surface-subtle)] px-3 py-1.5 text-xs font-medium text-[var(--core-color-text-muted)]">
                <span className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.6)]" aria-hidden="true" />
                <span>Agent live</span>
                <Sparkles className="h-3.5 w-3.5 text-[var(--core-color-brand-secondary)]" aria-hidden="true" />
              </div>

              <button
                type="button"
                className="relative rounded-full p-2 text-[var(--core-color-text-muted)] transition-colors hover:bg-[var(--core-color-surface-subtle)] hover:text-[var(--core-color-text-primary)]"
                aria-label="View notifications"
              >
                <Bell className="h-5 w-5" aria-hidden="true" />
                <span className="absolute right-2 top-2 inline-flex h-2 w-2 animate-pulse rounded-full bg-[var(--core-color-brand-secondary)]" />
              </button>

              {user && (
                <div className="flex items-center gap-3">
                  <div className="hidden sm:flex flex-col items-end">
                    <span className="text-sm font-semibold text-[var(--core-color-text-primary)]">{user.full_name ?? user.username}</span>
                    <span className="text-xs text-[var(--core-color-text-muted)]">{user.role}</span>
                  </div>
                  <RoleBadge role={user.role} />
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--core-color-brand-primary)] text-sm font-semibold text-white">
                    {(user.full_name ?? user.username).charAt(0).toUpperCase()}
                  </div>
                </div>
              )}
            </div>
          </header>

          <main className="flex-1 overflow-y-auto">
            <div className="mx-auto w-full max-w-[1320px] px-4 py-6 sm:px-6 lg:px-8">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
