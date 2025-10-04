import { ReactNode } from 'react'
import { Box, Flex, Heading, type BoxProps } from '@chakra-ui/react'

interface SurfaceCardProps extends BoxProps {
  title?: string
  actions?: ReactNode
  children: ReactNode
}

export function SurfaceCard({ title, actions, children, ...rest }: SurfaceCardProps) {
  return (
    <Box
      borderWidth="1px"
      borderColor="gray.200"
      bg="white"
      rounded="lg"
      _dark={{ bg: '#0F0F0F', borderColor: '#262626' }}
      shadow="sm"
      {...rest}
    >
      {(title || actions) && (
        <Flex align="center" justify="space-between" px={4} py={3} borderBottomWidth="1px" borderColor="gray.200" _dark={{ borderColor: '#262626' }}>
          {title && (
            <Heading as="h3" size="sm" color="gray.900" _dark={{ color: '#FAFAFA' }}>
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
