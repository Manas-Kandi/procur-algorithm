import clsx from 'clsx'
import type { UserRole } from '../../types'

interface RoleBadgeProps {
  role: UserRole
}

const ROLE_MAP: Record<UserRole, { label: string; className: string }> = {
  buyer: {
    label: 'Buyer',
    className:
      'bg-[rgba(15,118,110,0.12)] text-[var(--persona-color-buyer-accent)]',
  },
  seller: {
    label: 'Seller',
    className:
      'bg-[rgba(249,115,22,0.12)] text-[var(--persona-color-seller-accent)]',
  },
  approver: {
    label: 'Approver',
    className:
      'bg-[rgba(37,99,235,0.12)] text-[var(--core-color-brand-primary)]',
  },
  admin: {
    label: 'Admin',
    className: 'bg-[rgba(124,58,237,0.12)] text-[#7C3AED]',
  },
  auditor: {
    label: 'Auditor',
    className: 'bg-[rgba(14,165,233,0.12)] text-[var(--core-color-data-info)]',
  },
}

export function RoleBadge({ role }: RoleBadgeProps): JSX.Element {
  const config = ROLE_MAP[role]

  return (
    <span
      className={clsx(
        'inline-flex items-center justify-center rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide',
        config.className
      )}
    >
      {config.label}
    </span>
  )
}
