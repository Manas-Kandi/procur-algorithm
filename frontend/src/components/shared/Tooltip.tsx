import { ReactNode } from 'react'
import clsx from 'clsx'

interface TooltipProps {
  content: ReactNode
  children: ReactNode
  className?: string
}

// Minimal CSS-only tooltip using group hover
export function Tooltip({ content, children, className }: TooltipProps) {
  return (
    <div className={clsx('group relative inline-flex', className)}>
      {children}
      <div
        role="tooltip"
        className="pointer-events-none absolute left-full top-1/2 z-50 ml-2 hidden -translate-y-1/2 whitespace-nowrap rounded-sm border border-border-medium bg-surface-raised px-2 py-1 text-xs text-text-primary shadow-medium group-hover:block"
      >
        {content}
      </div>
    </div>
  )
}
