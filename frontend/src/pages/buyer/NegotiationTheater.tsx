import { useParams, Link as RouterLink } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Box, Heading, SimpleGrid, Text, VStack, Badge, HStack, Button } from '@chakra-ui/react'
import { FiPlay } from 'react-icons/fi'
import { api } from '../../services/api'
import { OfferCard } from '../../components/buyer/negotiation/OfferCard'
import { NegotiationFeedWrapper } from '../../components/buyer/negotiation/NegotiationFeedWrapper'
import { NegotiationControl } from '../../components/buyer/negotiation/NegotiationControl'
import { SmartAlert } from '../../components/shared/SmartAlert'
import { useEffect, useState, useMemo } from 'react'
import { toaster } from '@/components/ui/toaster'

export function NegotiationTheater(): JSX.Element {
  const { requestId } = useParams<{ requestId: string }>()
  const [activeStreams, setActiveStreams] = useState<Set<string>>(new Set())
  const [activeNegotiatingSession, setActiveNegotiatingSession] = useState<string | null>(null)
  

  const { data: sessions, isLoading, refetch } = useQuery({
    queryKey: ['negotiations', requestId],
    queryFn: async () => {
      if (!requestId) return []
      return await api.getNegotiationsForRequest(requestId)
    },
    enabled: Boolean(requestId),
  })

  // Auto-negotiate mutation
  const autoNegotiateMutation = useMutation({
    mutationFn: async (sessionId: string) => {
      return await api.autoNegotiate(sessionId, 8)
    },
    onSuccess: (data) => {
      console.log('Negotiation completed:', data)
      // Non-blocking toast feedback
      const outcome = data.outcome === 'agreement' ? 'Deal reached' : 'No agreement'
      const rounds = data.rounds_completed || 0
      toaster.create({
        title: 'Negotiation completed',
        description: `${outcome}. Rounds: ${rounds}. Status: ${data.status}.`,
        type: data.outcome === 'agreement' ? 'success' : 'info',
        duration: 5000,
        closable: true,
      })

      setActiveNegotiatingSession(null)
      refetch()
    },
    onError: (error: any) => {
      console.error('Negotiation failed:', error)
      toaster.create({
        title: 'Negotiation failed',
        description: error.response?.data?.detail || error.message,
        type: 'error',
        duration: 6000,
        closable: true,
      })
      setActiveNegotiatingSession(null)
    },
  })

  const handleStartNegotiation = (sessionId: string) => {
    setActiveNegotiatingSession(sessionId)
    autoNegotiateMutation.mutate(sessionId)
  }

  // Memoize active sessions to prevent infinite re-renders
  const activeSessions = useMemo(
    () => (sessions ?? []).filter((session) => session.status === 'active'),
    [sessions]
  )

  const topSessions = useMemo(
    () => activeSessions.slice(0, 3),
    [activeSessions]
  )

  // Auto-connect to WebSocket for all active sessions
  // This hook must be called BEFORE any conditional returns
  useEffect(() => {
    if (activeSessions.length > 0) {
      const sessionIds = activeSessions.map((s) => s.session_id)
      setActiveStreams(new Set(sessionIds))
    }
  }, [activeSessions])

  // Now it's safe to have conditional returns after all hooks
  if (isLoading) {
    return (
      <Box py={12} textAlign="center">
        <Text fontSize="sm" color="fg.muted">
          Loading negotiation insights…
        </Text>
      </Box>
    )
  }

  if (!sessions || sessions.length === 0) {
    return (
      <VStack gap={6} align="stretch">
        <Heading size="lg" color="fg">
          Negotiation theater
        </Heading>
        <SmartAlert
          severity="info"
          title="No negotiations in progress"
          message="Launch AI sourcing to start negotiating with vendors."
        />
        <RouterLink to="/requests/new">
          <Button colorPalette="blue" size="sm" width="fit-content">
            Create new request
          </Button>
        </RouterLink>
      </VStack>
    )
  }

  const getStatus = (index: number): 'leading' | 'contender' | 'fallback' => {
    if (index === 0) return 'leading'
    if (index === 1) return 'contender'
    return 'fallback'
  }

  return (
    <VStack gap={10} align="stretch">
      {/* Page header */}
      <Box>
        <Heading size="lg" color="fg">
          Negotiation theater
        </Heading>
        <Text mt={1} fontSize="sm" color="fg.muted">
          Watch your agent orchestrate offers in real-time. Intervene when needed.
        </Text>
      </Box>
      <Box as="hr" borderTopWidth="1px" borderColor="border" />

      {/* Current best offers */}
      <VStack gap={4} align="stretch">
        <Box>
          <Heading size="md" color="fg">
            Current best offers
          </Heading>
          <Text mt={1} fontSize="sm" color="fg.muted">
            AI ranks offers based on budget fit, feature coverage, and risk.
          </Text>
        </Box>
        <SimpleGrid columns={{ base: 1, md: 2, xl: 3 }} gap={4}>
          {topSessions.map((session, index) => (
            <OfferCard
              key={session.session_id}
              session={session}
              rank={index + 1}
              status={getStatus(index)}
              requestId={requestId}
              clickable={false}
              actions={
                <Button
                  colorPalette="blue"
                  size="sm"
                  width="full"
                  loading={autoNegotiateMutation.isPending && activeNegotiatingSession === session.session_id}
                  disabled={autoNegotiateMutation.isPending && activeNegotiatingSession !== session.session_id}
                  onClick={() => handleStartNegotiation(session.session_id)}
                >
                  <HStack gap={2}>
                    <FiPlay />
                    <span>
                      {activeNegotiatingSession === session.session_id
                        ? 'Negotiating...'
                        : 'Start Auto-Negotiate'}
                    </span>
                  </HStack>
                </Button>
              }
            />
          ))}
        </SimpleGrid>
      </VStack>

      {/* Live negotiation feed - only show when negotiating */}
      {activeNegotiatingSession && (
        <>
          <Box as="hr" borderTopWidth="1px" borderColor="border" />

          <VStack gap={4} align="stretch">
            <Box>
              <HStack justify="space-between">
                <Box>
                  <Heading size="md" color="fg">
                    Live negotiation feed
                  </Heading>
                  <Text mt={1} fontSize="sm" color="fg.muted">
                    Real-time AI negotiations with full transparency
                  </Text>
                </Box>
                <Badge colorPalette="green" fontSize="sm">
                  Live
                </Badge>
              </HStack>
            </Box>
            {activeSessions
              .filter(s => s.session_id === activeNegotiatingSession)
              .map((session) => (
                <NegotiationFeedWrapper key={session.session_id} session={session} />
              ))}
          </VStack>
        </>
      )}

      <Box as="hr" borderTopWidth="1px" borderColor="border" />

      {/* Control panel */}
      <VStack gap={3} align="stretch">
        <Heading size="md" color="fg">
          Control panel
        </Heading>
        <NegotiationControl
          onAdjustBudget={() => {
            console.log('adjust budget')
          }}
          onAddRequirement={() => {
            console.log('add requirement')
          }}
          onStop={() => {
            console.log('pause negotiations')
          }}
          onAcceptBest={() => {
            console.log('accept best offer')
          }}
        />
      </VStack>
    </VStack>
  )
}
