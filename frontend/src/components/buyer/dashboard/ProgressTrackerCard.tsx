import { useMemo } from 'react'
import { MessageSquare, MoreHorizontal } from 'lucide-react'
import { Box, Flex, Text, Button, Icon, IconButton } from '@chakra-ui/react'

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

  const borderLight = isActive ? 'teal.400' : 'gray.200'
  const borderDark = isActive ? 'teal.300' : '#262626'

  return (
    <Box
      as="button"
      onClick={onClick}
      w="full"
      textAlign="left"
      p={4}
      borderWidth="1px"
      borderColor={borderLight}
      bg="white"
      transition="transform 0.2s ease"
      _hover={{ transform: 'translateY(-2px)' }}
      _dark={{ bg: '#0F0F0F', borderColor: borderDark }}
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
          borderColor="gray.200"
          bg="white"
          fontSize="xs"
          fontWeight="semibold"
          color="gray.900"
          _dark={{ borderColor: '#262626', bg: '#111', color: '#FAFAFA' }}
        >
          {(vendor ?? title).charAt(0).toUpperCase()}
        </Box>

        {/* Content */}
        <Box minW={0} flex={1}>
          <Flex align="start" justify="space-between" gap={2}>
            <Box minW={0} flex={1}>
              <Text as="h3" truncate fontSize="sm" fontWeight="semibold" color="gray.900" _dark={{ color: '#FAFAFA' }}>
                {title}
              </Text>
              {vendor && (
                <Text mt={0.5} fontSize="xs" color="gray.600" _dark={{ color: '#A1A1AA' }}>
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
              borderColor="gray.200"
              bg="white"
              px={2}
              py={0.5}
              fontSize="xs"
              fontWeight="medium"
              color="gray.700"
              _dark={{ borderColor: '#262626', bg: '#111', color: '#A1A1AA' }}
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
                  borderColor="gray.300"
                  bg={reached ? 'teal.400' : 'transparent'}
                  _dark={{ borderColor: '#262626', bg: reached ? 'teal.300' : 'transparent' }}
                />
              )
            })}
          </Flex>

          {/* Negotiation preview (subtle bubble) */}
          {preview && (
            <Box mt={2} display="inline-flex" maxW="full" alignItems="center" bg="gray.50" px={2} py={1} fontSize="xs" color="gray.700" _dark={{ bg: 'whiteAlpha.100', color: '#A1A1AA' }}>
              <Text truncate>{preview}</Text>
            </Box>
          )}
        </Box>
      </Flex>

      {/* Single primary CTA + overflow */}
      <Flex mt={3} align="center" justify="space-between">
        <Button
          onClick={onClick}
          size="sm"
          variant="outline"
          borderColor="teal.400"
          color="gray.900"
          _hover={{ bg: 'teal.50' }}
          _dark={{ color: '#FAFAFA', borderColor: 'teal.300', _hover: { bg: 'whiteAlpha.100' } }}
        >
          <Icon as={MessageSquare} boxSize={3.5} mr={2} />
          Open negotiation
        </Button>
        <IconButton aria-label="More options" size="sm" variant="ghost" color="gray.600" _dark={{ color: '#A1A1AA' }}>
          <Icon as={MoreHorizontal} boxSize={4} />
        </IconButton>
      </Flex>
    </Box>
  )
}
