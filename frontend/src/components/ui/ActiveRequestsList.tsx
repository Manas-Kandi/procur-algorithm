import { Box, Flex, Icon, Text } from '@chakra-ui/react'
import { ChevronRight } from 'lucide-react'
import { Tooltip } from '../shared/Tooltip'
import { useState } from 'react'

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
  hoverMs?: number
}

export function ActiveRequestsList({ items, onRowClick, hoverMs = 250 }: ActiveRequestsListProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)
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
            py={3}
            mt={idx === 0 ? 0 : 1.5}
            _hover={{ bg: 'bg.subtle' }}
            cursor="pointer"
            onClick={() => onRowClick?.(it.id)}
            data-expanded={expandedId === it.id ? 'true' : 'false'}
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
              {/* Hover/expand metadata */}
              {(it.preview || it.budget || it.nextAction) && (
                <Flex
                  align="center"
                  gap={3}
                  mt={1}
                  color="fg.muted"
                  fontSize="xs"
                  transition={`all ${hoverMs}ms ease`}
                  opacity={expandedId === it.id ? 1 : 0}
                  transform={expandedId === it.id ? 'translateY(0)' : 'translateY(-2px)'}
                  maxH={expandedId === it.id ? '48px' : '0px'}
                  overflow="hidden"
                  _groupHover={{ opacity: 1, transform: 'translateY(0)', maxH: '48px' }}
                >
                  {it.preview && <Text truncate>{it.preview}</Text>}
                  {it.budget && <Text>{it.budget}</Text>}
                  {it.nextAction && <Text>{it.nextAction}</Text>}
                </Flex>
              )}
            </Box>

            {/* Right: chevron */}
            <Box
              as="button"
              onClick={(e) => {
                e.stopPropagation()
                setExpandedId((prev) => (prev === it.id ? null : it.id))
              }}
              aria-label={expandedId === it.id ? 'Collapse details' : 'Expand details'}
            >
              <Icon
                as={ChevronRight}
                boxSize={4}
                color="fg.muted"
                transition={`transform ${hoverMs}ms ease`}
                transform={expandedId === it.id ? 'rotate(90deg)' : undefined}
              />
            </Box>
          </Flex>
        )
      })}
    </Box>
  )
}
