import { Box, Text, VStack, HStack, Badge } from '@chakra-ui/react'
import { formatDistanceToNow } from 'date-fns'
import { ArrowRight, TrendingDown, TrendingUp } from 'lucide-react'

export interface NegotiationRound {
  round: number
  timestamp: string
  actor: 'buyer' | 'seller'
  price: number
  strategy?: string
  accepted?: boolean
  rationale?: string[]
}

interface NegotiationRoundsTimelineProps {
  rounds: NegotiationRound[]
}

export function NegotiationRoundsTimeline({
  rounds,
}: NegotiationRoundsTimelineProps): JSX.Element {
  if (rounds.length === 0) {
    return (
      <Box
        p={6}
        textAlign="center"
        borderWidth="1px"
        borderColor="var(--core-color-border-subtle)"
        borderRadius="md"
        bg="var(--core-color-surface-subtle)"
      >
        <Text fontSize="sm" color="var(--core-color-text-muted)">
          Waiting for first offer...
        </Text>
      </Box>
    )
  }

  return (
    <VStack align="stretch" gap={0}>
      {rounds.map((round, index) => {
        const isLast = index === rounds.length - 1
        const prevRound = index > 0 ? rounds[index - 1] : null
        const priceDiff = prevRound ? round.price - prevRound.price : 0
        const isBuyer = round.actor === 'buyer'

        return (
          <Box
            key={round.round}
            position="relative"
            pl={12}
            pb={isLast ? 0 : 6}
          >
            {/* Timeline line */}
            {!isLast && (
              <Box
                position="absolute"
                left="20px"
                top="32px"
                bottom="0"
                width="2px"
                bg="var(--core-color-border-subtle)"
              />
            )}

            {/* Round indicator */}
            <Box
              position="absolute"
              left="0"
              top="4px"
              w={10}
              h={10}
              borderRadius="full"
              bg={
                round.accepted
                  ? 'var(--core-color-success-bg)'
                  : isBuyer
                  ? 'var(--core-color-brand-bg)'
                  : 'var(--core-color-purple-100)'
              }
              borderWidth="2px"
              borderColor="var(--core-color-surface-canvas)"
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
              <Text
                fontSize="sm"
                fontWeight="bold"
                color={
                  round.accepted
                    ? 'var(--core-color-success)'
                    : isBuyer
                    ? 'var(--core-color-brand-primary)'
                    : 'var(--core-color-purple-600)'
                }
              >
                {round.round}
              </Text>
            </Box>

            {/* Content */}
            <Box
              p={4}
              borderWidth="1px"
              borderColor={
                round.accepted
                  ? 'var(--core-color-success-border)'
                  : 'var(--core-color-border-subtle)'
              }
              borderRadius="md"
              bg={
                round.accepted
                  ? 'var(--core-color-success-bg)'
                  : 'var(--core-color-surface-canvas)'
              }
            >
              <HStack justify="space-between" align="start" mb={2}>
                <VStack align="start" gap={1}>
                  <HStack gap={2}>
                    <Badge
                      fontSize="xs"
                      px={2}
                      py={0.5}
                      borderRadius="sm"
                      bg={
                        isBuyer
                          ? 'var(--core-color-brand-bg)'
                          : 'var(--core-color-purple-100)'
                      }
                      color={
                        isBuyer
                          ? 'var(--core-color-brand-primary)'
                          : 'var(--core-color-purple-600)'
                      }
                    >
                      {isBuyer ? 'Buyer Agent' : 'Seller Agent'}
                    </Badge>
                    {round.strategy && (
                      <Badge
                        fontSize="xs"
                        px={2}
                        py={0.5}
                        borderRadius="sm"
                        bg="var(--core-color-background-tertiary)"
                        color="var(--core-color-text-secondary)"
                      >
                        {round.strategy}
                      </Badge>
                    )}
                    {round.accepted && (
                      <Badge
                        fontSize="xs"
                        px={2}
                        py={0.5}
                        borderRadius="sm"
                        bg="var(--core-color-success)"
                        color="white"
                      >
                        Accepted
                      </Badge>
                    )}
                  </HStack>
                  <Text fontSize="xs" color="var(--core-color-text-tertiary)">
                    {formatDistanceToNow(new Date(round.timestamp), { addSuffix: true })}
                  </Text>
                </VStack>

                <HStack gap={2} align="center">
                  {prevRound && priceDiff !== 0 && (
                    <>
                      <Text fontSize="xs" color="var(--core-color-text-muted)">
                        {priceDiff > 0 ? '+' : ''}${Math.abs(priceDiff).toLocaleString()}
                      </Text>
                      {priceDiff > 0 ? (
                        <TrendingUp className="h-4 w-4 text-red-600" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-green-600" />
                      )}
                    </>
                  )}
                  <Text fontSize="lg" fontWeight="bold" color="var(--core-color-text-primary)">
                    ${round.price.toLocaleString()}
                  </Text>
                </HStack>
              </HStack>

              {round.rationale && round.rationale.length > 0 && (
                <VStack align="stretch" gap={1} mt={2}>
                  {round.rationale.slice(0, 2).map((reason, i) => (
                    <HStack key={i} gap={2}>
                      <ArrowRight className="h-3 w-3" style={{ color: 'var(--core-color-ai-primary)' }} />
                      <Text fontSize="sm" color="var(--core-color-text-muted)">
                        {reason}
                      </Text>
                    </HStack>
                  ))}
                </VStack>
              )}
            </Box>
          </Box>
        )
      })}
    </VStack>
  )
}
