import { ReactNode } from 'react'
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
    badgeClass: 'bg-[rgba(14,165,233,0.12)] text-[var(--core-color-data-info)]',
    iconClass: 'text-[var(--core-color-data-info)]',
  },
  success: {
    icon: CheckCircle2,
    badgeClass: 'bg-[rgba(22,163,74,0.12)] text-[var(--core-color-data-positive)]',
    iconClass: 'text-[var(--core-color-data-positive)]',
  },
  warning: {
    icon: AlertTriangle,
    badgeClass: 'bg-[rgba(245,158,11,0.12)] text-[var(--core-color-data-warning)]',
    iconClass: 'text-[var(--core-color-data-warning)]',
  },
  critical: {
    icon: OctagonAlert,
    badgeClass: 'bg-[rgba(220,38,38,0.12)] text-[var(--core-color-data-critical)]',
    iconClass: 'text-[var(--core-color-data-critical)]',
  },
} as const

export function SmartAlert ({
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
    <div className="flex items-start gap-4 rounded-xl border border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)] px-5 py-4 shadow-100">
      <div className={`flex h-10 w-10 items-center justify-center rounded-full ${config.badgeClass}`}>
        <Icon className={`h-5 w-5 ${config.iconClass}`} aria-hidden="true" />
      </div>
      <div className="flex-1">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-sm font-semibold text-[var(--core-color-text-primary)]">{title}</p>
            <p className="mt-1 text-sm text-[var(--core-color-text-muted)]">
              {message}{' '}
              {emphasis && <span className="font-semibold text-[var(--core-color-text-primary)]">{emphasis}</span>}
            </p>
          </div>
          {actionLabel && (
            <Button size={compact ? 'sm' : 'md'} variant={severity === 'critical' ? 'danger' : 'outline'} onClick={onAction}>
              {actionLabel}
            </Button>
          )}
        </div>
        {footer && <div className="mt-3 text-xs text-[var(--core-color-text-muted)]">{footer}</div>}
      </div>
    </div>
  )
}
