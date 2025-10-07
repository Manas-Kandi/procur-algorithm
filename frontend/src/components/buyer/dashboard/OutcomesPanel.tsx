import { Box, Heading, Text, SimpleGrid, VStack, HStack } from '@chakra-ui/react'
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
    <Box
      borderWidth="1px"
      borderColor="var(--core-color-border-default)"
      borderRadius="lg"
      bg="var(--core-color-surface-canvas)"
      p={6}
    >
      <VStack align="stretch" gap={4}>
        <Box>
          <Heading size="md" color="var(--core-color-text-primary)">
            Outcomes & Savings
          </Heading>
          <Text fontSize="sm" color="var(--core-color-text-muted)" mt={1}>
            Key metrics from AI-driven procurement
          </Text>
        </Box>

        <SimpleGrid columns={{ base: 1, md: 2, xl: 4 }} gap={4}>
          {metrics.map((metric, index) => (
            <Box
              key={index}
              borderWidth="1px"
              borderColor="var(--core-color-border-subtle)"
              borderRadius="md"
              bg="var(--core-color-surface-subtle)"
              p={4}
              _hover={{
                borderColor: 'var(--core-color-border-default)',
                boxShadow: 'sm',
              }}
              transition="all 0.2s"
            >
              <HStack justify="space-between" mb={3}>
                <Box className={metric.color}>{metric.icon}</Box>
                {metric.trend && metric.trendValue && (
                  <Text
                    fontSize="xs"
                    fontWeight="medium"
                    color={
                      metric.trend === 'up'
                        ? 'var(--core-color-success)'
                        : metric.trend === 'down'
                        ? 'var(--core-color-danger)'
                        : 'var(--core-color-text-muted)'
                    }
                  >
                    {metric.trendValue}
                  </Text>
                )}
              </HStack>
              <VStack align="stretch" gap={1}>
                <Text
                  fontSize="2xl"
                  fontWeight="bold"
                  color="var(--core-color-text-primary)"
                >
                  {metric.value}
                </Text>
                <Text fontSize="xs" color="var(--core-color-text-muted)">
                  {metric.label}
                </Text>
              </VStack>
            </Box>
          ))}
        </SimpleGrid>

        {/* Quick summary */}
        {totalSavings > 0 && (
          <Box
            mt={2}
            p={3}
            borderRadius="md"
            bg="var(--core-color-ai-bg)"
            borderWidth="1px"
            borderColor="var(--core-color-ai-border)"
          >
            <HStack gap={2}>
              <Text fontSize="sm" fontWeight="medium" color="var(--core-color-ai-primary)">
                💡 AI Impact:
              </Text>
              <Text fontSize="sm" color="var(--core-color-text-muted)">
                Your agents have saved you an average of {avgSavingsPercent.toFixed(1)}% per contract
                {avgClosingTime > 0 && `, closing deals ${Math.round((30 - avgClosingTime) / 30 * 100)}% faster than industry average`}.
              </Text>
            </HStack>
          </Box>
        )}
      </VStack>
    </Box>
  )
}
