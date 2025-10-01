import { useEffect, useState } from 'react'
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
  ChevronsLeft,
  ChevronsRight,
  LogOut,
} from 'lucide-react'
import { useAuthStore } from '../../store/auth'
import type { UserRole } from '../../types'
import { RoleBadge } from '../../ui/components/RoleBadge'
import { Tooltip } from '../shared/Tooltip'

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
    accent: 'bg-info',
    items: buyerNavItems,
  },
  seller: {
    label: 'Seller Workspace',
    accent: 'bg-warning',
    items: sellerNavItems,
  },
}

export function Navigation ({ variant = 'desktop', onNavigate }: NavigationProps): JSX.Element | null {
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const [collapsed, setCollapsed] = useState<boolean>(() => {
    try { return localStorage.getItem('nav_collapsed') === '1' } catch { return false }
  })
  useEffect(() => {
    try { localStorage.setItem('nav_collapsed', collapsed ? '1' : '0') } catch {}
  }, [collapsed])
  const toggleCollapsed = () => setCollapsed(prev => !prev)

  if (!user) return null

  const sections: Array<{ key: 'buyer' | 'seller'; label: string; accent: string; items: NavItem[] }> = []
  if (['buyer', 'approver', 'admin'].includes(user.role)) {
    sections.push({ key: 'buyer', ...SECTION_CONFIG.buyer })
  }
  if (['seller', 'admin'].includes(user.role)) {
    sections.push({ key: 'seller', ...SECTION_CONFIG.seller })
  }

  const containerClass = clsx(
    'flex flex-col bg-surface-raised transition-[width] duration-200 ease-in-out',
    collapsed ? 'w-16' : 'w-60',
    variant === 'desktop' && 'hidden h-screen overflow-hidden border-r border-border-subtle lg:flex',
    variant === 'mobile' && 'h-full shadow-medium'
  )

  return (
    <nav className={containerClass} aria-label="Primary navigation">
      <div className="flex items-center justify-between border-b border-border-subtle px-3 py-3">
        <Link to="/" className="inline-flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-sm bg-brand-primary text-text-inverse text-sm font-bold">
            P
          </div>
          {!collapsed && <span className="text-sm font-semibold text-text-primary">Procur</span>}
        </Link>
        <Tooltip content={collapsed ? 'Expand' : 'Collapse'}>
          <button
            type="button"
            onClick={toggleCollapsed}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            className="inline-flex h-8 w-8 items-center justify-center rounded-sm border border-border-medium bg-surface-raised text-text-secondary transition-all duration-150 hover:bg-background-secondary hover:text-text-primary"
          >
            {collapsed ? <ChevronsRight className="h-4 w-4" /> : <ChevronsLeft className="h-4 w-4" />}
          </button>
        </Tooltip>
      </div>
      <div className="flex-1 py-4">
        {sections.map((section) => (
          <div key={section.key} className="mb-8">
            {!collapsed && (
              <div className="flex items-center gap-2 px-6 text-xs font-semibold uppercase tracking-wide text-text-tertiary">
                <span className={clsx('h-1 w-1 rounded-full', section.accent)} aria-hidden="true" />
                {section.label}
              </div>
            )}
            <div className={clsx('mt-2 space-y-0.5', collapsed ? 'px-2' : 'px-3')}>
              {section.items
                .filter(item => item.roles.includes(user.role))
                .map((item) => {
                  const isRoot = item.href === '/'
                  const isActive = isRoot
                    ? location.pathname === '/'
                    : location.pathname.startsWith(item.href)
                  const ItemIcon = item.icon

                  const link = (
                    <Link
                      to={item.href}
                      onClick={onNavigate}
                      className={clsx(
                        'group flex items-center gap-3 rounded-sm px-3 py-2.5 text-sm font-medium transition-all duration-150',
                        collapsed && 'justify-center gap-0 px-2',
                        isActive
                          ? 'bg-brand-primary/10 text-brand-primary'
                          : 'text-text-secondary hover:bg-background-secondary hover:text-text-primary'
                      )}
                    >
                      <span className={clsx(
                        'flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-sm transition-colors',
                        isActive
                          ? 'bg-brand-primary/10 text-brand-primary'
                          : 'bg-background-secondary text-text-tertiary group-hover:text-text-secondary'
                      )}>
                        <ItemIcon className="h-4 w-4" aria-hidden="true" />
                      </span>
                      {!collapsed && (
                        <span className="flex flex-col">
                          {item.name}
                        </span>
                      )}
                    </Link>
                  )

                  return collapsed ? (
                    <Tooltip key={item.href} content={item.name}>{link}</Tooltip>
                  ) : (
                    <span key={item.href}>{link}</span>
                  )
                })}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-auto border-t border-border-subtle px-4 py-4">
        <div className={clsx('flex items-center gap-3', collapsed && 'justify-center') }>
          <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-sm bg-background-secondary text-sm font-semibold text-brand-primary">
            {(user.full_name ?? user.username).charAt(0).toUpperCase()}
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-text-primary truncate">{user.full_name ?? user.username}</p>
              <p className="text-xs text-text-tertiary truncate">{user.email}</p>
            </div>
          )}
          {!collapsed && <RoleBadge role={user.role} />}
        </div>
        {!collapsed ? (
          <button
            type="button"
            onClick={logout}
            className="mt-3 inline-flex w-full items-center justify-center rounded-sm border border-border-medium bg-surface-raised px-3 py-2 text-xs font-medium text-text-secondary transition-all duration-150 hover:border-border-strong hover:bg-background-secondary hover:text-text-primary"
          >
            Sign out
          </button>
        ) : (
          <div className="mt-3 flex justify-center">
            <Tooltip content="Sign out">
              <button
                type="button"
                onClick={logout}
                aria-label="Sign out"
                className="inline-flex h-8 w-8 items-center justify-center rounded-sm border border-border-medium bg-surface-raised text-text-secondary transition-all duration-150 hover:border-border-strong hover:bg-background-secondary hover:text-text-primary"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </Tooltip>
          </div>
        )}
      </div>
    </nav>
  )
}
