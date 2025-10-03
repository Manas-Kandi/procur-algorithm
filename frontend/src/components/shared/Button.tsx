import { type ButtonHTMLAttributes, type ReactNode } from 'react'
import clsx from 'clsx'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  loading?: boolean
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  disabled,
  className,
  ...props
}: ButtonProps) {
  return (
    <button
      className={clsx(
        'inline-flex items-center justify-center font-semibold transition-all duration-150',
        'focus:outline-none focus:ring-2 focus:ring-offset-2',
        'rounded-sm', // 2px border radius from design system
        {
          // Primary Button
          'bg-brand-primary text-text-inverse hover:bg-brand-hover active:bg-brand-active focus:ring-brand-primary':
            variant === 'primary',
          // Secondary/Outline Button
          'bg-surface-raised text-text-primary border border-border-medium hover:border-border-strong hover:bg-background-secondary focus:ring-brand-primary':
            variant === 'secondary' || variant === 'outline',
          // Ghost Button
          'bg-transparent text-text-secondary hover:bg-background-secondary hover:text-text-primary focus:ring-brand-primary':
            variant === 'ghost',
          // Danger Button
          'bg-danger text-text-inverse hover:bg-danger/90 focus:ring-danger':
            variant === 'danger',
          // Sizes from design system
          'px-3 py-1.5 text-xs': size === 'sm', // Small: 6px 12px
          'px-5 py-2.5 text-sm': size === 'md', // Medium: 10px 20px
          'px-6 py-3 text-base': size === 'lg', // Large: 12px 24px
          'w-full': fullWidth,
          'opacity-50 cursor-not-allowed pointer-events-none':
            disabled ?? loading,
        },
        className
      )}
      disabled={disabled ?? loading}
      {...props}
    >
      {loading ? (
        <>
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
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
          Loading...
        </>
      ) : (
        children
      )}
    </button>
  )
}
