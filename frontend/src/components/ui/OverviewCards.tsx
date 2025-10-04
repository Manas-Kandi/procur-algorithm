import { Box, Flex, Heading, HStack, Icon, SimpleGrid, Text } from '@chakra-ui/react'
import { DollarSign, CheckCircle2, ListChecks } from 'lucide-react'
import type { ReactNode } from 'react'

export interface OverviewCardsProps {
  income?: number | null
  paid?: number | null
  active: ReactNode
  avatarName?: string
}

function MetricCard({ icon: IconCmp, label, value }: { icon: any; label: string; value: ReactNode }) {
  return (
    <Box layerStyle="card" px={5} py={5}>
      <HStack align="center" justify="space-between">
        <HStack align="center" gap={3}>
          <Box w={9} h={9} display="flex" alignItems="center" justifyContent="center" borderRadius="full" bg="bg.subtle" borderWidth="1px" borderColor="border">
            <Icon as={IconCmp} boxSize={4} color="fg.muted" />
          </Box>
          <Text fontSize="xs" color="fg.muted">{label}</Text>
        </HStack>
      </HStack>
      <Heading as="p" size="xl" mt={2} color="fg">{value}</Heading>
    </Box>
  )
}

export function OverviewCards({ income, paid, active, avatarName }: OverviewCardsProps) {
  const fmtCurrency = (n?: number | null) => (typeof n === 'number' ? `$${n.toLocaleString()}` : '—')
  const initial = (avatarName || 'You').trim().charAt(0).toUpperCase()

  return (
    <>
      <Flex align="center" justify="space-between" mb={3}>
        <Heading as="h2" size="sm" color="fg">Overview</Heading>
        <HStack gap={3}>
          <Box w={8} h={8} display="flex" alignItems="center" justifyContent="center" borderRadius="full" bg="bg.subtle" color="fg" borderWidth="1px" borderColor="border" fontSize="sm" fontWeight="semibold">
            {initial}
          </Box>
        </HStack>
      </Flex>
      <SimpleGrid columns={{ base: 1, sm: 3 }} gap={6}>
        <MetricCard icon={DollarSign} label="Income" value={fmtCurrency(income)} />
        <MetricCard icon={CheckCircle2} label="Paid" value={fmtCurrency(paid)} />
        <MetricCard icon={ListChecks} label="Active requests" value={active} />
      </SimpleGrid>
    </>
  )
}
