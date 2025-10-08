import { Box, Heading, Text, SimpleGrid, VStack, HStack, Icon } from '@chakra-ui/react'
import { TrendingUp, Clock, Shield, CheckCircle } from 'lucide-react'

interface OutcomeMetric {
  label: string
  value: string | number
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  icon: React.ReactNode
  color: string
}

interface OutcomesPanelProps {
  totalSavings?: number
  avgSavingsPercent?: number
  avgClosingTime?: number
  complianceCoverage?: number
  contractsApproved?: number
}

export function OutcomesPanel({
  totalSavings = 0,
  avgSavingsPercent = 0,
  avgClosingTime = 0,
  complianceCoverage = 0,
  contractsApproved = 0,
}: OutcomesPanelProps): JSX.Element {
  const metrics: OutcomeMetric[] = [
    {
      label: 'Total Savings Achieved',
      value: `$${totalSavings.toLocaleString()}`,
      trend: totalSavings > 0 ? 'up' : 'neutral',
      trendValue: avgSavingsPercent > 0 ? `${avgSavingsPercent.toFixed(1)}% avg` : undefined,
      icon: <TrendingUp className="h-5 w-5" />,
      color: 'text-green-600',
    },
    {
      label: 'Avg. Time to Close',
      value: avgClosingTime > 0 ? `${avgClosingTime} days` : 'N/A',
      trend: avgClosingTime > 0 && avgClosingTime < 30 ? 'up' : 'neutral',
      trendValue: avgClosingTime > 0 ? `${Math.round((30 - avgClosingTime) / 30 * 100)}% faster` : undefined,
      icon: <Clock className="h-5 w-5" />,
      color: 'text-blue-600',
    },
    {
      label: 'Compliance Coverage',
      value: `${complianceCoverage}%`,
      trend: complianceCoverage >= 90 ? 'up' : complianceCoverage >= 70 ? 'neutral' : 'down',
      trendValue: complianceCoverage >= 90 ? 'Excellent' : complianceCoverage >= 70 ? 'Good' : 'Needs attention',
      icon: <Shield className="h-5 w-5" />,
      color: 'text-purple-600',
    },
    {
      label: 'Contracts Approved',
      value: contractsApproved,
      trend: contractsApproved > 0 ? 'up' : 'neutral',
      icon: <CheckCircle className="h-5 w-5" />,
      color: 'text-teal-600',
    },
  ]

  return (
    <Box bg="bg.panel" borderWidth="0" borderRadius="lg" p={4}>
      <VStack align="stretch" gap={4}>
        <Box>
          <Heading size="md" color="fg">
            Outcomes & Savings
          </Heading>
          <Text fontSize="sm" color="fg.muted" mt={1}>
            Key metrics from AI-driven procurement
          </Text>
        </Box>

        <SimpleGrid columns={{ base: 1, md: 2, xl: 4 }} gap={4}>
          {metrics.map((metric, index) => (
            <HStack key={index} align="start" gap={3}>
              <Box w={8} h={8} borderRadius="full" bg="bg.subtle" display="flex" alignItems="center" justifyContent="center">
                <Icon as={(metric.icon as any).type ?? TrendingUp} color="fg.muted" boxSize={4} />
              </Box>
              <VStack align="start" gap={0}>
                <Text fontSize="2xl" fontWeight="bold" color="fg" lineHeight="short">
                  {metric.value}
                </Text>
                <HStack gap={2}>
                  <Text fontSize="xs" color="fg.muted">{metric.label}</Text>
                  {metric.trend && metric.trendValue && (
                    <Text fontSize="xs" color={metric.trend === 'up' ? 'green.fg' : metric.trend === 'down' ? 'red.fg' : 'fg.muted'}>
                      {metric.trendValue}
                    </Text>
                  )}
                </HStack>
              </VStack>
            </HStack>
          ))}
        </SimpleGrid>

        {totalSavings > 0 && (
          <Box mt={1} p={3} borderRadius="md" bg="blue.subtle">
            <HStack gap={2}>
              <Text fontSize="sm" fontWeight="medium" color="blue.fg">💡 AI Impact:</Text>
              <Text fontSize="sm" color="fg.muted">
                Your agents have saved an average of {avgSavingsPercent.toFixed(1)}% per contract
                {avgClosingTime > 0 && `, closing deals ${Math.round((30 - avgClosingTime) / 30 * 100)}% faster than industry average`}.
              </Text>
            </HStack>
          </Box>
        )}
      </VStack>
    </Box>
  )
}
