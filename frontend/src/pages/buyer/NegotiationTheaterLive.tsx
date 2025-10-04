import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  Box,
  Button,
  Grid,
  HStack,
  VStack,
  Text,
  Badge,
  useToast,
} from '@chakra-ui/react'
import { FiPlay, FiPause } from 'react-icons/fi'
import { api } from '../../services/api'
import { useNegotiationStream } from '../../hooks/useNegotiationStream'
import { LiveNegotiationFeed } from '../../components/buyer/negotiation/LiveNegotiationFeed'
import { OfferCard } from '../../components/buyer/negotiation/OfferCard'
import { SmartAlert } from '../../components/shared/SmartAlert'
import type { NegotiationSession } from '../../types'

export function NegotiationTheaterLive(): JSX.Element {
  const { requestId } = useParams<{ requestId: string }>()
  const toast = useToast()
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null)

  const { data: sessions, isLoading, refetch } = useQuery({
    queryKey: ['negotiations', requestId],
    queryFn: async () => {
      if (!requestId) return []
      return await api.getNegotiationsForRequest(requestId)
    },
    enabled: Boolean(requestId),
  })

  // WebSocket stream for active session
  const streamState = useNegotiationStream(activeSessionId)

  // Auto-negotiate mutation
  const autoNegotiateMutation = useMutation({
    mutationFn: async (sessionId: string) => {
      return await api.autoNegotiate(sessionId, 8)
    },
    onSuccess: () => {
      toast({
        title: 'Negotiation completed',
        description: 'The AI has finished negotiating with the vendor.',
        status: 'success',
        duration: 5000,
      })
      refetch()
    },
    onError: (error: any) => {
      toast({
        title: 'Negotiation failed',
        description: error.response?.data?.detail || 'Failed to complete negotiation',
        status: 'error',
        duration: 5000,
      })
    },
  })

  const handleStartNegotiation = (sessionId: string) => {
    setActiveSessionId(sessionId)
    streamState.clearEvents()
    autoNegotiateMutation.mutate(sessionId)
  }

  if (isLoading) {
    return (
      <div className="py-12 text-center text-sm text-[var(--core-color-text-muted)]">
        Loading negotiation insights…
      </div>
    )
  }

  if (!sessions || sessions.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-[var(--core-color-text-primary)]">
          Negotiation Theater
        </h1>
        <SmartAlert
          severity="info"
          title="No negotiations in progress"
          message="Launch AI sourcing to start negotiating with vendors."
        />
      </div>
    )
  }

  const activeSessions = sessions.filter(
    (session) => session.status === 'active'
  )
  const topSessions = activeSessions.slice(0, 3)

  const getStatus = (index: number): 'leading' | 'contender' | 'fallback' => {
    if (index === 0) return 'leading'
    if (index === 1) return 'contender'
    return 'fallback'
  }

  return (
    <VStack align="stretch" spacing={8}>
      {/* Header */}
      <Box>
        <Text fontSize="2xl" fontWeight="bold" color="var(--core-color-text-primary)">
          Negotiation Theater
        </Text>
        <Text fontSize="sm" color="var(--core-color-text-muted)">
          Watch your AI agent orchestrate offers in real-time. Intervene when needed.
        </Text>
      </Box>

      {/* Connection Status */}
      {activeSessionId && (
        <HStack
          p={3}
          bg="var(--core-color-surface-secondary)"
          borderRadius="md"
          border="1px solid"
          borderColor={streamState.connected ? 'var(--core-color-green-300)' : 'var(--core-color-border-subtle)'}
        >
          <Badge colorScheme={streamState.connected ? 'green' : 'gray'}>
            {streamState.connected ? 'Connected' : 'Disconnected'}
          </Badge>
          <Text fontSize="sm" color="var(--core-color-text-secondary)">
            {streamState.isNegotiating
              ? 'Negotiation in progress...'
              : 'Ready to negotiate'}
          </Text>
          {streamState.error && (
            <Text fontSize="sm" color="var(--core-color-red-500)">
              {streamState.error}
            </Text>
          )}
        </HStack>
      )}

      {/* Top Offers Section */}
      <Box>
        <Text fontSize="lg" fontWeight="semibold" color="var(--core-color-text-primary)" mb={2}>
          Current Best Offers
        </Text>
        <Text fontSize="sm" color="var(--core-color-text-muted)" mb={4}>
          AI ranks offers based on budget fit, feature coverage, and risk.
        </Text>
        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', xl: 'repeat(3, 1fr)' }} gap={4}>
          {topSessions.map((session, index) => (
            <Box key={session.session_id}>
              <OfferCard
                session={session}
                rank={index + 1}
                status={getStatus(index)}
              />
              <HStack mt={3} justify="center">
                <Button
                  size="sm"
                  leftIcon={streamState.isNegotiating && activeSessionId === session.session_id ? <FiPause /> : <FiPlay />}
                  colorScheme="blue"
                  isLoading={autoNegotiateMutation.isPending && activeSessionId === session.session_id}
                  isDisabled={streamState.isNegotiating && activeSessionId !== session.session_id}
                  onClick={() => handleStartNegotiation(session.session_id)}
                >
                  {activeSessionId === session.session_id
                    ? 'Negotiating...'
                    : 'Start Auto-Negotiate'}
                </Button>
              </HStack>
            </Box>
          ))}
        </Grid>
      </Box>

      {/* Live Negotiation Feed */}
      {activeSessionId && (
        <Box>
          <Text fontSize="lg" fontWeight="semibold" color="var(--core-color-text-primary)" mb={2}>
            Live Negotiation Feed
          </Text>
          <Text fontSize="sm" color="var(--core-color-text-muted)" mb={4}>
            Real-time stream of negotiation rounds with full reasoning transparency.
          </Text>
          <LiveNegotiationFeed
            events={streamState.events}
            vendorName={
              sessions.find((s) => s.session_id === activeSessionId)?.vendor_name || 'Unknown Vendor'
            }
          />
        </Box>
      )}

      {/* Static Feed for Other Sessions */}
      {!activeSessionId && (
        <Box>
          <Text fontSize="lg" fontWeight="semibold" color="var(--core-color-text-primary)" mb={2}>
            Negotiation History
          </Text>
          <Text fontSize="sm" color="var(--core-color-text-muted)" mb={4}>
            Start a negotiation above to see the live feed.
          </Text>
          <Grid templateColumns={{ base: '1fr', lg: 'repeat(2, 1fr)' }} gap={4}>
            {activeSessions.map((session: NegotiationSession) => (
              <Box
                key={session.session_id}
                p={4}
                bg="var(--core-color-surface-primary)"
                borderRadius="md"
                border="1px solid"
                borderColor="var(--core-color-border-subtle)"
              >
                <HStack justify="space-between" mb={2}>
                  <Text fontSize="sm" fontWeight="semibold" color="var(--core-color-text-primary)">
                    {session.vendor_name}
                  </Text>
                  <Badge colorScheme="gray" fontSize="xs">
                    {session.status}
                  </Badge>
                </HStack>
                <Text fontSize="xs" color="var(--core-color-text-muted)">
                  Click "Start Auto-Negotiate" above to see live negotiation
                </Text>
              </Box>
            ))}
          </Grid>
        </Box>
      )}
    </VStack>
  )
}
