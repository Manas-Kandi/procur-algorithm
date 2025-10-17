/**
 * Enhanced Metric Card Component
 * Displays key metrics with trend indicators and sparklines
 */

import React from 'react'
import clsx from 'clsx'
import { TrendingUp, TrendingDown, Minus, LucideIcon } from 'lucide-react'
import { Sparkline } from './Sparkline'

export interface MetricCardProps {
  title: string
  value: string | number
  change?: {
    value: number
    type: 'percentage' | 'absolute'
  }
  trend?: 'up' | 'down' | 'neutral'
  sparklineData?: number[]
  icon?: LucideIcon
  variant?: 'default' | 'success' | 'warning' | 'danger'
  size?: 'small' | 'medium' | 'large'
  loading?: boolean
}

export const EnhancedMetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  trend,
  sparklineData,
  icon: Icon,
  variant = 'default',
  size = 'medium',
  loading = false,
}) => {
  const getTrendIcon = () => {
    if (!trend) return null
    
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4" />
      case 'down':
        return <TrendingDown className="h-4 w-4" />
      case 'neutral':
        return <Minus className="h-4 w-4" />
    }
  }

  const getTrendColor = () => {
    if (!trend) return 'text-text-tertiary'
    
    switch (trend) {
      case 'up':
        return variant === 'danger' ? 'text-danger' : 'text-success'
      case 'down':
        return variant === 'danger' ? 'text-success' : 'text-danger'
      case 'neutral':
        return 'text-text-tertiary'
    }
  }

  const getVariantClasses = () => {
    switch (variant) {
      case 'success':
        return 'border-t-2 border-t-success'
      case 'warning':
        return 'border-t-2 border-t-warning'
      case 'danger':
        return 'border-t-2 border-t-danger'
      default:
        return ''
    }
  }

  const sizeClasses = {
    small: 'p-4',
    medium: 'p-6',
    large: 'p-8',
  }

  const valueSizeClasses = {
    small: 'text-2xl',
    medium: 'text-4xl',
    large: 'text-5xl',
  }

  if (loading) {
    return (
      <div className={clsx(
        'bg-surface-raised border border-border-subtle rounded-sm',
        sizeClasses[size],
        getVariantClasses()
      )}>
        <div className="animate-pulse">
          <div className="h-4 bg-background-tertiary rounded w-24 mb-3" />
          <div className="h-10 bg-background-tertiary rounded w-32 mb-2" />
          <div className="h-3 bg-background-tertiary rounded w-20" />
        </div>
      </div>
    )
  }

  return (
    <div className={clsx(
      'bg-surface-raised border border-border-subtle rounded-sm transition-all duration-150 hover:shadow-low',
      sizeClasses[size],
      getVariantClasses()
    )}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          {Icon && (
            <div className="p-2 bg-background-secondary rounded-sm">
              <Icon className="h-4 w-4 text-text-tertiary" />
            </div>
          )}
          <h3 className="text-sm font-medium text-text-secondary uppercase tracking-wider">
            {title}
          </h3>
        </div>
        {sparklineData && sparklineData.length > 0 && (
          <div className="w-20 h-8">
            <Sparkline
              data={sparklineData}
              color={
                variant === 'success' ? '#16A34A' :
                variant === 'warning' ? '#F59E0B' :
                variant === 'danger' ? '#DC2626' :
                '#2563EB'
              }
            />
          </div>
        )}
      </div>

      <div className="space-y-2">
        <div className={clsx(
          'font-bold text-text-primary leading-tight',
          valueSizeClasses[size]
        )}>
          {value}
        </div>

        {change && (
          <div className={clsx(
            'flex items-center gap-1.5 text-sm font-medium',
            getTrendColor()
          )}>
            {getTrendIcon()}
            <span>
              {change.value > 0 ? '+' : ''}
              {change.value}
              {change.type === 'percentage' ? '%' : ''}
            </span>
            <span className="text-text-tertiary font-normal">
              from last period
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

// ============================================================================
// Metric Card Grid Component
// ============================================================================

export interface MetricCardGridProps {
  children: React.ReactNode
  columns?: {
    mobile?: number
    tablet?: number
    desktop?: number
  }
}

export const MetricCardGrid: React.FC<MetricCardGridProps> = ({
  children,
  columns = { mobile: 1, tablet: 2, desktop: 4 },
}) => {
  return (
    <div className={clsx(
      'grid gap-6',
      `grid-cols-${columns.mobile || 1}`,
      `md:grid-cols-${columns.tablet || 2}`,
      `lg:grid-cols-${columns.desktop || 4}`
    )}>
      {children}
    </div>
  )
}

// ============================================================================
// Comparison Metric Card Component
// ============================================================================

export interface ComparisonMetricCardProps {
  title: string
  current: {
    label: string
    value: string | number
  }
  previous: {
    label: string
    value: string | number
  }
  change: {
    value: number
    type: 'percentage' | 'absolute'
  }
  trend: 'up' | 'down' | 'neutral'
}

export const ComparisonMetricCard: React.FC<ComparisonMetricCardProps> = ({
  title,
  current,
  previous,
  change,
  trend,
}) => {
  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-success bg-success-bg'
      case 'down':
        return 'text-danger bg-danger-bg'
      case 'neutral':
        return 'text-text-tertiary bg-background-tertiary'
    }
  }

  return (
    <div className="bg-surface-raised border border-border-subtle rounded-sm p-6">
      <h3 className="text-sm font-medium text-text-secondary uppercase tracking-wider mb-4">
        {title}
      </h3>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-text-tertiary mb-1">{current.label}</p>
          <p className="text-2xl font-bold text-text-primary">{current.value}</p>
        </div>
        <div>
          <p className="text-xs text-text-tertiary mb-1">{previous.label}</p>
          <p className="text-2xl font-bold text-text-secondary">{previous.value}</p>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-border-subtle">
        <div className={clsx(
          'inline-flex items-center gap-1.5 px-2 py-1 rounded-sm text-xs font-medium',
          getTrendColor()
        )}>
          {trend === 'up' && <TrendingUp className="h-3 w-3" />}
          {trend === 'down' && <TrendingDown className="h-3 w-3" />}
          {trend === 'neutral' && <Minus className="h-3 w-3" />}
          <span>
            {change.value > 0 ? '+' : ''}
            {change.value}
            {change.type === 'percentage' ? '%' : ''} change
          </span>
        </div>
      </div>
    </div>
  )
}
