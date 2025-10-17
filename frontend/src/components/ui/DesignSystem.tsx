/**
 * Core Design System Components
 * Following ProcureAI Design System v1.0
 */

import React from 'react'
import clsx from 'clsx'
import { LucideIcon } from 'lucide-react'

// ============================================================================
// Button Component with all variants
// ============================================================================

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'small' | 'medium' | 'large'
  loading?: boolean
  icon?: LucideIcon
  iconPosition?: 'left' | 'right'
  fullWidth?: boolean
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'medium',
      loading = false,
      icon: Icon,
      iconPosition = 'left',
      fullWidth = false,
      className,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const baseClasses = 'inline-flex items-center justify-center font-semibold transition-all duration-150 border-radius-sm cursor-pointer'
    
    const variantClasses = {
      primary: 'bg-brand-primary text-text-inverse border-0 hover:bg-brand-hover active:bg-brand-active',
      secondary: 'bg-surface-raised text-text-primary border border-border-medium hover:border-border-strong hover:bg-background-secondary',
      ghost: 'bg-transparent text-text-secondary border-0 hover:bg-background-secondary hover:text-text-primary',
      danger: 'bg-danger text-text-inverse border-0 hover:bg-danger-dark active:bg-danger-darker',
    }

    const sizeClasses = {
      small: 'px-3 py-1.5 text-xs gap-1.5',
      medium: 'px-5 py-2.5 text-sm gap-2',
      large: 'px-6 py-3 text-base gap-2.5',
    }

    const isDisabled = disabled || loading

    return (
      <button
        ref={ref}
        className={clsx(
          baseClasses,
          variantClasses[variant],
          sizeClasses[size],
          fullWidth && 'w-full',
          isDisabled && 'opacity-50 cursor-not-allowed pointer-events-none',
          'rounded-sm', // 2px radius as per design system
          className
        )}
        disabled={isDisabled}
        {...props}
      >
        {loading ? (
          <Spinner size={size === 'small' ? 14 : size === 'large' ? 20 : 16} />
        ) : (
          <>
            {Icon && iconPosition === 'left' && <Icon className={clsx(
              size === 'small' ? 'h-3.5 w-3.5' : size === 'large' ? 'h-5 w-5' : 'h-4 w-4'
            )} />}
            {children}
            {Icon && iconPosition === 'right' && <Icon className={clsx(
              size === 'small' ? 'h-3.5 w-3.5' : size === 'large' ? 'h-5 w-5' : 'h-4 w-4'
            )} />}
          </>
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'

// ============================================================================
// Input Component with proper styling
// ============================================================================

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  helper?: string
  error?: string
  icon?: LucideIcon
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, helper, error, icon: Icon, className, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text-secondary mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          {Icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary">
              <Icon className="h-4 w-4" />
            </div>
          )}
          <input
            ref={ref}
            className={clsx(
              'w-full bg-surface-sunken border border-border-subtle rounded-sm',
              'px-3 py-2.5 text-sm text-text-primary',
              'transition-all duration-150',
              'hover:border-border-medium',
              'focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary/20',
              'placeholder:text-text-tertiary',
              Icon && 'pl-9',
              error && 'border-danger focus:border-danger focus:ring-danger/20',
              className
            )}
            {...props}
          />
        </div>
        {helper && !error && (
          <p className="mt-1 text-xs text-text-tertiary">{helper}</p>
        )}
        {error && (
          <p className="mt-1 text-xs text-danger">{error}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

// ============================================================================
// Card Component with hover effects
// ============================================================================

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hover?: boolean
  padding?: 'none' | 'small' | 'medium' | 'large'
  status?: 'success' | 'warning' | 'danger' | 'info'
}

export const Card: React.FC<CardProps> = ({
  hover = false,
  padding = 'medium',
  status,
  className,
  children,
  ...props
}) => {
  const paddingClasses = {
    none: '',
    small: 'p-4',
    medium: 'p-6',
    large: 'p-8',
  }

  return (
    <div
      className={clsx(
        'bg-surface-raised border border-border-subtle rounded-sm',
        paddingClasses[padding],
        hover && 'transition-all duration-150 cursor-pointer hover:border-border-medium',
        status && 'relative overflow-hidden',
        className
      )}
      {...props}
    >
      {status && (
        <div
          className={clsx(
            'absolute top-0 left-0 right-0 h-1',
            status === 'success' && 'bg-success',
            status === 'warning' && 'bg-warning',
            status === 'danger' && 'bg-danger',
            status === 'info' && 'bg-info'
          )}
        />
      )}
      {children}
    </div>
  )
}

// ============================================================================
// Badge Component for status indicators
// ============================================================================

export interface BadgeProps {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral'
  size?: 'small' | 'medium'
  children: React.ReactNode
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'neutral',
  size = 'medium',
  children,
}) => {
  const variantClasses = {
    success: 'bg-success-bg text-success',
    warning: 'bg-warning-bg text-warning',
    danger: 'bg-danger-bg text-danger',
    info: 'bg-info-bg text-info',
    neutral: 'bg-background-tertiary text-text-secondary',
  }

  const sizeClasses = {
    small: 'px-2 py-0.5 text-xs',
    medium: 'px-2.5 py-1 text-xs',
  }

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-sm font-semibold uppercase tracking-wider',
        variantClasses[variant],
        sizeClasses[size]
      )}
    >
      {children}
    </span>
  )
}

