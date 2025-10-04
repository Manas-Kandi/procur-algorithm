import { useEffect, useRef } from 'react'
import { Box, VStack, HStack, Text, Badge, Divider, Icon } from '@chakra-ui/react'
import { FiArrowRight, FiCheck, FiX, FiZap } from 'react-icons/fi'
import type { NegotiationEvent } from '../../../hooks/useNegotiationStream'

interface LiveNegotiationFeedProps {
  events: NegotiationEvent[]
  vendorName: string
}

export function LiveNegotiationFeed({
  events,
  vendorName,
}: LiveNegotiationFeedProps): JSX.Element {
  const endOfFeedRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    endOfFeedRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [events])

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'connected':
        return FiCheck
      case 'round_start':
        return FiZap
      case 'buyer_offer':
        return FiArrowRight
      case 'seller_counter':
        return FiArrowRight
      case 'completed':
        return FiCheck
      case 'error':
        return FiX
      default:
        return FiZap
    }
  }

  const getEventColor = (type: string) => {
    switch (type) {
      case 'connected':
        return 'green'
      case 'buyer_offer':
        return 'blue'
      case 'seller_counter':
        return 'purple'
      case 'completed':
        return 'green'
      case 'error':
        return 'red'
      default:
        return 'gray'
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(price)
  }

  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp)
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      })
    } catch {
      return timestamp
    }
  }

  return (
    <Box
      p={4}
      bg="var(--core-color-surface-primary)"
      borderRadius="md"
      border="1px solid"
      borderColor="var(--core-color-border-subtle)"
      maxH="600px"
      overflowY="auto"
    >
      <HStack justify="space-between" mb={4}>
        <Text fontSize="sm" fontWeight="semibold" color="var(--core-color-text-primary)">
          Live Feed: {vendorName}
        </Text>
        <Badge colorScheme="green" fontSize="xs">
          {events.length} events
        </Badge>
      </HStack>

      <VStack align="stretch" spacing={3}>
        {events.length === 0 && (
          <Text fontSize="sm" color="var(--core-color-text-muted)" textAlign="center" py={8}>
            Waiting for negotiation to start...
          </Text>
        )}

        {events.map((event, index) => {
          const EventIcon = getEventIcon(event.type)
          const color = getEventColor(event.type)

          return (
            <Box key={index}>
              <HStack align="start" spacing={3}>
                <Icon
                  as={EventIcon}
                  color={`var(--core-color-${color}-500)`}
                  mt={1}
                  flexShrink={0}
                />
                <VStack align="start" spacing={1} flex={1}>
                  <HStack justify="space-between" w="full">
                    <Badge colorScheme={color} fontSize="xs">
                      {event.type.replace('_', ' ')}
                    </Badge>
                    <Text fontSize="xs" color="var(--core-color-text-muted)">
                      {formatTime(event.timestamp)}
                    </Text>
                  </HStack>

                  {event.data.message && (
                    <Text fontSize="sm" color="var(--core-color-text-secondary)">
                      {event.data.message}
                    </Text>
                  )}

                  {event.data.round_number && (
                    <Text fontSize="xs" fontWeight="semibold" color="var(--core-color-text-primary)">
                      Round {event.data.round_number}
                      {event.data.actor && ` • ${event.data.actor}`}
                      {event.data.strategy && ` • Strategy: ${event.data.strategy}`}
                    </Text>
                  )}

                  {event.data.offer && (
                    <HStack
                      spacing={4}
                      p={2}
                      bg="var(--core-color-surface-secondary)"
                      borderRadius="sm"
                      w="full"
                    >
                      <VStack align="start" spacing={0}>
                        <Text fontSize="xs" color="var(--core-color-text-muted)">
                          Price
                        </Text>
                        <Text fontSize="sm" fontWeight="semibold" color="var(--core-color-text-primary)">
                          {formatPrice(event.data.offer.unit_price)}
                        </Text>
                      </VStack>
                      <VStack align="start" spacing={0}>
                        <Text fontSize="xs" color="var(--core-color-text-muted)">
                          Term
                        </Text>
                        <Text fontSize="sm" fontWeight="semibold" color="var(--core-color-text-primary)">
                          {event.data.offer.term_months} months
                        </Text>
                      </VStack>
                      {event.data.utility !== undefined && (
                        <VStack align="start" spacing={0}>
                          <Text fontSize="xs" color="var(--core-color-text-muted)">
                            Utility
                          </Text>
                          <Text fontSize="sm" fontWeight="semibold" color="var(--core-color-text-primary)">
                            {(event.data.utility * 100).toFixed(1)}%
                          </Text>
                        </VStack>
                      )}
                    </HStack>
                  )}

                  {event.data.rationale && event.data.rationale.length > 0 && (
                    <VStack align="start" spacing={1} pl={2} borderLeftWidth={2} borderColor={`var(--core-color-${color}-300)`}>
                      {event.data.rationale.map((reason, idx) => (
                        <Text key={idx} fontSize="xs" color="var(--core-color-text-muted)">
                          • {reason}
                        </Text>
                      ))}
                    </VStack>
                  )}
                </VStack>
              </HStack>

              {index < events.length - 1 && <Divider my={2} />}
            </Box>
          )
        })}

        <div ref={endOfFeedRef} />
      </VStack>
    </Box>
  )
}
