import clsx from 'clsx'
import type { RequestStatus } from '../../types'

interface StatusBadgeProps {
  status: RequestStatus
  size?: 'sm' | 'md' | 'lg'
}

const statusConfig: Record<RequestStatus, { label: string; color: string }> = {
  draft: { label: 'Draft', color: 'bg-gray-100 text-gray-700' },
  intake: { label: 'Intake', color: 'bg-blue-100 text-blue-700' },
  sourcing: { label: 'Sourcing', color: 'bg-cyan-100 text-cyan-700' },
  negotiating: { label: 'Negotiating', color: 'bg-purple-100 text-purple-700' },
  approving: { label: 'Approving', color: 'bg-amber-100 text-amber-700' },
  contracted: { label: 'Contracted', color: 'bg-green-100 text-green-700' },
  provisioning: { label: 'Provisioning', color: 'bg-indigo-100 text-indigo-700' },
  completed: { label: 'Completed', color: 'bg-green-100 text-green-700' },
  cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-700' },
}

export function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const config = statusConfig[status]
  
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full font-medium',
        config.color,
        {
          'px-2 py-0.5 text-xs': size === 'sm',
          'px-2.5 py-1 text-sm': size === 'md',
          'px-3 py-1.5 text-base': size === 'lg',
        }
      )}
    >
      {config.label}
    </span>
  )
}
