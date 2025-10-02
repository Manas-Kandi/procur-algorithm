import { PropsWithChildren, useEffect, useRef, useState } from 'react'
import { Menu, Search, X } from 'lucide-react'
import { Navigation } from './Navigation'
import { useAuthStore } from '../../store/auth'
// import { RoleBadge } from '../../ui/components/RoleBadge'

export function AppLayout ({ children }: PropsWithChildren): JSX.Element {
  const { user, logout } = useAuthStore()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const userMenuRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!userMenuOpen) return
    const onClick = (e: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false)
      }
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setUserMenuOpen(false)
    }
    document.addEventListener('mousedown', onClick)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onClick)
      document.removeEventListener('keydown', onKey)
    }
  }, [userMenuOpen])

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
          <header className="sticky top-0 z-30 flex h-16 items-center border-b border-gray-100 bg-white px-4 sm:px-6">
            {/* Left section: mobile menu only */}
            <div className="flex min-w-0 flex-1 items-center gap-3">
              <button
                type="button"
                className="rounded-sm bg-[var(--core-color-surface-subtle)] p-2 text-[var(--core-color-text-primary)] hover:bg-[var(--core-color-surface-background)] lg:hidden"
                onClick={() => setMobileNavOpen(true)}
                aria-label="Open navigation"
              >
                <Menu className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>

            {/* Center section: search */}
            <div className="mx-4 hidden md:block">
              <label htmlFor="global-search" className="sr-only">Search</label>
              <div className="relative w-[400px]">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--core-color-text-muted)]" aria-hidden="true" />
                <input
                  id="global-search"
                  name="search"
                  type="search"
                  placeholder="Search..."
                  className="w-full rounded-sm border border-gray-200 bg-[var(--core-color-surface-sunken)] py-2 pl-10 pr-4 text-sm text-[var(--core-color-text-primary)] placeholder:text-[var(--core-color-text-muted)] focus:border-[var(--core-color-border-focus)] focus:outline-none focus:ring-1 focus:ring-[var(--core-color-border-focus)]/40"
                />
              </div>
            </div>

            {/* Right section: user avatar only */}
            <div className="flex min-w-0 flex-1 items-center justify-end gap-4">
              {user && (
                <div className="relative" ref={userMenuRef}>
                  <button
                    type="button"
                    onClick={() => setUserMenuOpen((v) => !v)}
                    aria-haspopup="menu"
                    aria-expanded={userMenuOpen}
                    className="flex h-8 w-8 items-center justify-center rounded-full border border-gray-200 bg-[var(--core-color-surface-subtle)] text-xs font-semibold text-[var(--core-color-text-primary)] transition-colors hover:bg-[var(--core-color-surface-background)]"
                  >
                    {(user.full_name ?? user.username).charAt(0).toUpperCase()}
                  </button>
                  {userMenuOpen && (
                    <div className="absolute right-0 mt-2 w-44 rounded-sm border border-[var(--core-color-border-subtle)] bg-[var(--core-color-surface-raised)] py-1 text-sm shadow-200">
                      <button className="block w-full px-3 py-2 text-left text-[var(--core-color-text-secondary)] hover:bg-[var(--core-color-surface-subtle)]">Profile</button>
                      <button className="block w-full px-3 py-2 text-left text-[var(--core-color-text-secondary)] hover:bg-[var(--core-color-surface-subtle)]">Settings</button>
                      <div className="my-1 h-px bg-[var(--core-color-border-subtle)]" />
                      <button
                        className="block w-full px-3 py-2 text-left text-[var(--core-color-text-primary)] hover:bg-[var(--core-color-surface-subtle)]"
                        onClick={() => { setUserMenuOpen(false); logout() }}
                      >
                        Sign out
                      </button>
                    </div>
                  )}
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
