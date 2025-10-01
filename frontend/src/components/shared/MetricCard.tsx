import { ReactNode } from 'react'
import { TrendingDown, TrendingUp, Minus } from 'lucide-react'
import clsx from 'clsx'
import { Card } from './Card'

interface MetricCardProps {
  title: string
  value: string | number
  icon?: ReactNode
  trend?: {
    value: number
    direction: 'up' | 'down' | 'neutral'
  }
  subtitle?: string
  onClick?: () => void
}

export function MetricCard ({ title, value, icon, trend, subtitle, onClick }: MetricCardProps): JSX.Element {
  const TrendIcon = trend?.direction === 'up' ? TrendingUp : trend?.direction === 'down' ? TrendingDown : Minus

  return (
    <Card
      hover={!!onClick}
      onClick={onClick}
      className="h-full border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)]"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-[var(--core-color-text-muted)]">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-[var(--core-color-text-primary)]">{value}</p>
          {subtitle && <p className="mt-1 text-xs text-[var(--core-color-text-muted)]">{subtitle}</p>}
        </div>
        {icon && (
          <div className="ml-4 flex h-10 w-10 items-center justify-center rounded-md bg-[var(--core-color-surface-subtle)] text-[var(--core-color-brand-primary)]">
            {icon}
          </div>
        )}
      </div>
      {trend && (
        <div className="mt-4 inline-flex items-center gap-2 rounded-full bg-[var(--core-color-surface-subtle)] px-3 py-1 text-xs font-semibold text-[var(--core-color-text-muted)]">
          <TrendIcon
            className={clsx('h-3.5 w-3.5', {
              'text-[var(--core-color-data-positive)]': trend.direction === 'up',
              'text-[var(--core-color-data-critical)]': trend.direction === 'down',
              'text-[var(--core-color-text-muted)]': trend.direction === 'neutral',
            })}
            aria-hidden="true"
          />
          <span>{trend.value.toFixed(1)}%</span>
          <span className="font-normal">vs market</span>
        </div>
      )}
    </Card>
  )
}
