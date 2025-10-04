import { useEffect, useRef } from 'react'
import { Box, VStack, HStack, Text, Avatar, Badge, Spinner } from '@chakra-ui/react'
import { FiUser, FiCpu } from 'react-icons/fi'
import type { NegotiationEvent } from '../../../hooks/useNegotiationStream'

interface NegotiationChatProps {
  events: NegotiationEvent[]
  vendorName: string
  isNegotiating: boolean
}

interface ChatMessage {
  id: string
  actor: 'buyer' | 'seller' | 'system'
  content: string
  timestamp: string
  metadata?: {
    price?: number
    term?: number
    strategy?: string
    utility?: number
  }
}

export function NegotiationChat({
  events,
  vendorName,
  isNegotiating,
}: NegotiationChatProps): JSX.Element {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [events])

  // Convert events to chat messages
  const messages: ChatMessage[] = events.flatMap((event, index) => {
    const msgs: ChatMessage[] = []

    switch (event.type) {
      case 'connected':
        msgs.push({
          id: `${index}-connected`,
          actor: 'system',
          content: `Connected to negotiation stream with ${vendorName}`,
          timestamp: event.timestamp,
        })
        break

      case 'negotiation_start':
        msgs.push({
          id: `${index}-start`,
          actor: 'system',
          content: `Starting AI negotiation with ${event.data.vendor_name || vendorName}`,
          timestamp: event.timestamp,
        })
        break

      case 'round_start':
        msgs.push({
          id: `${index}-round`,
          actor: 'system',
          content: `Round ${event.data.round_number || 'N/A'} begins`,
          timestamp: event.timestamp,
        })
        break

      case 'buyer_offer':
        msgs.push({
          id: `${index}-buyer`,
          actor: 'buyer',
          content: event.data.message || 'Made an offer',
          timestamp: event.timestamp,
          metadata: {
            price: event.data.offer?.unit_price,
            term: event.data.offer?.term_months,
            strategy: event.data.strategy,
            utility: event.data.utility,
          },
        })
        break

      case 'seller_counter':
        msgs.push({
          id: `${index}-seller`,
          actor: 'seller',
          content: event.data.message || 'Sent counteroffer',
          timestamp: event.timestamp,
          metadata: {
            price: event.data.offer?.unit_price,
            term: event.data.offer?.term_months,
            utility: event.data.utility,
          },
        })
        break

      case 'negotiation_complete':
      case 'completed':
        msgs.push({
          id: `${index}-complete`,
          actor: 'system',
          content: event.data.message || 'Negotiation completed',
          timestamp: event.timestamp,
        })
        break

      case 'error':
        msgs.push({
          id: `${index}-error`,
          actor: 'system',
          content: `Error: ${event.data.message || 'Unknown error'}`,
          timestamp: event.timestamp,
        })
        break

      default:
        if (event.data.message) {
          msgs.push({
            id: `${index}-default`,
            actor: 'system',
            content: event.data.message,
            timestamp: event.timestamp,
          })
        }
    }

    return msgs
  })

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

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(price)
  }

  const getActorColor = (actor: string) => {
    switch (actor) {
      case 'buyer':
        return 'var(--core-color-blue-500)'
      case 'seller':
        return 'var(--core-color-purple-500)'
      default:
        return 'var(--core-color-text-muted)'
    }
  }

  const getActorIcon = (actor: string) => {
    switch (actor) {
      case 'buyer':
        return FiCpu
      case 'seller':
        return FiUser
      default:
        return null
    }
  }

  return (
    <Box
      h="100%"
      display="flex"
      flexDirection="column"
      bg="var(--core-color-surface-primary)"
      borderRadius="md"
      border="1px solid"
      borderColor="var(--core-color-border-subtle)"
    >
      {/* Header */}
      <HStack
        p={4}
        borderBottom="1px solid"
        borderColor="var(--core-color-border-subtle)"
        justify="space-between"
      >
        <VStack align="start" spacing={0}>
          <Text fontSize="md" fontWeight="semibold" color="var(--core-color-text-primary)">
            {vendorName}
          </Text>
          <Text fontSize="xs" color="var(--core-color-text-muted)">
            AI Negotiation Chat
          </Text>
        </VStack>
        {isNegotiating && (
          <HStack spacing={2}>
            <Spinner size="sm" color="var(--core-color-blue-500)" />
            <Badge colorScheme="blue" fontSize="xs">
              Negotiating...
            </Badge>
          </HStack>
        )}
      </HStack>

      {/* Messages */}
      <VStack
        flex={1}
        align="stretch"
        spacing={0}
        overflowY="auto"
        p={4}
        sx={{
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'var(--core-color-surface-secondary)',
          },
          '&::-webkit-scrollbar-thumb': {
            background: 'var(--core-color-border-default)',
            borderRadius: '4px',
          },
        }}
      >
        {messages.length === 0 && (
          <Box textAlign="center" py={12}>
            <Text fontSize="sm" color="var(--core-color-text-muted)">
              Waiting for negotiation to start...
            </Text>
          </Box>
        )}

        {messages.map((message) => {
          const ActorIcon = getActorIcon(message.actor)
          const isSystem = message.actor === 'system'
          const isBuyer = message.actor === 'buyer'

          if (isSystem) {
            // System messages: centered, minimal
            return (
              <HStack key={message.id} justify="center" py={2}>
                <Text fontSize="xs" color="var(--core-color-text-muted)" fontStyle="italic">
                  {message.content}
                </Text>
                <Text fontSize="xs" color="var(--core-color-text-muted)" opacity={0.6}>
                  {formatTime(message.timestamp)}
                </Text>
              </HStack>
            )
          }

          // Buyer/Seller messages: chat bubble style
          return (
            <HStack
              key={message.id}
              align="start"
              spacing={3}
              justify={isBuyer ? 'flex-end' : 'flex-start'}
              py={2}
            >
              {!isBuyer && ActorIcon && (
                <Avatar
                  size="sm"
                  icon={<ActorIcon />}
                  bg={getActorColor(message.actor)}
                  color="white"
                />
              )}

              <VStack
                align={isBuyer ? 'end' : 'start'}
                spacing={1}
                maxW="70%"
              >
                <HStack spacing={2}>
                  <Text fontSize="xs" fontWeight="semibold" color={getActorColor(message.actor)}>
                    {message.actor === 'buyer' ? 'Your AI Agent' : vendorName}
                  </Text>
                  <Text fontSize="xs" color="var(--core-color-text-muted)">
                    {formatTime(message.timestamp)}
                  </Text>
                </HStack>

                <Box
                  px={3}
                  py={2}
                  borderRadius="lg"
                  bg={isBuyer ? 'var(--core-color-blue-50)' : 'var(--core-color-surface-secondary)'}
                  border="1px solid"
                  borderColor={isBuyer ? 'var(--core-color-blue-200)' : 'var(--core-color-border-default)'}
                >
                  <Text fontSize="sm" color="var(--core-color-text-primary)">
                    {message.content}
                  </Text>

                  {message.metadata && (
                    <VStack align="start" spacing={1} mt={2} pt={2} borderTopWidth="1px" borderColor="var(--core-color-border-subtle)">
                      {message.metadata.price && (
                        <HStack spacing={2} fontSize="xs">
                          <Text color="var(--core-color-text-muted)">Price:</Text>
                          <Text fontWeight="semibold" color="var(--core-color-text-primary)">
                            {formatPrice(message.metadata.price)}/unit
                          </Text>
                        </HStack>
                      )}
                      {message.metadata.term && (
                        <HStack spacing={2} fontSize="xs">
                          <Text color="var(--core-color-text-muted)">Term:</Text>
                          <Text fontWeight="semibold" color="var(--core-color-text-primary)">
                            {message.metadata.term} months
                          </Text>
                        </HStack>
                      )}
                      {message.metadata.strategy && (
                        <HStack spacing={2} fontSize="xs">
                          <Text color="var(--core-color-text-muted)">Strategy:</Text>
                          <Badge colorScheme="blue" fontSize="xs">
                            {message.metadata.strategy}
                          </Badge>
                        </HStack>
                      )}
                      {message.metadata.utility !== undefined && (
                        <HStack spacing={2} fontSize="xs">
                          <Text color="var(--core-color-text-muted)">Utility:</Text>
                          <Text fontWeight="semibold" color="var(--core-color-text-primary)">
                            {(message.metadata.utility * 100).toFixed(1)}%
                          </Text>
                        </HStack>
                      )}
                    </VStack>
                  )}
                </Box>
              </VStack>

              {isBuyer && ActorIcon && (
                <Avatar
                  size="sm"
                  icon={<ActorIcon />}
                  bg={getActorColor(message.actor)}
                  color="white"
                />
              )}
            </HStack>
          )
        })}

        <div ref={messagesEndRef} />
      </VStack>

      {/* Footer status */}
      <HStack
        p={3}
        borderTop="1px solid"
        borderColor="var(--core-color-border-subtle)"
        justify="space-between"
        fontSize="xs"
        color="var(--core-color-text-muted)"
      >
        <Text>{messages.length} messages</Text>
        {isNegotiating && <Text>AI is analyzing and responding...</Text>}
      </HStack>
    </Box>
  )
}
