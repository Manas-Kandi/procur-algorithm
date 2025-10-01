import { ReactNode } from 'react'
import { Card } from './Card'
import clsx from 'clsx'

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

export function MetricCard({ title, value, icon, trend, subtitle, onClick }: MetricCardProps) {
  return (
    <Card hover={!!onClick} onClick={onClick}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{value}</p>
          {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
          {trend && (
            <div className="mt-2 flex items-center">
              <span
                className={clsx('text-sm font-medium', {
                  'text-green-600': trend.direction === 'up',
                  'text-red-600': trend.direction === 'down',
                  'text-gray-600': trend.direction === 'neutral',
                })}
              >
                {trend.direction === 'up' && '↑'}
                {trend.direction === 'down' && '↓'}
                {trend.direction === 'neutral' && '→'}
                {' '}
                {Math.abs(trend.value)}%
              </span>
            </div>
          )}
        </div>
        {icon && <div className="ml-4 text-gray-400">{icon}</div>}
      </div>
    </Card>
  )
}
