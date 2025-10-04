import { useMemo } from 'react'
import { MessageSquare, MoreHorizontal } from 'lucide-react'
import { Box, Flex, Text, Icon } from '@chakra-ui/react'

type StageKey =
  | 'draft'
  | 'intake'
  | 'sourcing'
  | 'negotiating'
  | 'approving'
  | 'contracted'
  | 'provisioning'
  | 'completed'
  | 'cancelled'

interface ProgressTrackerCardProps {
  title: string
  vendor?: string
  stage: StageKey
  nextAction?: string
  preview?: string
  budget?: string
  isActive?: boolean
  onClick?: () => void
}

const STAGE_CONFIG: Record<StageKey, { label: string }> = {
  draft: { label: 'Draft' },
  intake: { label: 'Intake' },
  sourcing: { label: 'Sourcing vendors' },
  negotiating: { label: 'Agent negotiating' },
  approving: { label: 'Awaiting approval' },
  contracted: { label: 'Contracted' },
  provisioning: { label: 'Provisioning' },
  completed: { label: 'Completed' },
  cancelled: { label: 'Cancelled' },
}

export function ProgressTrackerCard({
  title,
  vendor,
  stage,
  nextAction,
  preview,
  budget,
  isActive = false,
  onClick,
}: ProgressTrackerCardProps) {
  const config = useMemo(() => {
    return STAGE_CONFIG[stage] ?? { label: 'In progress' }
  }, [stage])

  const borderColor = isActive ? 'teal.solid' : 'border'

  return (
    <Box
      as="button"
      onClick={onClick}
      w="full"
      textAlign="left"
      p={4}
      borderWidth="1px"
      borderColor={borderColor}
      bg="bg.panel"
      transition="transform 0.2s ease"
      _hover={{ transform: 'translateY(-2px)' }}
    >
      <Flex align="start" gap={3}>
        {/* Vendor avatar */}
        <Box
          mt="0.5"
          h="32px"
          w="32px"
          flexShrink={0}
          display="flex"
          alignItems="center"
          justifyContent="center"
          borderWidth="1px"
          borderColor="border"
          bg="bg.panel"
          fontSize="xs"
          fontWeight="semibold"
          color="fg"
        >
          {(vendor ?? title).charAt(0).toUpperCase()}
        </Box>

        {/* Content */}
        <Box minW={0} flex={1}>
          <Flex align="start" justify="space-between" gap={2}>
            <Box minW={0} flex={1}>
              <Text as="h3" truncate fontSize="sm" fontWeight="semibold" color="fg">
                {title}
              </Text>
              {vendor && (
                <Text mt={0.5} fontSize="xs" color="fg.muted">
                  {vendor}
                </Text>
              )}
            </Box>
          </Flex>

          {/* Status badge + summary */}
          <Flex mt={1} align="center" gap={2}>
            <Box
              as="span"
              display="inline-flex"
              alignItems="center"
              borderWidth="1px"
              borderColor="border"
              bg="bg.panel"
              px={2}
              py={0.5}
              fontSize="xs"
              fontWeight="medium"
              color="fg.muted"
            >
              {nextAction ?? config.label}
            </Box>
          </Flex>

          {/* Inline micro-progress squares (3 steps) */}
          <Flex mt={1} align="center" gap={1.5} aria-hidden="true">
            {(['sourcing', 'negotiating', 'approving'] as StageKey[]).map((s) => {
              const order = ['sourcing', 'negotiating', 'approving']
              const reached = order.indexOf(stage) >= order.indexOf(s)
              return (
                <Box
                  key={s}
                  h="8px"
                  w="8px"
                  borderWidth={reached ? 0 : '1px'}
                  borderColor="border"
                  bg={reached ? 'teal.solid' : 'transparent'}
                />
              )
            })}
          </Flex>

          {/* Negotiation preview (subtle bubble) */}
          {preview && (
            <Box mt={2} display="inline-flex" maxW="full" alignItems="center" bg="bg.subtle" px={2} py={1} fontSize="xs" color="fg.muted">
              <Text truncate>{preview}</Text>
            </Box>
          )}
        </Box>
      </Flex>

      {/* Single primary CTA + overflow */}
      <Flex mt={3} align="center" justify="space-between">
        <Box
          as="span"
          display="inline-flex"
          alignItems="center"
          px={3}
          py={1.5}
          fontSize="sm"
          fontWeight="medium"
          borderWidth="1px"
          borderColor="teal.solid"
          color="fg"
          _hover={{ bg: 'teal.subtle' }}
        >
          <Icon as={MessageSquare} boxSize={3.5} mr={2} />
          Open negotiation
        </Box>
        <Box
          as="span"
          display="inline-flex"
          alignItems="center"
          justifyContent="center"
          p={1.5}
          color="fg.muted"
          _hover={{ bg: 'bg.subtle' }}
          onClick={(e) => {
            e.stopPropagation()
            // Handle more options menu here
          }}
        >
          <Icon as={MoreHorizontal} boxSize={4} />
        </Box>
      </Flex>
    </Box>
  )
}
