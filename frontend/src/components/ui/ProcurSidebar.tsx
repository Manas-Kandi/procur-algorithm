import React from 'react'
import { Home, FilePlus, Briefcase, ChevronsRight } from 'lucide-react'
import { Box, VStack, Button, Icon, IconButton, Flex, Text } from '@chakra-ui/react'
import { ColorModeButton } from './color-mode'

export interface ProcurSidebarProps {
  open: boolean
  selectedKey?: string
  onSelect?: (key: string) => void
  onToggle?: () => void
}

const items = [
  { key: 'dashboard', label: 'Dashboard', Icon: Home, color: '#60A5FA' }, // blue
  { key: 'new-request', label: 'New Request', Icon: FilePlus, color: '#34D399' }, // green
  { key: 'portfolio', label: 'Portfolio', Icon: Briefcase, color: '#A78BFA' }, // purple
]

export function ProcurSidebar({
  open,
  selectedKey = 'dashboard',
  onSelect,
  onToggle,
}: ProcurSidebarProps) {

  return (
    <Box
      as="aside"
      position="sticky"
      top={0}
      h="100vh"
      flexShrink={0}
      borderRightWidth="1px"
      borderColor="gray.200"
      transition="width 0.3s ease-in-out"
      w={open ? '16rem' : '4rem'}
      bg="white"
      _dark={{ borderColor: '#262626', bg: '#0F0F0F' }}
    >
      {/* Title / Brand */}
      <Flex align="center" justify="space-between" gap={2} px={2} py={3}>
        <Box minW={0}>
          <Text fontSize="sm" fontWeight="semibold" color="gray.600" _dark={{ color: 'gray.400' }}>
            {open ? 'Procur' : 'P.'}
          </Text>
        </Box>
        {open && <ColorModeButton size="xs" />}
      </Flex>

      <VStack align="stretch" px={2} gap={1}>
        {items.map(({ key, label, Icon: LIcon }) => {
          const selected = key === selectedKey
          return (
            <Button
              key={key}
              onClick={() => onSelect?.(key)}
              justifyContent="flex-start"
              variant={selected ? 'solid' : 'ghost'}
              colorScheme={selected ? 'gray' : undefined}
              h="44px"
              // Default text/icon color: light gray. Selected: white on dark bg.
              color={selected ? 'white' : 'gray.600'}
              _dark={{ color: selected ? 'white' : 'gray.400' }}
              // Ensure selected state has a clear background and doesn't disappear on hover
              bg={selected ? 'gray.700' : 'transparent'}
              _hover={{
                bg: selected ? 'gray.700' : 'gray.100',
                _dark: { bg: selected ? 'gray.700' : 'whiteAlpha.100' },
              }}
              _active={{
                bg: selected ? 'gray.700' : 'gray.200',
                _dark: { bg: selected ? 'gray.700' : 'whiteAlpha.200' },
              }}
            >
              <Icon as={LIcon} boxSize={4} mr={open ? 2 : 0} />
              {open ? label : ''}
            </Button>
          )
        })}
      </VStack>

      {/* Toggle */}
      <Flex position="absolute" bottom={0} left={0} right={0} px={2} py={2} align="center">
        <IconButton
          aria-label={open ? 'Collapse sidebar' : 'Expand sidebar'}
          variant="ghost"
          onClick={onToggle}
        >
          <Icon as={ChevronsRight} boxSize={4} transform={open ? 'rotate(180deg)' : undefined} transition="transform 0.3s" color="gray.500" _dark={{ color: 'gray.400' }} />
        </IconButton>
        {open && (
          <Text fontSize="sm" color="gray.500" _dark={{ color: 'gray.400' }} ml={2}>
            Hide
          </Text>
        )}
      </Flex>
    </Box>
  )
}
