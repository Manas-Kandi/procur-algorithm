import { Bot, Building2 } from 'lucide-react'
import { useState } from 'react'
import { VStack, Flex, Box, Text, Icon, Button } from '@chakra-ui/react'

interface Message {
  id: string
  sender: 'agent' | 'vendor'
  content: string
  timestamp?: string
  metadata?: {
    price?: string
    term?: string
    payment?: string
  }
}

interface NegotiationStoryboardProps {
  messages: Message[]
  vendorName?: string
}

export function NegotiationStoryboard({
  messages,
  vendorName = 'Vendor',
}: NegotiationStoryboardProps) {
  const [expanded, setExpanded] = useState(false)

  const visible =
    expanded || messages.length <= 3 ? messages : messages.slice(-3)
  const hasMore = messages.length > 3

  // Use Chakra v3 semantic tokens
  const bubbleAgentBg = 'bg.subtle'
  const bubbleVendorBg = 'bg.subtle'
  const avatarAgentBg = 'bg.subtle'
  const avatarVendorBg = 'bg.subtle'
  const textPrimary = 'fg'
  const textSecondary = 'fg.muted'
  const avatarText = 'fg'

  return (
    <VStack gap={3} align="stretch">
      {visible.map((message) => {
        const isAgent = message.sender === 'agent'
        const bubbleBg = isAgent ? bubbleAgentBg : bubbleVendorBg
        const avatarBg = isAgent ? avatarAgentBg : avatarVendorBg
        return (
          <Flex key={message.id} gap={3} justify={isAgent ? 'flex-start' : 'flex-end'}>
            {isAgent && (
              <Flex
                h={7}
                w={7}
                flexShrink={0}
                align="center"
                justify="center"
                rounded="full"
                bg={avatarBg}
                color={avatarText}
              >
                <Icon as={Bot} boxSize={3.5} />
              </Flex>
            )}

            <Box
              maxW="75%"
              rounded="0"
              px={4}
              py={2.5}
              bg={bubbleBg}
            >
              <Flex align="baseline" gap={2}>
                <Text fontSize="xs" fontWeight="semibold" color={textPrimary}>
                  {isAgent ? 'Agent' : vendorName}
                </Text>
                {message.timestamp && (
                  <Text fontSize="xs" color={textSecondary}>
                    {message.timestamp}
                  </Text>
                )}
              </Flex>
              <Text mt={1} fontSize="sm" color={textPrimary}>
                {message.content}
              </Text>
            </Box>

            {!isAgent && (
              <Flex
                h={7}
                w={7}
                flexShrink={0}
                align="center"
                justify="center"
                rounded="full"
                bg={avatarBg}
                color={avatarText}
              >
                <Icon as={Building2} boxSize={3.5} />
              </Flex>
            )}
          </Flex>
        )
      })}

      {hasMore && (
        <Box pt={1}>
          <Button
            size="xs"
            variant="plain"
            colorPalette="gray"
            color={textSecondary}
            _hover={{ textDecoration: 'underline' }}
            onClick={() => setExpanded((v) => !v)}
          >
            {expanded ? 'Collapse' : `Show full thread (${messages.length})`}
          </Button>
        </Box>
      )}
    </VStack>
  )
}
