import { type ReactNode } from 'react'
import { AlertTriangle, CheckCircle2, Info, OctagonAlert } from 'lucide-react'
import { Button } from './Button'

interface SmartAlertProps {
  title: string
  message: string
  emphasis?: string
  severity?: 'info' | 'success' | 'warning' | 'critical'
  actionLabel?: string
  onAction?: () => void
  footer?: ReactNode
  compact?: boolean
}

const SEVERITY_CONFIG = {
  info: {
    icon: Info,
    badgeClass: 'bg-info/10 text-info',
    borderClass: 'border-info/20',
    bgClass: 'bg-info-bg',
  },
  success: {
    icon: CheckCircle2,
    badgeClass: 'bg-success/10 text-success',
    borderClass: 'border-success/20',
    bgClass: 'bg-success-bg',
  },
  warning: {
    icon: AlertTriangle,
    badgeClass: 'bg-warning/10 text-warning',
    borderClass: 'border-warning/20',
    bgClass: 'bg-warning-bg',
  },
  critical: {
    icon: OctagonAlert,
    badgeClass: 'bg-danger/10 text-danger',
    borderClass: 'border-danger/20',
    bgClass: 'bg-danger-bg',
  },
} as const

export function SmartAlert({
  title,
  message,
  emphasis,
  severity = 'info',
  actionLabel,
  onAction,
  footer,
  compact = false,
}: SmartAlertProps): JSX.Element {
  const config = SEVERITY_CONFIG[severity]
  const Icon = config.icon

  return (
    <div
      className={`flex items-start gap-4 rounded-sm border ${config.borderClass} ${config.bgClass} px-4 py-4`}
    >
      <div
        className={`flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-sm ${config.badgeClass}`}
      >
        <Icon className="h-5 w-5" aria-hidden="true" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-text-primary">{title}</p>
            <p className="mt-1 text-sm text-text-secondary leading-relaxed">
              {message}{' '}
              {emphasis && (
                <span className="font-semibold text-text-primary">
                  {emphasis}
                </span>
              )}
            </p>
          </div>
          {actionLabel && (
            <Button
              size={compact ? 'sm' : 'md'}
              variant={severity === 'critical' ? 'danger' : 'outline'}
              onClick={onAction}
            >
              {actionLabel}
            </Button>
          )}
        </div>
        {footer && (
          <div className="mt-3 text-xs text-text-tertiary">{footer}</div>
        )}
      </div>
    </div>
  )
}
