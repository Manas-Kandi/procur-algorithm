import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Box, Heading, SimpleGrid, Text, VStack } from '@chakra-ui/react'
import { api } from '../../services/api'
import { OfferCard } from '../../components/buyer/negotiation/OfferCard'
import { NegotiationFeed } from '../../components/buyer/negotiation/NegotiationFeed'
import { NegotiationControl } from '../../components/buyer/negotiation/NegotiationControl'
import { SmartAlert } from '../../components/shared/SmartAlert'
import type { NegotiationSession } from '../../types'

export function NegotiationTheater(): JSX.Element {
  const { requestId } = useParams<{ requestId: string }>()

  const { data: sessions, isLoading } = useQuery({
    queryKey: ['negotiations', requestId],
    queryFn: async () => {
      if (!requestId) return []
      return await api.getNegotiationsForRequest(requestId)
    },
    enabled: Boolean(requestId),
  })

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
            />
          ))}
        </SimpleGrid>
      </VStack>

      <Box as="hr" borderTopWidth="1px" borderColor="var(--core-color-border-default)" />

      {/* Live negotiation feed */}
      <VStack gap={4} align="stretch">
        <Box>
          <Heading size="md" color="var(--core-color-text-primary)">
            Live negotiation feed
          </Heading>
          <Text mt={1} fontSize="sm" color="var(--core-color-text-muted)">
            Reasoning transparency for every move across active vendors.
          </Text>
        </Box>
        <SimpleGrid columns={{ base: 1, lg: 2 }} gap={4}>
          {activeSessions.map((session: NegotiationSession) => (
            <NegotiationFeed key={session.session_id} session={session} />
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
