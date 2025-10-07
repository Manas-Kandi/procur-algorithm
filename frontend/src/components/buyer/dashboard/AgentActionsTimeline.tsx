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
  success: {
    icon: CheckCircle,
    color: 'var(--core-color-success)',
    bgColor: 'var(--core-color-success-bg)',
  },
  pending: {
    icon: Info,
    color: 'var(--core-color-brand-primary)',
    bgColor: 'var(--core-color-brand-bg)',
  },
  info: {
    icon: Info,
    color: 'var(--core-color-info)',
    bgColor: 'var(--core-color-info-bg)',
  },
  warning: {
    icon: AlertCircle,
    color: 'var(--core-color-warning)',
    bgColor: 'var(--core-color-warning-bg)',
  },
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
      <Box
        p={6}
        textAlign="center"
        borderWidth="1px"
        borderColor="var(--core-color-border-subtle)"
        borderRadius="md"
        bg="var(--core-color-surface-subtle)"
      >
        <Text fontSize="sm" color="var(--core-color-text-muted)">
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
            pb={isLast ? 0 : 6}
            cursor={onActionClick ? 'pointer' : 'default'}
            onClick={() => onActionClick?.(action)}
            _hover={
              onActionClick
                ? {
                    '& .action-content': {
                      borderColor: 'var(--core-color-border-default)',
                      bg: 'var(--core-color-surface-subtle)',
                    },
                  }
                : undefined
            }
            transition="all 0.2s"
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

            {/* Icon */}
            <Box
              position="absolute"
              left="0"
              top="4px"
              w={10}
              h={10}
              borderRadius="full"
              bg={config.bgColor}
              borderWidth="2px"
              borderColor="var(--core-color-surface-canvas)"
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
              <Icon className="h-5 w-5" style={{ color: config.color }} />
            </Box>

            {/* Content */}
            <Box
              className="action-content"
              p={4}
              borderWidth="1px"
              borderColor="var(--core-color-border-subtle)"
              borderRadius="md"
              bg="var(--core-color-surface-canvas)"
              transition="all 0.2s"
            >
              <HStack justify="space-between" align="start" mb={2}>
                <HStack gap={2}>
                  <Bot className="h-4 w-4" style={{ color: 'var(--core-color-ai-primary)' }} />
                  <Text fontSize="sm" fontWeight="semibold" color="var(--core-color-text-primary)">
                    {action.action}
                  </Text>
                </HStack>
                <Text fontSize="xs" color="var(--core-color-text-tertiary)">
                  {formatDistanceToNow(new Date(action.timestamp), { addSuffix: true })}
                </Text>
              </HStack>

              <Text fontSize="sm" color="var(--core-color-text-muted)" mb={2}>
                {action.description}
              </Text>

              <HStack gap={2} flexWrap="wrap">
                <Badge
                  fontSize="xs"
                  px={2}
                  py={0.5}
                  borderRadius="sm"
                  bg="var(--core-color-background-tertiary)"
                  color="var(--core-color-text-secondary)"
                >
                  {ACTOR_LABELS[action.actor]}
                </Badge>
                {action.vendorName && (
                  <Badge
                    fontSize="xs"
                    px={2}
                    py={0.5}
                    borderRadius="sm"
                    bg="var(--core-color-brand-bg)"
                    color="var(--core-color-brand-primary)"
                  >
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
