import clsx from 'clsx'
import type { RequestStatus } from '../../types'

interface StatusBadgeProps {
  status: RequestStatus
  size?: 'sm' | 'md' | 'lg'
}

const statusConfig: Record<RequestStatus, { label: string; color: string }> = {
  draft: {
    label: 'Draft',
    color: 'bg-background-tertiary text-text-secondary',
  },
  intake: { label: 'Intake', color: 'bg-info-bg text-info' },
  sourcing: { label: 'Sourcing', color: 'bg-info-bg text-info' },
  negotiating: { label: 'Negotiating', color: 'bg-ai-bg text-ai-primary' },
  approving: { label: 'Approving', color: 'bg-warning-bg text-warning' },
  contracted: { label: 'Contracted', color: 'bg-success-bg text-success' },
  provisioning: {
    label: 'Provisioning',
    color: 'bg-brand-primary/10 text-brand-primary',
  },
  completed: { label: 'Completed', color: 'bg-success-bg text-success' },
  cancelled: { label: 'Cancelled', color: 'bg-danger-bg text-danger' },
}

export function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const config = statusConfig[status]

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-sm font-semibold uppercase tracking-wide',
        config.color,
        {
          'px-2 py-1 text-xs': size === 'sm',
          'px-2.5 py-1 text-xs': size === 'md',
          'px-3 py-1.5 text-xs': size === 'lg',
        }
      )}
    >
      {config.label}
    </span>
  )
}