// ============================================================================
// Alert Component for notifications
// ============================================================================

export interface AlertProps {
  variant?: 'success' | 'warning' | 'danger' | 'info'
  title?: string
  icon?: LucideIcon
  children: React.ReactNode
  onClose?: () => void
}

export const Alert: React.FC<AlertProps> = ({
  variant = 'info',
  title,
  icon: Icon,
  children,
  onClose,
}) => {
  const variantClasses = {
    success: 'bg-success-bg border-success text-success',
    warning: 'bg-warning-bg border-warning text-warning',
    danger: 'bg-danger-bg border-danger text-danger',
    info: 'bg-info-bg border-info text-info',
  }

  return (
    <div
      className={clsx(
        'flex gap-3 p-4 border rounded-sm',
        variantClasses[variant]
      )}
    >
      {Icon && <Icon className="h-5 w-5 flex-shrink-0 mt-0.5" />}
      <div className="flex-1 min-w-0">
        {title && (
          <h3 className="font-semibold text-sm mb-1">{title}</h3>
        )}
        <div className="text-sm">{children}</div>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 hover:opacity-70 transition-opacity"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  )
}

// ============================================================================
// Spinner Component for loading states
// ============================================================================

export interface SpinnerProps {
  size?: number
  className?: string
}

export const Spinner: React.FC<SpinnerProps> = ({ size = 20, className }) => {
  return (
    <svg
      className={clsx('animate-spin', className)}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  )
}

// ============================================================================
// Progress Bar Component
// ============================================================================

export interface ProgressBarProps {
  value: number
  max?: number
  variant?: 'primary' | 'success' | 'warning' | 'danger'
  size?: 'small' | 'medium' | 'large'
  showLabel?: boolean
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  variant = 'primary',
  size = 'medium',
  showLabel = false,
}) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))

  const variantClasses = {
    primary: 'bg-brand-primary',
    success: 'bg-success',
    warning: 'bg-warning',
    danger: 'bg-danger',
  }

  const sizeClasses = {
    small: 'h-1',
    medium: 'h-2',
    large: 'h-3',
  }

  return (
    <div className="w-full">
      <div className={clsx(
        'w-full bg-background-tertiary rounded-sm overflow-hidden',
        sizeClasses[size]
      )}>
        <div
          className={clsx(
            'h-full transition-all duration-300 ease-out',
            variantClasses[variant]
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <p className="mt-1 text-xs text-text-tertiary">
          {percentage.toFixed(0)}%
        </p>
      )}
    </div>
  )
}

// ============================================================================
// Skeleton Loader Component
// ============================================================================

export interface SkeletonProps {
  width?: string | number
  height?: string | number
  className?: string
  variant?: 'text' | 'circular' | 'rectangular'
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width,
  height,
  className,
  variant = 'rectangular',
}) => {
  return (
    <div
      className={clsx(
        'bg-background-tertiary animate-pulse',
        variant === 'circular' && 'rounded-full',
        variant === 'rectangular' && 'rounded-sm',
        variant === 'text' && 'rounded-sm',
        className
      )}
      style={{
        width: width || (variant === 'text' ? '100%' : undefined),
        height: height || (variant === 'text' ? '1em' : undefined),
      }}
    />
  )
}

// ============================================================================
// Tabs Component
// ============================================================================

export interface TabsProps {
  value: string
  onChange: (value: string) => void
  children: React.ReactNode
}

export const Tabs: React.FC<TabsProps> = ({ value, onChange, children }) => {
  return (
    <div>
      <div className="flex border-b border-border-subtle">
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child) && child.type === Tab) {
            return React.cloneElement(child, {
              isActive: child.props.value === value,
              onClick: () => onChange(child.props.value),
            } as any)
          }
          return child
        })}
      </div>
    </div>
  )
}

export interface TabProps {
  value: string
  label: string
  isActive?: boolean
  onClick?: () => void
}

export const Tab: React.FC<TabProps> = ({ label, isActive, onClick }) => {
  return (
    <button
      className={clsx(
        'px-5 py-3 text-sm font-medium border-b-2 transition-all duration-150',
        isActive
          ? 'text-brand-primary border-brand-primary'
          : 'text-text-secondary border-transparent hover:text-text-primary'
      )}
      onClick={onClick}
    >
      {label}
    </button>
  )
}

// Import X icon for Alert close button
import { X } from 'lucide-react'
