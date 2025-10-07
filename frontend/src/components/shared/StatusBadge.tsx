import clsx from 'clsx'
import type { RequestStatus } from '../../types'

interface StatusBadgeProps {
  status: RequestStatus
  size?: 'sm' | 'md' | 'lg'
  showIcon?: boolean
  variant?: 'default' | 'subtle'
}

const statusConfig: Record<
  RequestStatus,
  { label: string; color: string; icon: string; description: string }
> = {
  draft: {
    label: 'Draft',
    color: 'bg-background-tertiary text-text-secondary',
    icon: '📝',
    description: 'Request is being drafted',
  },
  intake: {
    label: 'Intake Complete',
    color: 'bg-info-bg text-info',
    icon: '✓',
    description: 'Requirements collected',
  },
  sourcing: {
    label: 'Sourcing',
    color: 'bg-info-bg text-info',
    icon: '🔍',
    description: 'Finding vendors',
  },
  negotiating: {
    label: 'Negotiating',
    color: 'bg-ai-bg text-ai-primary',
    icon: '🤝',
    description: 'AI negotiating with vendors',
  },
  approving: {
    label: 'Awaiting Approval',
    color: 'bg-warning-bg text-warning',
    icon: '⏳',
    description: 'Pending decision',
  },
  contracted: {
    label: 'Contracted',
    color: 'bg-success-bg text-success',
    icon: '✅',
    description: 'Contract signed',
  },
  provisioning: {
    label: 'Provisioning',
    color: 'bg-brand-primary/10 text-brand-primary',
    icon: '⚙️',
    description: 'Setting up service',
  },
  completed: {
    label: 'Completed',
    color: 'bg-success-bg text-success',
    icon: '🎉',
    description: 'Successfully delivered',
  },
  cancelled: {
    label: 'Cancelled',
    color: 'bg-danger-bg text-danger',
    icon: '❌',
    description: 'Request cancelled',
  },
}

export function StatusBadge({
  status,
  size = 'md',
  showIcon = false,
  variant = 'default',
}: StatusBadgeProps) {
  const config = statusConfig[status]

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 rounded-sm font-semibold uppercase tracking-wide',
        variant === 'default' ? config.color : 'bg-transparent border border-current',
        {
          'px-2 py-1 text-xs': size === 'sm',
          'px-2.5 py-1 text-xs': size === 'md',
          'px-3 py-1.5 text-xs': size === 'lg',
        }
      )}
      title={config.description}
    >
      {showIcon && <span className="not-uppercase">{config.icon}</span>}
      {config.label}
    </span>
  )
}
