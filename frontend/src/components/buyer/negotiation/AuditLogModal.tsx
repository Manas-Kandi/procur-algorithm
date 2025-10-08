import {
  Box,
  Text,
  VStack,
  HStack,
  Badge,
  Button,
  Portal,
} from '@chakra-ui/react'
import { formatDistanceToNow } from 'date-fns'
import { FileText, User, Bot, Shield, CheckCircle2, AlertTriangle } from 'lucide-react'

export interface AuditEntry {
  id: string
  timestamp: string
  actor: 'user' | 'agent' | 'system' | 'policy'
  action: string
  details: string
  metadata?: Record<string, any>
  level: 'info' | 'warning' | 'success'
}

interface AuditLogModalProps {
  isOpen: boolean
  onClose: () => void
  sessionId: string
  entries: AuditEntry[]
}

const ACTOR_CONFIG = {
  user: {
    icon: User,
    label: 'User',
    color: 'var(--core-color-brand-primary)',
    bg: 'var(--core-color-brand-bg)',
  },
  agent: {
    icon: Bot,
    label: 'AI Agent',
    color: 'var(--core-color-ai-primary)',
    bg: 'var(--core-color-ai-bg)',
  },
  system: {
    icon: FileText,
    label: 'System',
    color: 'var(--core-color-text-secondary)',
    bg: 'var(--core-color-background-tertiary)',
  },
  policy: {
    icon: Shield,
    label: 'Policy Engine',
    color: 'var(--core-color-purple-600)',
    bg: 'var(--core-color-purple-100)',
  },
}

const LEVEL_CONFIG = {
  info: {
    icon: FileText,
    color: 'var(--core-color-text-muted)',
  },
  warning: {
    icon: AlertTriangle,
    color: 'var(--core-color-warning)',
  },
  success: {
    icon: CheckCircle2,
    color: 'var(--core-color-success)',
  },
}

export function AuditLogModal({
  isOpen,
  onClose,
  sessionId,
  entries,
}: AuditLogModalProps): JSX.Element {
  if (!isOpen) return <></>

  return (
    <Portal>
      {/* Overlay */}
      <Box
        position="fixed"
        top={0}
        left={0}
        right={0}
        bottom={0}
        bg="blackAlpha.600"
        zIndex={1400}
        onClick={onClose}
      />

      {/* Modal Content */}
      <Box
        position="fixed"
        top="50%"
        left="50%"
        transform="translate(-50%, -50%)"
        maxW="800px"
        w="90%"
        maxH="80vh"
        bg="var(--core-color-surface-canvas)"
        borderRadius="lg"
        borderWidth="1px"
        borderColor="var(--core-color-border-default)"
        boxShadow="2xl"
        zIndex={1500}
        display="flex"
        flexDirection="column"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <Box
          p={6}
          borderBottomWidth="1px"
          borderColor="var(--core-color-border-default)"
        >
          <HStack justify="space-between" align="start">
            <VStack align="start" gap={1}>
              <Text fontSize="xl" fontWeight="semibold" color="var(--core-color-text-primary)">
                Audit Log
              </Text>
              <Text fontSize="sm" color="var(--core-color-text-muted)">
                Step-by-step agent decisions for session {sessionId.slice(0, 8)}
              </Text>
            </VStack>
            <Button size="sm" variant="ghost" onClick={onClose}>
              ✕
            </Button>
          </HStack>
        </Box>

        {/* Body */}
        <Box flex="1" overflowY="auto" p={6}>
          {entries.length === 0 ? (
            <Box
              p={6}
              textAlign="center"
              borderRadius="md"
              bg="var(--core-color-surface-subtle)"
            >
              <Text color="var(--core-color-text-muted)">No audit entries yet</Text>
            </Box>
          ) : (
            <VStack align="stretch" gap={0}>
              {entries.map((entry, index) => {
                const actorConfig = ACTOR_CONFIG[entry.actor]
                const levelConfig = LEVEL_CONFIG[entry.level]
                const ActorIcon = actorConfig.icon
                const LevelIcon = levelConfig.icon
                const isLast = index === entries.length - 1

                return (
                  <Box key={entry.id}>
                    <Box position="relative" pl={12} pb={isLast ? 0 : 4}>
                      {/* Timeline line */}
                      {!isLast && (
                        <Box
                          position="absolute"
                          left="20px"
                          top="32px"
                          bottom="-4px"
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
                        bg={actorConfig.bg}
                        borderWidth="2px"
                        borderColor="var(--core-color-surface-canvas)"
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                      >
                        <ActorIcon
                          className="h-5 w-5"
                          style={{ color: actorConfig.color }}
                        />
                      </Box>

                      {/* Content */}
                      <Box
                        p={3}
                        borderRadius="md"
                        bg="var(--core-color-surface-canvas)"
                        borderWidth="1px"
                        borderColor="var(--core-color-border-subtle)"
                      >
                        <HStack justify="space-between" align="start" mb={2}>
                          <HStack gap={2}>
                            <Badge
                              fontSize="xs"
                              px={2}
                              py={0.5}
                              borderRadius="sm"
                              bg={actorConfig.bg}
                              color={actorConfig.color}
                            >
                              {actorConfig.label}
                            </Badge>
                            <HStack gap={1}>
                              <LevelIcon
                                className="h-3 w-3"
                                style={{ color: levelConfig.color }}
                              />
                              <Text
                                fontSize="sm"
                                fontWeight="medium"
                                color="var(--core-color-text-primary)"
                              >
                                {entry.action}
                              </Text>
                            </HStack>
                          </HStack>
                          <Text fontSize="xs" color="var(--core-color-text-tertiary)">
                            {formatDistanceToNow(new Date(entry.timestamp), { addSuffix: true })}
                          </Text>
                        </HStack>

                        <Text fontSize="sm" color="var(--core-color-text-muted)" mb={2}>
                          {entry.details}
                        </Text>

                        {entry.metadata && Object.keys(entry.metadata).length > 0 && (
                          <Box
                            mt={2}
                            p={2}
                            borderRadius="sm"
                            bg="var(--core-color-surface-subtle)"
                            fontSize="xs"
                          >
                            {Object.entries(entry.metadata).map(([key, value]) => (
                              <HStack key={key} gap={2}>
                                <Text color="var(--core-color-text-secondary)" fontWeight="medium">
                                  {key}:
                                </Text>
                                <Text color="var(--core-color-text-muted)">
                                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                </Text>
                              </HStack>
                            ))}
                          </Box>
                        )}
                      </Box>
                    </Box>
                    {!isLast && (
                      <Box
                        my={2}
                        h="1px"
                        bg="var(--core-color-border-subtle)"
                      />
                    )}
                  </Box>
                )
              })}
            </VStack>
          )}
        </Box>
      </Box>
    </Portal>
  )
}
