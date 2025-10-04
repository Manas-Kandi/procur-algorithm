import { Box, Heading, Text, Flex, type BoxProps } from '@chakra-ui/react'

interface StatCardProps extends BoxProps {
  label: string
  value: string | number
  accent?: string // Chakra bgGradient value
}

export function StatCard({ label, value, accent = 'linear(to-br, #0ea5e9, #8b5cf6)', ...rest }: StatCardProps) {
  return (
    <Box
      borderWidth="1px"
      borderColor="gray.200"
      bg="white"
      rounded="lg"
      overflow="hidden"
      _dark={{ bg: '#0F0F0F', borderColor: '#262626' }}
      shadow="sm"
      {...rest}
    >
      <Box h="2px" bgGradient={accent} />
      <Flex direction="column" px={4} py={4} gap={1}>
        <Text fontSize="xs" color="gray.600" _dark={{ color: '#A1A1AA' }}>
          {label}
        </Text>
        <Heading as="p" size="lg" color="gray.900" _dark={{ color: '#FAFAFA' }}>
          {value}
        </Heading>
      </Flex>
    </Box>
  )
}

export default StatCard
