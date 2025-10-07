import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
  Divider,
  SimpleGrid,
  Progress,
} from '@chakra-ui/react'
import { Check, X, Info, TrendingUp, TrendingDown } from 'lucide-react'
import type { NegotiationSession } from '../../../types'

interface OfferDetailsPanelProps {
  session: NegotiationSession
  requestBudget?: { min?: number; max?: number }
  mustHaves?: string[]
  onClose?: () => void
}

export function OfferDetailsPanel({
  session,
  requestBudget,
  mustHaves = [],
}: OfferDetailsPanelProps): JSX.Element {
  // Calculate metrics
  const currentPrice = session.current_price || 0
  const budgetFit =
    requestBudget?.max && currentPrice > 0
      ? Math.max(0, Math.min(100, ((requestBudget.max - currentPrice) / requestBudget.max) * 100))
      : 0

  const featureCoverage = session.utility_score ? session.utility_score * 100 : 0

  // Mock compliance data (would come from backend)
  const complianceItems = [
    { name: 'SOC 2 Type II', met: true },
    { name: 'GDPR Compliant', met: true },
    { name: 'Data residency (US)', met: true },
    { name: 'SSO/SAML', met: false },
  ]

  const complianceMet = complianceItems.filter((item) => item.met).length
  const complianceTotal = complianceItems.length
  const compliancePercent = (complianceMet / complianceTotal) * 100

  // Mock negotiation history
  const rounds = session.rounds_completed || 0
  const messages = session.messages || []

  return (
    <Box
      w="full"
      maxW="4xl"
      mx="auto"
      borderWidth="1px"
      borderColor="var(--core-color-border-default)"
      borderRadius="lg"
      bg="var(--core-color-surface-canvas)"
      overflow="hidden"
    >
      {/* Header */}
      <Box
        p={6}
        bg="var(--core-color-surface-subtle)"
        borderBottomWidth="1px"
        borderColor="var(--core-color-border-default)"
      >
        <HStack justify="space-between" align="start">
          <VStack align="stretch" gap={1}>
            <Heading size="lg" color="var(--core-color-text-primary)">
              {session.vendor_name || 'Vendor Offer'}
            </Heading>
            <Text fontSize="sm" color="var(--core-color-text-muted)">
              Round {rounds} • {session.status}
            </Text>
          </VStack>
          <Badge
            fontSize="md"
            px={3}
            py={1.5}
            borderRadius="md"
            bg="var(--core-color-brand-bg)"
            color="var(--core-color-brand-primary)"
          >
            Rank #{session.utility_score && session.utility_score > 0.8 ? '1' : session.utility_score && session.utility_score > 0.6 ? '2' : '3'}
          </Badge>
        </HStack>
      </Box>

      {/* Content */}
      <Box p={6}>
        <VStack align="stretch" gap={6}>
          {/* Price & Budget Fit */}
          <Box>
            <HStack justify="space-between" mb={3}>
              <Text fontSize="sm" fontWeight="semibold" color="var(--core-color-text-primary)">
                Current Offer
              </Text>
              <HStack gap={2}>
                {currentPrice > 0 && requestBudget?.max && (
                  <>
                    {currentPrice < requestBudget.max ? (
                      <TrendingDown className="h-4 w-4 text-green-600" />
                    ) : (
                      <TrendingUp className="h-4 w-4 text-red-600" />
                    )}
                    <Text
                      fontSize="xs"
                      fontWeight="medium"
                      color={
                        currentPrice < requestBudget.max
                          ? 'var(--core-color-success)'
                          : 'var(--core-color-danger)'
                      }
                    >
                      {currentPrice < requestBudget.max
                        ? `$${(requestBudget.max - currentPrice).toLocaleString()} under budget`
                        : `$${(currentPrice - requestBudget.max).toLocaleString()} over budget`}
                    </Text>
                  </>
                )}
              </HStack>
            </HStack>
            <HStack align="baseline" gap={2}>
              <Text fontSize="3xl" fontWeight="bold" color="var(--core-color-text-primary)">
                ${currentPrice.toLocaleString()}
              </Text>
              <Text fontSize="sm" color="var(--core-color-text-muted)">
                / month
              </Text>
            </HStack>
            {requestBudget?.max && (
              <Box mt={3}>
                <HStack justify="space-between" mb={1}>
                  <Text fontSize="xs" color="var(--core-color-text-muted)">
                    Budget fit
                  </Text>
                  <Text fontSize="xs" fontWeight="medium" color="var(--core-color-text-primary)">
                    {budgetFit.toFixed(0)}%
                  </Text>
                </HStack>
                <Progress
                  value={budgetFit}
                  size="sm"
                  colorScheme={budgetFit > 80 ? 'green' : budgetFit > 50 ? 'yellow' : 'red'}
                  borderRadius="full"
                />
              </Box>
            )}
          </Box>

          <Divider borderColor="var(--core-color-border-subtle)" />

          {/* Feature Coverage */}
          <Box>
            <HStack justify="space-between" mb={3}>
              <Text fontSize="sm" fontWeight="semibold" color="var(--core-color-text-primary)">
                Feature Coverage
              </Text>
              <Text fontSize="xs" fontWeight="medium" color="var(--core-color-text-primary)">
                {featureCoverage.toFixed(0)}%
              </Text>
            </HStack>
            <Progress
              value={featureCoverage}
              size="sm"
              colorScheme={featureCoverage > 80 ? 'green' : featureCoverage > 50 ? 'yellow' : 'red'}
              borderRadius="full"
              mb={3}
            />
            <VStack align="stretch" gap={2}>
              {mustHaves.slice(0, 5).map((feature, index) => (
                <HStack key={index} gap={2}>
                  {index < 3 ? (
                    <Check className="h-4 w-4 text-green-600" />
                  ) : (
                    <X className="h-4 w-4 text-red-600" />
                  )}
                  <Text
                    fontSize="sm"
                    color={
                      index < 3
                        ? 'var(--core-color-text-primary)'
                        : 'var(--core-color-text-muted)'
                    }
                  >
                    {feature}
                  </Text>
                </HStack>
              ))}
            </VStack>
          </Box>

          <Divider borderColor="var(--core-color-border-subtle)" />

          {/* Compliance */}
          <Box>
            <HStack justify="space-between" mb={3}>
              <Text fontSize="sm" fontWeight="semibold" color="var(--core-color-text-primary)">
                Compliance & Security
              </Text>
              <Text fontSize="xs" fontWeight="medium" color="var(--core-color-text-primary)">
                {complianceMet}/{complianceTotal} met
              </Text>
            </HStack>
            <Progress
              value={compliancePercent}
              size="sm"
              colorScheme={compliancePercent >= 75 ? 'green' : 'yellow'}
              borderRadius="full"
              mb={3}
            />
            <SimpleGrid columns={2} gap={2}>
              {complianceItems.map((item, index) => (
                <HStack key={index} gap={2}>
                  {item.met ? (
                    <Check className="h-4 w-4 text-green-600" />
                  ) : (
                    <X className="h-4 w-4 text-red-600" />
                  )}
                  <Text
                    fontSize="sm"
                    color={
                      item.met
                        ? 'var(--core-color-text-primary)'
                        : 'var(--core-color-text-muted)'
                    }
                  >
                    {item.name}
                  </Text>
                </HStack>
              ))}
            </SimpleGrid>
          </Box>

          <Divider borderColor="var(--core-color-border-subtle)" />

          {/* Negotiation History */}
          <Box>
            <Text fontSize="sm" fontWeight="semibold" color="var(--core-color-text-primary)" mb={3}>
              Negotiation History ({rounds} rounds)
            </Text>
            <VStack align="stretch" gap={2}>
              {messages.slice(0, 3).map((message: any, index: number) => (
                <Box
                  key={index}
                  p={3}
                  borderRadius="md"
                  bg="var(--core-color-surface-subtle)"
                  borderWidth="1px"
                  borderColor="var(--core-color-border-subtle)"
                >
                  <HStack gap={2} mb={1}>
                    <Info className="h-3 w-3" style={{ color: 'var(--core-color-ai-primary)' }} />
                    <Text fontSize="xs" fontWeight="medium" color="var(--core-color-ai-primary)">
                      Round {index + 1}
                    </Text>
                  </HStack>
                  <Text fontSize="sm" color="var(--core-color-text-muted)">
                    {message.message || `${message.actor} ${message.strategy || 'made an offer'}`}
                  </Text>
                </Box>
              ))}
            </VStack>
          </Box>
        </VStack>
      </Box>
    </Box>
  )
}
