import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Box, Heading, SimpleGrid, Text, VStack, Badge, HStack } from '@chakra-ui/react'
import { api } from '../../services/api'
import { OfferCard } from '../../components/buyer/negotiation/OfferCard'
import { NegotiationFeedWrapper } from '../../components/buyer/negotiation/NegotiationFeedWrapper'
import { NegotiationControl } from '../../components/buyer/negotiation/NegotiationControl'
import { SmartAlert } from '../../components/shared/SmartAlert'
import { useEffect, useState } from 'react'

export function NegotiationTheater(): JSX.Element {
  const { requestId } = useParams<{ requestId: string }>()
  const [activeStreams, setActiveStreams] = useState<Set<string>>(new Set())

  const { data: sessions, isLoading } = useQuery({
    queryKey: ['negotiations', requestId],
    queryFn: async () => {
      if (!requestId) return []
      return await api.getNegotiationsForRequest(requestId)
    },
    enabled: Boolean(requestId),
  })

  // Calculate active sessions (safe to do before early returns since it uses ?? for null safety)
  const activeSessions = (sessions ?? []).filter(
    (session) => session.status === 'active'
  )
  const topSessions = activeSessions.slice(0, 3)

  // Auto-connect to WebSocket for all active sessions
  // This hook must be called BEFORE any conditional returns
  useEffect(() => {
    if (activeSessions.length > 0) {
      activeSessions.forEach((session) => {
        setActiveStreams((prev) => new Set(prev).add(session.session_id))
      })
    }
  }, [activeSessions])

  // Now it's safe to have conditional returns after all hooks
  if (isLoading) {
    return (
      <Box py={12} textAlign="center">
        <Text fontSize="sm" color="var(--core-color-text-muted)">
          Loading negotiation insights…
        </Text>
      </Box>
    )
  }

  if (!sessions || sessions.length === 0) {
    return (
      <VStack gap={6} align="stretch">
        <Heading size="lg" color="var(--core-color-text-primary)">
          Negotiation theater
        </Heading>
        <SmartAlert
          severity="info"
          title="No negotiations in progress"
          message="Launch AI sourcing to start negotiating with vendors."
        />
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
        <Heading size="lg" color="var(--core-color-text-primary)">
          Negotiation theater
        </Heading>
        <Text mt={1} fontSize="sm" color="var(--core-color-text-muted)">
          Watch your agent orchestrate offers in real-time. Intervene when needed.
        </Text>
      </Box>

      <Box as="hr" borderTopWidth="1px" borderColor="var(--core-color-border-default)" />

      {/* Current best offers */}
      <VStack gap={4} align="stretch">
        <Box>
          <Heading size="md" color="var(--core-color-text-primary)">
            Current best offers
          </Heading>
          <Text mt={1} fontSize="sm" color="var(--core-color-text-muted)">
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
              clickable={true}
            />
          ))}
        </SimpleGrid>
      </VStack>

      <Box as="hr" borderTopWidth="1px" borderColor="var(--core-color-border-default)" />

      {/* Live negotiation feed with real-time WebSocket updates */}
      <VStack gap={4} align="stretch">
        <Box>
          <HStack justify="space-between">
            <Box>
              <Heading size="md" color="var(--core-color-text-primary)">
                Live negotiation feed
              </Heading>
              <Text mt={1} fontSize="sm" color="var(--core-color-text-muted)">
                Real-time AI negotiations with full transparency
              </Text>
            </Box>
            <Badge colorScheme="green" fontSize="sm">
              {activeSessions.length} active
            </Badge>
          </HStack>
        </Box>
        <SimpleGrid columns={{ base: 1, lg: 2 }} gap={4}>
          {activeSessions.map((session) => (
            <NegotiationFeedWrapper key={session.session_id} session={session} />
          ))}
        </SimpleGrid>
      </VStack>

      <Box as="hr" borderTopWidth="1px" borderColor="var(--core-color-border-default)" />

      {/* Control panel */}
      <VStack gap={3} align="stretch">
        <Heading size="md" color="var(--core-color-text-primary)">
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
