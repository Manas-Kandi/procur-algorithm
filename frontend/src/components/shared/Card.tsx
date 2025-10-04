import { type ReactNode, type HTMLAttributes } from 'react'
import { Box } from '@chakra-ui/react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
}

export function Card({
  children,
  padding = 'md',
  hover = false,
  className,
  ...props
}: CardProps) {
  const paddingMap = padding === 'none' ? 0 : padding === 'sm' ? 4 : padding === 'lg' ? 8 : 6

  return (
    <Box
      bg="white"
      borderWidth="1px"
      borderColor="gray.200"
      rounded="0"
      p={paddingMap}
      transition="all 150ms"
      cursor={hover ? 'pointer' : undefined}
      _hover={hover ? { borderColor: 'gray.300', _dark: { borderColor: '#333333' } } : undefined}
      _dark={{ bg: '#0F0F0F', borderColor: '#262626' }}
      className={className}
      {...props}
    >
      {children}
    </Box>
  )
}
