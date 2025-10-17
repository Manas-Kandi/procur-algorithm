import { Box, Flex, Heading, HStack, Icon, SimpleGrid, Text } from '@chakra-ui/react'
import { DollarSign, CheckCircle2, ListChecks } from 'lucide-react'
import type { ReactNode } from 'react'
import { Sparkline } from './Sparkline'

export interface OverviewCardsProps {
  income?: number | null
  paid?: number | null
  active: ReactNode
  avatarName?: string
  variant?: 'card' | 'plain'
  incomeTrend?: number[]
  paidTrend?: number[]
  activeTrend?: number[]
}

function MetricCard({ icon: IconCmp, label, value, variant = 'card', trend }: { icon: any; label: string; value: ReactNode; variant?: 'card' | 'plain'; trend?: number[] }) {
  return (
    <Box
      px={variant === 'card' ? 5 : 0}
      py={variant === 'card' ? 5 : 0}
      layerStyle={variant === 'card' ? 'card' : undefined}
    >
      <HStack align="center" justify="space-between">
        <HStack align="center" gap={3}>
          <Box w={9} h={9} display="flex" alignItems="center" justifyContent="center" borderRadius="full" bg={variant === 'card' ? 'bg.subtle' : 'transparent'} borderWidth={variant === 'card' ? '1px' : '0'} borderColor="border">
            <Icon as={IconCmp} boxSize={4} color="fg.muted" />
          </Box>
          <Text fontSize="xs" color="fg.muted">{label}</Text>
        </HStack>
      </HStack>
      <Heading as="p" size="xl" mt={1} color="fg" lineHeight="shorter">{value}</Heading>
      {trend && trend.length > 1 ? (
        <Box mt={1}>
          <Sparkline data={trend} width={120} height={28} color="brand.emphasized" />
        </Box>
      ) : null}
    </Box>
  )
}

export function OverviewCards({ income, paid, active, avatarName, variant = 'card', incomeTrend, paidTrend, activeTrend }: OverviewCardsProps) {
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
      <SimpleGrid columns={{ base: 1, sm: 3 }} gap={variant === 'card' ? 6 : 4}>
        <MetricCard variant={variant} icon={DollarSign} label="Income" value={fmtCurrency(income)} trend={incomeTrend} />
        <MetricCard variant={variant} icon={CheckCircle2} label="Paid" value={fmtCurrency(paid)} trend={paidTrend} />
        <MetricCard variant={variant} icon={ListChecks} label="Active requests" value={active} trend={activeTrend} />
      </SimpleGrid>
    </>
  )
}
