import { Box, Text, VStack, HStack, Badge, Button } from '@chakra-ui/react'
import { Check, X, Clock, TrendingDown, AlertCircle, ChevronRight } from 'lucide-react'
import type { NegotiationSession } from '../../../types'

interface VendorOfferCardProps {
  session: NegotiationSession
  rank: number
  budgetMax?: number
  mustHaves?: string[]
  onClick?: () => void
  onAccept?: () => void
  onIntervene?: () => void
}

const STATUS_CONFIG = {
  waiting: { label: 'Waiting', color: 'gray', icon: Clock },
  negotiating: { label: 'Negotiating', color: 'blue', icon: TrendingDown },
  quoted: { label: 'Quoted', color: 'green', icon: Check },
  closed: { label: 'Closed', color: 'red', icon: X },
  active: { label: 'Active', color: 'purple', icon: Clock },
}

const RANK_CONFIG = {
  1: { label: 'Best Fit', color: 'green', bgColor: 'var(--core-color-success-bg)', borderColor: 'var(--core-color-success-border)' },
  2: { label: 'Strong Option', color: 'blue', bgColor: 'var(--core-color-brand-bg)', borderColor: 'var(--core-color-brand-border)' },
  3: { label: 'Alternative', color: 'yellow', bgColor: 'var(--core-color-warning-bg)', borderColor: 'var(--core-color-warning-border)' },
}

