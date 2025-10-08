import { Box, Text, VStack, HStack, Badge } from '@chakra-ui/react'
import { formatDistanceToNow } from 'date-fns'
import { Bot, CheckCircle, AlertCircle, Info } from 'lucide-react'

export interface AgentAction {
  id: string
  timestamp: string
  actor: 'buyer_agent' | 'seller_agent' | 'system'
  action: string
  description: string
  requestId?: string
  vendorName?: string
  status: 'success' | 'pending' | 'info' | 'warning'
}

interface AgentActionsTimelineProps {
  actions: AgentAction[]
  maxItems?: number
  onActionClick?: (action: AgentAction) => void
}

const ACTION_CONFIG = {
  success: { icon: CheckCircle, color: 'green.fg' },
  pending: { icon: Info, color: 'blue.fg' },
  info: { icon: Info, color: 'blue.fg' },
  warning: { icon: AlertCircle, color: 'yellow.fg' },
}

const ACTOR_LABELS = {
  buyer_agent: 'Buyer Agent',
  seller_agent: 'Seller Agent',
  system: 'System',
}

export function AgentActionsTimeline({
  actions,
  maxItems = 10,
  onActionClick,
}: AgentActionsTimelineProps): JSX.Element {
  const displayActions = actions.slice(0, maxItems)

  if (displayActions.length === 0) {
    return (
      <Box p={6} textAlign="center" bg="bg.subtle" borderRadius="md">
        <Text fontSize="sm" color="fg.muted">
          No recent agent activity
        </Text>
      </Box>
    )
  }

  return (
    <VStack align="stretch" gap={0}>
      {displayActions.map((action, index) => {
        const config = ACTION_CONFIG[action.status]
        const Icon = config.icon
        const isLast = index === displayActions.length - 1

        return (
          <Box
            key={action.id}
            position="relative"
            pl={12}
            pb={isLast ? 0 : 5}
            cursor={onActionClick ? 'pointer' : 'default'}
            onClick={() => onActionClick?.(action)}
            _hover={onActionClick ? { '& .action-content': { bg: 'bg.subtle' } } : undefined}
            transition="all 0.2s"
          >
            {/* Timeline line */}
            {!isLast && (
              <Box
                position="absolute"
                left="20px"
                top="32px"
                bottom="0"
                width="1px"
                bg="border"
              />
            )}

            {/* Icon */}
            <Box
              position="absolute"
              left="0"
              top="4px"
              w={10}
              h={10}
              borderRadius="full"
              bg="bg.subtle"
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
              <Icon className="h-5 w-5" style={{ color: 'currentColor' }} color={config.color as any} />
            </Box>

            {/* Content */}
            <Box className="action-content" p={4} borderRadius="md" bg="transparent" transition="all 0.2s" borderBottomWidth={isLast ? '0' : '1px'} borderColor="border">
              <HStack justify="space-between" align="start" mb={2}>
                <HStack gap={2}>
                  <Bot className="h-4 w-4" style={{ color: 'var(--core-color-ai-primary)' }} />
                  <Text fontSize="sm" fontWeight="semibold" color="fg">
                    {action.action}
                  </Text>
                </HStack>
                <Text fontSize="xs" color="fg.muted">
                  {formatDistanceToNow(new Date(action.timestamp), { addSuffix: true })}
                </Text>
              </HStack>

              <Text fontSize="sm" color="fg.muted" mb={2}>
                {action.description}
              </Text>

              <HStack gap={2} flexWrap="wrap">
                <Badge fontSize="xs" px={2} py={0.5} borderRadius="sm" bg="transparent" borderWidth="1px" borderColor="border" color="fg.muted">
                  {ACTOR_LABELS[action.actor]}
                </Badge>
                {action.vendorName && (
                  <Badge fontSize="xs" px={2} py={0.5} borderRadius="sm" bg="transparent" borderWidth="1px" borderColor="border" color="fg.muted">
                    {action.vendorName}
                  </Badge>
                )}
              </HStack>
            </Box>
          </Box>
        )
      })}
    </VStack>
  )
}
