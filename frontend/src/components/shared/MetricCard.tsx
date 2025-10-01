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
      className="h-full"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs font-medium uppercase tracking-wide text-text-secondary">{title}</p>
          <p className="mt-2 text-4xl font-bold leading-tight text-text-primary">{value}</p>
          {subtitle && <p className="mt-2 text-sm font-medium text-text-secondary">{subtitle}</p>}
        </div>
        {icon && (
          <div className="ml-4 flex h-10 w-10 items-center justify-center rounded-sm bg-background-secondary text-brand-primary">
            {icon}
          </div>
        )}
      </div>
      {trend && (
        <div className="mt-2 inline-flex items-center gap-2 text-sm font-medium">
          <TrendIcon
            className={clsx('h-4 w-4', {
              'text-success': trend.direction === 'up',
              'text-danger': trend.direction === 'down',
              'text-text-tertiary': trend.direction === 'neutral',
            })}
            aria-hidden="true"
          />
          <span className={clsx({
            'text-success': trend.direction === 'up',
            'text-danger': trend.direction === 'down',
            'text-text-secondary': trend.direction === 'neutral',
          })}>{trend.value.toFixed(1)}%</span>
        </div>
      )}
    </Card>
  )
}
