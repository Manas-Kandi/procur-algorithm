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

  // Resolve color tokens once per render (hooks must not run inside loops)
  const bubbleAgentBg = 'gray.100'
  const bubbleVendorBg = 'gray.200'
  const avatarAgentBg = 'gray.300'
  const avatarVendorBg = 'gray.300'
  const textPrimary = 'gray.800'
  const textSecondary = 'gray.600'
  const avatarText = 'gray.900'

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
                _dark={{ bg: '#333333', color: '#FAFAFA' }}
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
              _dark={{ bg: '#1A1A1A' }}
            >
              <Flex align="baseline" gap={2}>
                <Text fontSize="xs" fontWeight="semibold" color={textPrimary} _dark={{ color: '#FAFAFA' }}>
                  {isAgent ? 'Agent' : vendorName}
                </Text>
                {message.timestamp && (
                  <Text fontSize="xs" color={textSecondary} _dark={{ color: '#A1A1AA' }}>
                    {message.timestamp}
                  </Text>
                )}
              </Flex>
              <Text mt={1} fontSize="sm" color={textPrimary} _dark={{ color: '#FAFAFA' }}>
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
                _dark={{ bg: '#333333', color: '#FAFAFA' }}
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
            color={textSecondary}
            _dark={{ color: 'gray.400' }}
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
