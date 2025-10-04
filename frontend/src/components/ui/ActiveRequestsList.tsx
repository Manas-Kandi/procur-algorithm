import { Box, Flex, Icon, Text } from '@chakra-ui/react'
import { ChevronRight } from 'lucide-react'
import { Tooltip } from '../shared/Tooltip'

export type ActiveRow = {
  id: string
  name: string
  status: string
  budget?: string
  nextAction?: string
  preview?: string
}

const PALETTE: Record<string, string> = {
  negotiating: 'teal',
  approving: 'yellow',
  pending: 'yellow',
  sourcing: 'blue',
  contracted: 'green',
  completed: 'green',
  provisioning: 'blue',
  draft: 'gray',
  intake: 'gray',
  cancelled: 'red',
}

export interface ActiveRequestsListProps {
  items: ActiveRow[]
  onRowClick?: (id: string) => void
}

export function ActiveRequestsList({ items, onRowClick }: ActiveRequestsListProps) {
  return (
    <Box>
      {items.map((it, idx) => {
        const palette = PALETTE[it.status] ?? 'gray'
        return (
          <Flex
            key={it.id}
            role="group"
            align="center"
            justify="space-between"
            px={3}
            py={2.5}
            borderTopWidth={idx === 0 ? '0' : '1px'}
            borderColor="border"
            _hover={{ bg: 'bg.subtle' }}
            cursor="pointer"
            onClick={() => onRowClick?.(it.id)}
          >
            {/* Left: Name + subtle details */}
            <Box flex={1} minW={0} pr={3}>
              <Flex align="center" gap={2} minW={0}>
                <Tooltip content={it.name} wrapperProps={{ display: 'block', flex: 1, minW: 0, maxW: '100%', overflow: 'hidden' }}>
                  <Text as="span" display="block" width="100%" overflow="hidden" textOverflow="ellipsis" whiteSpace="nowrap" fontSize="sm" color="fg" fontWeight="normal">
                    {it.name}
                  </Text>
                </Tooltip>
                {/* Status: tiny pill dot + text muted */}
                <Flex align="center" gap={1} color="fg.muted" fontSize="xs">
                  <Box as="span" w={2} h={2} borderRadius="full" bg={`${palette}.emphasized`} opacity={0.9} />
                  <Text>{it.status}</Text>
                </Flex>
              </Flex>
              {/* Hover-only extra metadata */}
              {(it.preview || it.budget || it.nextAction) && (
                <Flex align="center" gap={3} mt={1} color="fg.muted" fontSize="xs" opacity={0} transform="translateY(-2px)" transition="all 220ms ease" _groupHover={{ opacity: 1, transform: 'translateY(0)' }}>
                  {it.preview && <Text truncate>{it.preview}</Text>}
                  {it.budget && <Text>{it.budget}</Text>}
                  {it.nextAction && <Text>{it.nextAction}</Text>}
                </Flex>
              )}
            </Box>

            {/* Right: chevron */}
            <Icon as={ChevronRight} boxSize={4} color="fg.muted" _groupHover={{ transform: 'translateX(2px)' }} transition="transform 200ms ease" />
          </Flex>
        )
      })}
    </Box>
  )
}
