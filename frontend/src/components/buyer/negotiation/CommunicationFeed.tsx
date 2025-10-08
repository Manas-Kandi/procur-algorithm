import { Box, Text, VStack, HStack, Badge, Textarea, Button, Avatar } from '@chakra-ui/react'
import { formatDistanceToNow } from 'date-fns'
import { Bot, User, MessageSquare, Send, Tag } from 'lucide-react'
import { useState } from 'react'

export interface Message {
  id: string
  timestamp: string
  sender: 'agent' | 'vendor' | 'user' | 'system'
  senderName: string
  content: string
  type: 'message' | 'note' | 'system'
  tags?: string[]
}

interface CommunicationFeedProps {
  messages: Message[]
  onSendMessage?: (message: string) => void
  onTagApprover?: () => void
  onTagLegal?: () => void
}

const SENDER_CONFIG = {
  agent: {
    icon: Bot,
    color: 'var(--core-color-ai-primary)',
    bgColor: 'var(--core-color-ai-bg)',
    label: 'AI Agent',
  },
  vendor: {
    icon: MessageSquare,
    color: 'var(--core-color-brand-primary)',
    bgColor: 'var(--core-color-brand-bg)',
    label: 'Vendor',
  },
  user: {
    icon: User,
    color: 'var(--core-color-purple-600)',
    bgColor: 'var(--core-color-purple-100)',
    label: 'You',
  },
  system: {
    icon: MessageSquare,
    color: 'var(--core-color-text-secondary)',
    bgColor: 'var(--core-color-background-tertiary)',
    label: 'System',
  },
}

export function CommunicationFeed({
  messages,
  onSendMessage,
  onTagApprover,
  onTagLegal,
}: CommunicationFeedProps): JSX.Element {
  const [newMessage, setNewMessage] = useState('')

  const handleSend = () => {
    if (newMessage.trim() && onSendMessage) {
      onSendMessage(newMessage.trim())
      setNewMessage('')
    }
  }

  return (
    <Box
      borderWidth="1px"
      borderColor="var(--core-color-border-default)"
      borderRadius="lg"
      bg="var(--core-color-surface-canvas)"
      overflow="hidden"
    >
      {/* Header */}
      <Box
        p={4}
        borderBottomWidth="1px"
        borderColor="var(--core-color-border-default)"
        bg="var(--core-color-surface-subtle)"
      >
        <HStack justify="space-between">
          <Text fontSize="md" fontWeight="semibold" color="var(--core-color-text-primary)">
            Communication & Notes
          </Text>
          <HStack gap={2}>
            {onTagApprover && (
              <Button
                size="xs"
                variant="ghost"
                leftIcon={<Tag className="h-3 w-3" />}
                onClick={onTagApprover}
              >
                Tag Approver
              </Button>
            )}
            {onTagLegal && (
              <Button
                size="xs"
                variant="ghost"
                leftIcon={<Tag className="h-3 w-3" />}
                onClick={onTagLegal}
              >
                Tag Legal
              </Button>
            )}
          </HStack>
        </HStack>
      </Box>

      {/* Messages */}
      <Box maxH="400px" overflowY="auto" p={4}>
        {messages.length === 0 ? (
          <Box
            p={6}
            textAlign="center"
            borderRadius="md"
            bg="var(--core-color-surface-subtle)"
          >
            <MessageSquare className="h-8 w-8 mx-auto mb-2" style={{ color: 'var(--core-color-text-muted)' }} />
            <Text fontSize="sm" color="var(--core-color-text-muted)">
              No messages yet. Start the conversation or leave a note.
            </Text>
          </Box>
        ) : (
          <VStack align="stretch" gap={3}>
            {messages.map((message) => {
              const config = SENDER_CONFIG[message.sender]
              const Icon = config.icon
              const isUser = message.sender === 'user'

              return (
                <Box
                  key={message.id}
                  p={3}
                  borderRadius="md"
                  bg={message.type === 'note' ? 'var(--core-color-warning-bg)' : config.bgColor}
                  borderWidth="1px"
                  borderColor={message.type === 'note' ? 'var(--core-color-warning-border)' : 'var(--core-color-border-subtle)'}
                >
                  <HStack justify="space-between" align="start" mb={2}>
                    <HStack gap={2}>
                      <Box
                        p={1.5}
                        borderRadius="full"
                        bg={config.color}
                        color="white"
                      >
                        <Icon className="h-3 w-3" />
                      </Box>
                      <VStack align="start" gap={0}>
                        <Text fontSize="sm" fontWeight="semibold" color="var(--core-color-text-primary)">
                          {message.senderName}
                        </Text>
                        <Text fontSize="xs" color="var(--core-color-text-muted)">
                          {formatDistanceToNow(new Date(message.timestamp), { addSuffix: true })}
                        </Text>
                      </VStack>
                    </HStack>
                    {message.type === 'note' && (
                      <Badge
                        fontSize="xs"
                        px={2}
                        py={0.5}
                        borderRadius="sm"
                        bg="var(--core-color-warning)"
                        color="white"
                      >
                        Internal Note
                      </Badge>
                    )}
                  </HStack>

                  <Text fontSize="sm" color="var(--core-color-text-primary)">
                    {message.content}
                  </Text>

                  {message.tags && message.tags.length > 0 && (
                    <HStack gap={1} mt={2}>
                      {message.tags.map((tag) => (
                        <Badge
                          key={tag}
                          fontSize="xs"
                          px={2}
                          py={0.5}
                          borderRadius="sm"
                          bg="var(--core-color-background-tertiary)"
                          color="var(--core-color-text-secondary)"
                        >
                          @{tag}
                        </Badge>
                      ))}
                    </HStack>
                  )}
                </Box>
              )
            })}
          </VStack>
        )}
      </Box>

      {/* Input */}
      {onSendMessage && (
        <Box
          p={4}
          borderTopWidth="1px"
          borderColor="var(--core-color-border-default)"
          bg="var(--core-color-surface-subtle)"
        >
          <VStack align="stretch" gap={2}>
            <Textarea
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Add a note or comment..."
              size="sm"
              rows={2}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
            />
            <HStack justify="space-between">
              <Text fontSize="xs" color="var(--core-color-text-muted)">
                Press Enter to send, Shift+Enter for new line
              </Text>
              <Button
                size="sm"
                colorScheme="blue"
                leftIcon={<Send className="h-4 w-4" />}
                onClick={handleSend}
                isDisabled={!newMessage.trim()}
              >
                Send
              </Button>
            </HStack>
          </VStack>
        </Box>
      )}
    </Box>
  )
}
