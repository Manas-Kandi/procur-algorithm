import { ReactNode } from 'react'
import clsx from 'clsx'

interface CardProps {
  children: ReactNode
  className?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
  onClick?: () => void
}

export function Card({ children, className, padding = 'md', hover = false, onClick }: CardProps) {
  return (
    <div
      className={clsx(
        'bg-white rounded-lg border border-gray-200 shadow-sm',
        {
          'p-0': padding === 'none',
          'p-3': padding === 'sm',
          'p-4': padding === 'md',
          'p-6': padding === 'lg',
          'hover:shadow-md transition-shadow cursor-pointer': hover,
        },
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  )
}
