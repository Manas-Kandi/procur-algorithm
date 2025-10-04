import { Box, Heading, Text, Flex, type BoxProps } from '@chakra-ui/react'

interface StatCardProps extends BoxProps {
  label: string
  value: string | number
  accent?: string // Chakra bgGradient value
}

export function StatCard({ label, value, accent = 'linear(to-br, #0ea5e9, #8b5cf6)', ...rest }: StatCardProps) {
  return (
    <Box
      layerStyle="card"
      overflow="hidden"
      {...rest}
    >
      <Box h="2px" bgGradient={accent} />
      <Flex direction="column" px={4} py={4} gap={1}>
        <Text fontSize="xs" color="fg.muted">
          {label}
        </Text>
        <Heading as="p" size="lg" color="fg">
          {value}
        </Heading>
      </Flex>
    </Box>
  )
}

export default StatCard