export function VendorOfferCard({
  session,
  rank,
  budgetMax,
  mustHaves = [],
  onClick,
  onAccept,
  onIntervene,
}: VendorOfferCardProps): JSX.Element {
  const statusConfig = STATUS_CONFIG[session.status as keyof typeof STATUS_CONFIG] || STATUS_CONFIG.waiting
  const rankConfig = RANK_CONFIG[rank as keyof typeof RANK_CONFIG] || RANK_CONFIG[3]
  const StatusIcon = statusConfig.icon

  const currentPrice = session.current_price || 0
  const budgetFit = budgetMax && currentPrice > 0
    ? Math.min(100, Math.max(0, ((budgetMax - currentPrice) / budgetMax) * 100))
    : 0

  const featureCoverage = (session.utility_score || 0) * 100
  const complianceScore = 85 // Mock - would come from backend

  const isOverBudget = budgetMax && currentPrice > budgetMax
  const isBestDeal = rank === 1

  // Mock compliance badges
  const complianceBadges = ['SOC 2', 'GDPR', 'HIPAA'].slice(0, Math.floor(Math.random() * 3) + 1)

  return (
    <Box
      borderWidth="2px"
      borderColor={isBestDeal ? rankConfig.borderColor : 'var(--core-color-border-default)'}
      borderRadius="lg"
      bg={isBestDeal ? rankConfig.bgColor : 'var(--core-color-surface-canvas)'}
      p={5}
      cursor={onClick ? 'pointer' : 'default'}
      onClick={onClick}
      _hover={onClick ? {
        borderColor: 'var(--core-color-brand-primary)',
        boxShadow: 'md',
      } : undefined}
      transition="all 0.2s"
      position="relative"
    >
      {/* Rank Badge */}
      <Box
        position="absolute"
        top={-3}
        right={4}
        px={3}
        py={1}
        borderRadius="full"
        bg={`var(--core-color-${rankConfig.color}-600)`}
        color="white"
        fontSize="xs"
        fontWeight="bold"
      >
        #{rank} {rankConfig.label}
      </Box>

      <VStack align="stretch" gap={4}>
        {/* Header */}
        <HStack justify="space-between" align="start" mt={2}>
          <VStack align="start" gap={1}>
            <Text fontSize="xl" fontWeight="bold" color="var(--core-color-text-primary)">
              {session.vendor_name || 'Unknown Vendor'}
            </Text>
            <HStack gap={2}>
              <Badge
                fontSize="xs"
                px={2}
                py={0.5}
                borderRadius="sm"
                bg={`var(--core-color-${statusConfig.color}-100)`}
                color={`var(--core-color-${statusConfig.color}-600)`}
              >
                <HStack gap={1}>
                  <StatusIcon className="h-3 w-3" />
                  <span>{statusConfig.label}</span>
                </HStack>
              </Badge>
              <Text fontSize="xs" color="var(--core-color-text-muted)">
                Round {session.current_round || 1}/{session.max_rounds || 8}
              </Text>
            </HStack>
          </VStack>
          {onClick && <ChevronRight className="h-5 w-5" style={{ color: 'var(--core-color-text-muted)' }} />}
        </HStack>

        {/* Price */}
        <Box>
          <HStack justify="space-between" mb={2}>
            <Text fontSize="sm" fontWeight="medium" color="var(--core-color-text-secondary)">
              Current Offer
            </Text>
            {isOverBudget && (
              <HStack gap={1}>
                <AlertCircle className="h-4 w-4 text-red-600" />
                <Text fontSize="xs" color="var(--core-color-danger)">
                  Over budget
                </Text>
              </HStack>
            )}
          </HStack>
          <HStack align="baseline" gap={2}>
            <Text fontSize="3xl" fontWeight="bold" color={isOverBudget ? 'var(--core-color-danger)' : 'var(--core-color-text-primary)'}>
              ${currentPrice.toLocaleString()}
            </Text>
            <Text fontSize="sm" color="var(--core-color-text-muted)">/month</Text>
          </HStack>
          {budgetMax && (
            <Box mt={2}>
              <HStack justify="space-between" mb={1}>
                <Text fontSize="xs" color="var(--core-color-text-muted)">Budget fit</Text>
                <Text fontSize="xs" fontWeight="medium" color="var(--core-color-text-primary)">
                  {budgetFit.toFixed(0)}%
                </Text>
              </HStack>
              <Box
                h="6px"
                bg="var(--core-color-background-tertiary)"
                borderRadius="full"
                overflow="hidden"
              >
                <Box
                  h="100%"
                  w={`${budgetFit}%`}
                  bg={budgetFit > 80 ? 'var(--core-color-success)' : budgetFit > 50 ? 'var(--core-color-warning)' : 'var(--core-color-error)'}
                  borderRadius="full"
                  transition="width 0.3s"
                />
              </Box>
            </Box>
          )}
        </Box>

        {/* Feature Coverage */}
        <Box>
          <HStack justify="space-between" mb={2}>
            <Text fontSize="sm" fontWeight="medium" color="var(--core-color-text-secondary)">
              Feature Match
            </Text>
            <Text fontSize="sm" fontWeight="semibold" color="var(--core-color-text-primary)">
              {featureCoverage.toFixed(0)}%
            </Text>
          </HStack>
          <Box
            h="6px"
            bg="var(--core-color-background-tertiary)"
            borderRadius="full"
            overflow="hidden"
          >
            <Box
              h="100%"
              w={`${featureCoverage}%`}
              bg={featureCoverage > 80 ? 'var(--core-color-success)' : featureCoverage > 60 ? 'var(--core-color-warning)' : 'var(--core-color-error)'}
              borderRadius="full"
              transition="width 0.3s"
            />
          </Box>
        </Box>

        {/* Compliance Badges */}
        <Box>
          <Text fontSize="sm" fontWeight="medium" color="var(--core-color-text-secondary)" mb={2}>
            Compliance
          </Text>
          <HStack gap={2} flexWrap="wrap">
            {complianceBadges.map((badge) => (
              <Badge
                key={badge}
                fontSize="xs"
                px={2}
                py={1}
                borderRadius="sm"
                bg="var(--core-color-purple-100)"
                color="var(--core-color-purple-600)"
              >
                <HStack gap={1}>
                  <Check className="h-3 w-3" />
                  <span>{badge}</span>
                </HStack>
              </Badge>
            ))}
            <Badge
              fontSize="xs"
              px={2}
              py={1}
              borderRadius="sm"
              bg="var(--core-color-background-tertiary)"
              color="var(--core-color-text-secondary)"
            >
              {complianceScore}% coverage
            </Badge>
          </HStack>
        </Box>

        {/* Timeline/Response Time */}
        <Box
          p={3}
          borderRadius="md"
          bg="var(--core-color-surface-subtle)"
          borderWidth="1px"
          borderColor="var(--core-color-border-subtle)"
        >
          <HStack gap={2}>
            <Clock className="h-4 w-4" style={{ color: 'var(--core-color-text-muted)' }} />
            <VStack align="start" gap={0}>
              <Text fontSize="xs" fontWeight="medium" color="var(--core-color-text-primary)">
                Next update expected
              </Text>
              <Text fontSize="xs" color="var(--core-color-text-muted)">
                {session.status === 'active' ? 'Within 2 hours' : 'Waiting for response'}
              </Text>
            </VStack>
          </HStack>
        </Box>

        {/* Action Buttons */}
        <HStack gap={2}>
          {onIntervene && (
            <Button
              size="sm"
              variant="outline"
              onClick={(e) => {
                e.stopPropagation()
                onIntervene()
              }}
              flex={1}
            >
              Intervene
            </Button>
          )}
          {onAccept && isBestDeal && (
            <Button
              size="sm"
              colorScheme="green"
              onClick={(e) => {
                e.stopPropagation()
                onAccept()
              }}
              flex={1}
            >
              Accept Offer
            </Button>
          )}
        </HStack>
      </VStack>
    </Box>
  )
}
