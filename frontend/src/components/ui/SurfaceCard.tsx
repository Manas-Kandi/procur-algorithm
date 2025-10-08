import { ReactNode } from 'react'
import { Box, Flex, Heading, type BoxProps } from '@chakra-ui/react'

type SurfaceVariant = 'elevated' | 'flat' | 'plain'

interface SurfaceCardProps extends BoxProps {
  title?: string
  actions?: ReactNode
  children: ReactNode
  stickyHeader?: boolean
  variant?: SurfaceVariant
}

export function SurfaceCard({ title, actions, children, stickyHeader = false, variant = 'elevated', ...rest }: SurfaceCardProps) {
  const stylesByVariant: Record<SurfaceVariant, { borderWidth?: string; shadow?: string; bg?: string }> = {
    elevated: { borderWidth: '1px', shadow: 'sm', bg: 'bg.panel' },
    flat: { borderWidth: '1px', shadow: 'none', bg: 'bg.panel' },
    plain: { borderWidth: '0', shadow: 'none', bg: 'transparent' },
  }
  const styles = stylesByVariant[variant]
  return (
    <Box
      borderWidth={styles.borderWidth}
      borderColor="border"
      bg={styles.bg}
      rounded="lg"
      shadow={styles.shadow}
      {...rest}
    >
      {(title || actions) && (
        <Flex align="center" justify="space-between" px={4} py={3} borderBottomWidth={variant === 'plain' ? '1px' : '1px'} borderColor="border" position={stickyHeader ? 'sticky' : undefined} top={stickyHeader ? 0 : undefined} zIndex={stickyHeader ? 1 : undefined} bg={stickyHeader ? (variant === 'plain' ? 'transparent' : 'bg.panel') : undefined}>
          {title && (
            <Heading as="h3" size="sm" color="fg">
              {title}
            </Heading>
          )}
          {actions}
        </Flex>
      )}
      <Box px={4} py={4}>
        {children}
      </Box>
    </Box>
  )
}

export default SurfaceCard

