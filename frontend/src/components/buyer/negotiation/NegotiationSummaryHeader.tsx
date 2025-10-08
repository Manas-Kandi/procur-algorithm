import { Box, Text, HStack, VStack, SimpleGrid, Badge } from '@chakra-ui/react'
import { DollarSign, Target, Clock, Shield, TrendingDown } from 'lucide-react'

interface NegotiationSummaryHeaderProps {
  requestName: string
  totalVendors: number
  activeNegotiations: number
  projectedSavings?: number
  timeShortened?: number
  complianceWins?: number
  bestOfferPrice?: number
  targetBudget?: number
}

export function NegotiationSummaryHeader({
  requestName,
  totalVendors,
  activeNegotiations,
  projectedSavings = 0,
  timeShortened = 0,
  complianceWins = 0,
  bestOfferPrice,
  targetBudget,
}: NegotiationSummaryHeaderProps): JSX.Element {
  const savingsPercent = targetBudget && bestOfferPrice
    ? ((targetBudget - bestOfferPrice) / targetBudget * 100)
    : 0

  return (
    <Box
      borderWidth="1px"
      borderColor="var(--core-color-border-default)"
      borderRadius="lg"
      bg="var(--core-color-surface-canvas)"
      p={6}
    >
      <VStack align="stretch" gap={5}>
        {/* Header */}
        <Box>
          <HStack justify="space-between" align="start">
            <VStack align="start" gap={1}>
              <Text fontSize="2xl" fontWeight="bold" color="var(--core-color-text-primary)">
                {requestName}
              </Text>
              <HStack gap={2}>
                <Badge
                  fontSize="sm"
                  px={3}
                  py={1}
                  borderRadius="md"
                  bg="var(--core-color-brand-bg)"
                  color="var(--core-color-brand-primary)"
                >
                  {activeNegotiations} Active Negotiations
                </Badge>
                <Badge
                  fontSize="sm"
                  px={3}
                  py={1}
                  borderRadius="md"
                  bg="var(--core-color-background-tertiary)"
                  color="var(--core-color-text-secondary)"
                >
                  {totalVendors} Vendors Contacted
                </Badge>
              </HStack>
            </VStack>

            {savingsPercent > 0 && (
              <Box textAlign="right">
                <Text fontSize="xs" color="var(--core-color-text-muted)" mb={1}>
                  Projected Savings
                </Text>
                <HStack gap={2} justify="flex-end">
                  <TrendingDown className="h-5 w-5 text-green-600" />
                  <Text fontSize="2xl" fontWeight="bold" color="var(--core-color-success)">
                    {savingsPercent.toFixed(1)}%
                  </Text>
                </HStack>
              </Box>
            )}
          </HStack>
        </Box>

        {/* Impact Metrics */}
        <SimpleGrid columns={{ base: 2, md: 4 }} gap={4}>
          {/* Projected Savings */}
          <Box
            p={4}
            borderRadius="md"
            bg="var(--core-color-success-bg)"
            borderWidth="1px"
            borderColor="var(--core-color-success-border)"
          >
            <HStack gap={3}>
              <Box
                p={2}
                borderRadius="md"
                bg="var(--core-color-success)"
                color="white"
              >
                <DollarSign className="h-5 w-5" />
              </Box>
              <VStack align="start" gap={0}>
                <Text fontSize="xs" color="var(--core-color-text-muted)">
                  Savings
                </Text>
                <Text fontSize="lg" fontWeight="bold" color="var(--core-color-text-primary)">
                  ${projectedSavings.toLocaleString()}
                </Text>
              </VStack>
            </HStack>
          </Box>

          {/* Time Shortened */}
          <Box
            p={4}
            borderRadius="md"
            bg="var(--core-color-brand-bg)"
            borderWidth="1px"
            borderColor="var(--core-color-brand-border)"
          >
            <HStack gap={3}>
              <Box
                p={2}
                borderRadius="md"
                bg="var(--core-color-brand-primary)"
                color="white"
              >
                <Clock className="h-5 w-5" />
              </Box>
              <VStack align="start" gap={0}>
                <Text fontSize="xs" color="var(--core-color-text-muted)">
                  Time Saved
                </Text>
                <Text fontSize="lg" fontWeight="bold" color="var(--core-color-text-primary)">
                  {timeShortened} days
                </Text>
              </VStack>
            </HStack>
          </Box>

          {/* Compliance Wins */}
          <Box
            p={4}
            borderRadius="md"
            bg="var(--core-color-purple-100)"
            borderWidth="1px"
            borderColor="var(--core-color-purple-300)"
          >
            <HStack gap={3}>
              <Box
                p={2}
                borderRadius="md"
                bg="var(--core-color-purple-600)"
                color="white"
              >
                <Shield className="h-5 w-5" />
              </Box>
              <VStack align="start" gap={0}>
                <Text fontSize="xs" color="var(--core-color-text-muted)">
                  Compliance
                </Text>
                <Text fontSize="lg" fontWeight="bold" color="var(--core-color-text-primary)">
                  {complianceWins} Met
                </Text>
              </VStack>
            </HStack>
          </Box>

          {/* Best Deal */}
          {bestOfferPrice && (
            <Box
              p={4}
              borderRadius="md"
              bg="var(--core-color-ai-bg)"
              borderWidth="1px"
              borderColor="var(--core-color-ai-border)"
            >
              <HStack gap={3}>
                <Box
                  p={2}
                  borderRadius="md"
                  bg="var(--core-color-ai-primary)"
                  color="white"
                >
                  <Target className="h-5 w-5" />
                </Box>
                <VStack align="start" gap={0}>
                  <Text fontSize="xs" color="var(--core-color-text-muted)">
                    Best Offer
                  </Text>
                  <Text fontSize="lg" fontWeight="bold" color="var(--core-color-text-primary)">
                    ${bestOfferPrice.toLocaleString()}
                  </Text>
                </VStack>
              </HStack>
            </Box>
          )}
        </SimpleGrid>

        {/* AI Insight */}
        <Box
          p={3}
          borderRadius="md"
          bg="var(--core-color-ai-bg)"
          borderWidth="1px"
          borderColor="var(--core-color-ai-border)"
        >
          <HStack gap={2}>
            <Text fontSize="sm" fontWeight="semibold" color="var(--core-color-ai-primary)">
              🤖 AI Insight:
            </Text>
            <Text fontSize="sm" color="var(--core-color-text-primary)">
              {activeNegotiations} vendors are actively negotiating. Best offer is{' '}
              {savingsPercent > 0 ? `${savingsPercent.toFixed(1)}% under budget` : 'within budget'} with{' '}
              {complianceWins} compliance requirements met.
            </Text>
          </HStack>
        </Box>
      </VStack>
    </Box>
  )
}
