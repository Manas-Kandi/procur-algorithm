import { type ReactNode } from 'react'
import { Tooltip as ChakraUITooltip } from '@/components/ui/tooltip'
import { Box, type BoxProps } from '@chakra-ui/react'

interface TooltipProps {
  content: ReactNode
  children: ReactNode
  className?: string
  wrapperProps?: BoxProps
}

export function Tooltip({ content, children, className, wrapperProps }: TooltipProps) {
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
      <Box as="span" className={className} {...wrapperProps}>
        {children}
      </Box>
    </ChakraUITooltip>
  )
}
