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
        bg: 'gray.800',
        color: 'gray.100',
        borderWidth: '1px',
        borderColor: 'gray.700',
        borderRadius: '0',
        _dark: {
          bg: '#1A1A1A',
          color: '#FAFAFA',
          borderColor: '#333333',
        },
      }}
    >
      <span className={className}>{children}</span>
    </ChakraUITooltip>
  )
}
