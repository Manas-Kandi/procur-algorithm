import { Link, useLocation } from 'react-router-dom'
import clsx from 'clsx'
import type { LucideIcon } from 'lucide-react'
import {
  LayoutDashboard,
  FilePlus2,
  ShieldCheck,
  BriefcaseBusiness,
  Gauge,
  MessageSquareDot,
  SlidersHorizontal,
  Brain,
  MapPinned,
} from 'lucide-react'
import { useAuthStore } from '../../store/auth'
import type { UserRole } from '../../types'
import { RoleBadge } from '../../ui/components/RoleBadge'

interface NavigationProps {
  variant?: 'desktop' | 'mobile'
  onNavigate?: () => void
}

interface NavItem {
  name: string
  href: string
  icon: LucideIcon
  roles: UserRole[]
  description?: string
}

const buyerNavItems: NavItem[] = [
  {
    name: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
    roles: ['buyer', 'approver', 'admin'],
    description: 'Pipeline overview and smart alerts',
  },
  {
    name: 'New Request',
    href: '/requests/new',
    icon: FilePlus2,
    roles: ['buyer', 'admin'],
    description: 'Launch guided intake flow',
  },
  {
    name: 'Approvals',
    href: '/approvals',
    icon: ShieldCheck,
    roles: ['approver', 'admin'],
    description: 'Decision workspace',
  },
  {
    name: 'Portfolio',
    href: '/portfolio',
    icon: BriefcaseBusiness,
    roles: ['buyer', 'approver', 'admin'],
    description: 'Active subscriptions & renewals',
  },
]

const sellerNavItems: NavItem[] = [
  {
    name: 'Seller Dashboard',
    href: '/seller',
    icon: Gauge,
    roles: ['seller', 'admin'],
    description: 'Pipeline health & activity',
  },
  {
    name: 'Live Deals',
    href: '/seller/negotiations',
    icon: MessageSquareDot,
    roles: ['seller', 'admin'],
    description: 'Active negotiations',
  },
  {
    name: 'Guardrails',
    href: '/seller/guardrails',
    icon: SlidersHorizontal,
    roles: ['seller', 'admin'],
    description: 'Pricing & ZOPA controls',
  },
  {
    name: 'Intelligence',
    href: '/seller/intelligence',
    icon: Brain,
    roles: ['seller', 'admin'],
    description: 'Win/loss insights',
  },
  {
    name: 'Territory',
    href: '/seller/territory',
    icon: MapPinned,
    roles: ['seller', 'admin'],
    description: 'Team & segmentation',
  },
]

const SECTION_CONFIG = {
  buyer: {
    label: 'Buyer Workspace',
    accent: 'bg-[var(--persona-color-buyer-accent)]',
    items: buyerNavItems,
  },
  seller: {
    label: 'Seller Workspace',
    accent: 'bg-[var(--persona-color-seller-accent)]',
    items: sellerNavItems,
  },
}

export function Navigation ({ variant = 'desktop', onNavigate }: NavigationProps): JSX.Element | null {
  const location = useLocation()
  const { user, logout } = useAuthStore()

  if (!user) return null

  const sections: Array<{ key: 'buyer' | 'seller'; label: string; accent: string; items: NavItem[] }> = []
  if (['buyer', 'approver', 'admin'].includes(user.role)) {
    sections.push({ key: 'buyer', ...SECTION_CONFIG.buyer })
  }
  if (['seller', 'admin'].includes(user.role)) {
    sections.push({ key: 'seller', ...SECTION_CONFIG.seller })
  }

  const containerClass = clsx(
    'flex w-72 flex-col bg-[var(--core-color-surface-canvas)]',
    variant === 'desktop' && 'hidden border-r border-[var(--core-color-border-default)] shadow-100 lg:flex',
    variant === 'mobile' && 'h-full shadow-200'
  )

  return (
    <nav className={containerClass} aria-label="Primary navigation">
      <div className="flex-1 overflow-y-auto py-6">
        {sections.map((section) => (
          <div key={section.key} className="mb-8">
            <div className="flex items-center gap-2 px-6 text-xs font-semibold uppercase tracking-wider text-[var(--core-color-text-muted)]">
              <span className={clsx('h-1.5 w-1.5 rounded-full', section.accent)} aria-hidden="true" />
              {section.label}
            </div>
            <div className="mt-3 space-y-1 px-3">
              {section.items
                .filter(item => item.roles.includes(user.role))
                .map((item) => {
                  const isRoot = item.href === '/'
                  const isActive = isRoot
                    ? location.pathname === '/'
                    : location.pathname.startsWith(item.href)
                  const ItemIcon = item.icon

                  return (
                    <Link
                      key={item.href}
                      to={item.href}
                      onClick={onNavigate}
                      className={clsx(
                        'group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-[var(--core-color-brand-primary)]/10 text-[var(--core-color-brand-primary)]'
                          : 'text-[var(--core-color-text-muted)] hover:bg-[var(--core-color-surface-subtle)] hover:text-[var(--core-color-text-primary)]'
                      )}
                    >
                      <span className={clsx(
                        'flex h-8 w-8 items-center justify-center rounded-md border text-[var(--core-color-text-muted)] transition-colors',
                        isActive
                          ? 'border-[var(--core-color-brand-primary)] bg-[var(--core-color-brand-primary)]/10 text-[var(--core-color-brand-primary)]'
                          : 'border-transparent bg-[var(--core-color-surface-subtle)] group-hover:border-[var(--core-color-border-default)]'
                      )}>
                        <ItemIcon className="h-4 w-4" aria-hidden="true" />
                      </span>
                      <span className="flex flex-col">
                        {item.name}
                        {item.description && (
                          <span className="text-xs font-normal text-[var(--core-color-text-muted)] group-hover:text-[var(--core-color-text-primary)]/80">
                            {item.description}
                          </span>
                        )}
                      </span>
                    </Link>
                  )
                })}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-auto border-t border-[var(--core-color-border-default)] px-5 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--core-color-surface-subtle)] text-sm font-semibold text-[var(--core-color-brand-primary)]">
            {(user.full_name ?? user.username).charAt(0).toUpperCase()}
          </div>
          <div className="flex-1">
            <p className="text-sm font-semibold text-[var(--core-color-text-primary)]">{user.full_name ?? user.username}</p>
            <p className="text-xs text-[var(--core-color-text-muted)]">{user.email}</p>
          </div>
          <RoleBadge role={user.role} />
        </div>
        <button
          type="button"
          onClick={logout}
          className="mt-3 inline-flex w-full items-center justify-center rounded-lg border border-[var(--core-color-border-default)] bg-[var(--core-color-surface-subtle)] px-3 py-2 text-xs font-medium text-[var(--core-color-text-muted)] hover:border-[var(--core-color-border-focus)] hover:text-[var(--core-color-text-primary)]"
        >
          Sign out
        </button>
      </div>
    </nav>
  )
}
