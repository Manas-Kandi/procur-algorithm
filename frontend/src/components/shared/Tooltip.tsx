import { type ReactNode } from 'react'
import { Tooltip as ChakraUITooltip } from '@/components/ui/tooltip'

interface TooltipProps {
  content: ReactNode
  children: ReactNode
  className?: string
}

export function Tooltip({ content, children, className }: TooltipProps) {
  return (
    <ChakraUITooltip
      content={content}
      positioning={{ placement: 'right' }}
      contentProps={{
        bg: 'bg.panel',
        color: 'fg',
        borderWidth: '1px',
        borderColor: 'border',
        borderRadius: 'md',
      }}
    >
      <span className={className}>{children}</span>
    </ChakraUITooltip>
  )
}
