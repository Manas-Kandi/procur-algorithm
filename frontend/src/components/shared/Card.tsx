import { ReactNode, HTMLAttributes } from 'react'
import clsx from 'clsx'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
}

export function Card({ children, padding = 'md', hover = false, className, ...props }: CardProps) {
  return (
    <div
      className={clsx(
        'bg-surface-raised border border-border-subtle rounded-sm', 
        {
          'p-0': padding === 'none',
          'p-4': padding === 'sm',      
          'p-6': padding === 'md',      
          'p-8': padding === 'lg',      
          'hover:border-border-medium transition-all duration-150 cursor-pointer': hover,
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
