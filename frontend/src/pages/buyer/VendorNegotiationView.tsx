import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Badge,
  SimpleGrid,
} from '@chakra-ui/react'
import { FiArrowLeft, FiCheck, FiX } from 'react-icons/fi'
import { api } from '../../services/api'
import { NegotiationChat } from '../../components/buyer/negotiation/NegotiationChat'
import { useNegotiationStream } from '../../hooks/useNegotiationStream'
import { SmartAlert } from '../../components/shared/SmartAlert'

export function VendorNegotiationView(): JSX.Element {
  const { requestId, sessionId } = useParams<{ requestId: string; sessionId: string }>()
  const navigate = useNavigate()

  // Fetch negotiation session details
  const { data: session, isLoading } = useQuery({
    queryKey: ['negotiation', sessionId],
    queryFn: async () => {
      if (!sessionId) return null
      const sessions = await api.getNegotiationsForRequest(requestId!)
      return sessions.find((s) => s.session_id === sessionId)
    },
    enabled: Boolean(sessionId && requestId),
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  // Connect to WebSocket for real-time updates
  const streamState = useNegotiationStream(sessionId || null)

  const handleBack = () => {
    navigate(`/negotiations/${requestId}`)
  }

  const handleApprove = async () => {
    if (!session?.best_offer) return
    try {
      // TODO: Implement approve offer API call
      console.log('Approve offer:', session.best_offer.offer_id)
    } catch (error) {
      console.error('Failed to approve offer:', error)
    }
  }

  const handleReject = async () => {
    if (!sessionId) return
    try {
      // TODO: Implement reject offer API call
      console.log('Reject session:', sessionId)
    } catch (error) {
      console.error('Failed to reject offer:', error)
    }
  }

  if (isLoading) {
    return (
      <Box py={12} textAlign="center">
        <Text fontSize="sm" color="var(--core-color-text-muted)">
          Loading negotiation details…
        </Text>
      </Box>
    )
  }

  if (!session) {
    return (
      <VStack gap={6} align="stretch">
        <SmartAlert
          severity="critical"
          title="Negotiation not found"
          message="The requested negotiation session could not be found."
        />
        <Button onClick={handleBack}>
          <HStack gap={2}>
            <FiArrowLeft />
            <span>Back to Theater</span>
          </HStack>
        </Button>
      </VStack>
    )
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price)
  }

  const isActive = session.status === 'active'
  const isCompleted = session.status === 'completed'
  const hasOffer = Boolean(session.best_offer)

  return (
    <VStack gap={6} align="stretch" h="calc(100vh - 100px)">
      {/* Header */}
      <HStack justify="space-between" align="start">
        <VStack align="start" gap={1}>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleBack}
            color="fg.muted"
          >
            <HStack gap={2}>
              <FiArrowLeft />
              <span>Back to Theater</span>
            </HStack>
          </Button>
          <Heading size="lg" color="var(--core-color-text-primary)">
            {session.vendor_name || 'Unknown Vendor'}
          </Heading>
          <HStack gap={2}>
            <Badge
              colorPalette={isActive ? 'blue' : isCompleted ? 'green' : 'gray'}
              fontSize="sm"
            >
              {session.status}
            </Badge>
            {streamState.connected && (
              <Badge colorPalette="green" fontSize="sm">
                Connected
              </Badge>
            )}
          </HStack>
        </VStack>

        {isCompleted && hasOffer && (
          <HStack gap={3}>
            <Button
              colorPalette="red"
              variant="outline"
              onClick={handleReject}
            >
              <HStack gap={2}>
                <FiX />
                <span>Reject</span>
              </HStack>
            </Button>
            <Button
              colorPalette="green"
              onClick={handleApprove}
            >
              <HStack gap={2}>
                <FiCheck />
                <span>Approve Offer</span>
              </HStack>
            </Button>
          </HStack>
        )}
      </HStack>

      <Box as="hr" borderTopWidth="1px" borderColor="border" />

      {/* Stats */}
      <SimpleGrid columns={{ base: 1, md: 4 }} gap={4}>
        <Box
          p={4}
          bg="bg.panel"
          borderRadius="md"
          border="1px solid"
          borderColor="border"
        >
          <Text fontSize="xs" color="var(--core-color-text-muted)" mb={1}>
            Current Price
          </Text>
          <Text fontSize="2xl" fontWeight="semibold" color="var(--core-color-text-primary)">
            {session.current_price ? formatPrice(session.current_price) : 'N/A'}
          </Text>
          <Text fontSize="xs" color="var(--core-color-text-muted)" mt={1}>
            per unit
          </Text>
        </Box>

        <Box
          p={4}
          bg="bg.panel"
          borderRadius="md"
          border="1px solid"
          borderColor="border"
        >
          <Text fontSize="xs" color="var(--core-color-text-muted)" mb={1}>
            Total Cost
          </Text>
          <Text fontSize="2xl" fontWeight="semibold" color="var(--core-color-text-primary)">
            {session.total_cost ? formatPrice(session.total_cost) : 'N/A'}
          </Text>
          <Text fontSize="xs" color="var(--core-color-text-muted)" mt={1}>
            TCO
          </Text>
        </Box>

        <Box
          p={4}
          bg="var(--core-color-surface-secondary)"
          borderRadius="md"
          border="1px solid"
          borderColor="var(--core-color-border-subtle)"
        >
          <Text fontSize="xs" color="var(--core-color-text-muted)" mb={1}>
            Utility Score
          </Text>
          <Text fontSize="2xl" fontWeight="semibold" color="var(--core-color-text-primary)">
            {session.utility_score
              ? `${(session.utility_score * 100).toFixed(1)}%`
              : 'N/A'}
          </Text>
          <Text fontSize="xs" color="var(--core-color-text-muted)" mt={1}>
            value score
          </Text>
        </Box>

        <Box
          p={4}
          bg="var(--core-color-surface-secondary)"
          borderRadius="md"
          border="1px solid"
          borderColor="var(--core-color-border-subtle)"
        >
          <Text fontSize="xs" color="var(--core-color-text-muted)" mb={1}>
            Rounds
          </Text>
          <Text fontSize="2xl" fontWeight="semibold" color="var(--core-color-text-primary)">
            {session.rounds_completed || 0}
          </Text>
          <Text fontSize="xs" color="var(--core-color-text-muted)" mt={1}>
            of {session.max_rounds || 8} max
          </Text>
        </Box>
      </SimpleGrid>

      {/* Chat View */}
      <Box flex={1} minH="0">
        <NegotiationChat
          events={streamState.events}
          vendorName={session.vendor_name || 'Unknown Vendor'}
          isNegotiating={streamState.isNegotiating}
        />
      </Box>

      {/* Error state */}
      {streamState.error && (
        <SmartAlert
          severity="critical"
          title="Connection Error"
          message={streamState.error}
        />
      )}
    </VStack>
  )
}
