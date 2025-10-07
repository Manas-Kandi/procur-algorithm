import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Box,
  Text,
  VStack,
  HStack,
  Badge,
  Divider,
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
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="2xl">
      <ModalOverlay />
      <ModalContent maxH="80vh">
        <ModalHeader>
          <VStack align="start" gap={1}>
            <Text>Audit Log</Text>
            <Text fontSize="sm" fontWeight="normal" color="var(--core-color-text-muted)">
              Step-by-step agent decisions for session {sessionId.slice(0, 8)}
            </Text>
          </VStack>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6} overflowY="auto">
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
                    {!isLast && <Divider my={2} borderColor="var(--core-color-border-subtle)" />}
                  </Box>
                )
              })}
            </VStack>
          )}
        </ModalBody>
      </ModalContent>
    </Modal>
  )
}
