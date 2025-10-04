import { ReactNode } from 'react'
import { Box, Flex, Heading, type BoxProps } from '@chakra-ui/react'

interface SurfaceCardProps extends BoxProps {
  title?: string
  actions?: ReactNode
  children: ReactNode
  stickyHeader?: boolean
}

export function SurfaceCard({ title, actions, children, stickyHeader = false, ...rest }: SurfaceCardProps) {
  return (
    <Box
      borderWidth="1px"
      borderColor="border"
      bg="bg.panel"
      rounded="lg"
      shadow="sm"
      {...rest}
    >
      {(title || actions) && (
        <Flex align="center" justify="space-between" px={4} py={3} borderBottomWidth="1px" borderColor="border" position={stickyHeader ? 'sticky' : undefined} top={stickyHeader ? 0 : undefined} zIndex={stickyHeader ? 1 : undefined} bg={stickyHeader ? 'bg.panel' : undefined}>
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

