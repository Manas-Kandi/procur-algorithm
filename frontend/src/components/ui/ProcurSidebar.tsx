import React from 'react'
import { Home, FilePlus, Briefcase, ChevronsRight } from 'lucide-react'
import { Box, VStack, Button, Icon, IconButton, Flex, Text } from '@chakra-ui/react'
import { Tooltip } from '../shared/Tooltip'
import { useAuthStore } from '../../store/auth'

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
  const { user } = useAuthStore()
  const initial = (user?.full_name ?? user?.username ?? 'U').trim().charAt(0).toUpperCase()

  return (
    <Box
      as="aside"
      position="sticky"
      top={0}
      h="100vh"
      flexShrink={0}
      borderRightWidth="1px"
      borderColor="border"
      transition="width 0.3s ease-in-out"
      w={open ? '16rem' : '4rem'}
      bg="bg.panel"
    >
      {/* Title / Brand */}
      <Flex align="center" justify="space-between" gap={2} px={3} py={4}>
        <Flex align="center" gap={2} minW={0}>
          <Box w={7} h={7} borderRadius="md" bg="brand.subtle" borderWidth="1px" borderColor="brand.emphasized" display="flex" alignItems="center" justifyContent="center">
            <Text fontSize="sm" color="brand.fg" fontWeight="semibold">P</Text>
          </Box>
          {open && (
            <Box minW={0}>
              <Text fontSize="sm" fontWeight="semibold" color="fg">Procur</Text>
            </Box>
          )}
        </Flex>
        {/* Theme switcher removed per request */}
      </Flex>

      <VStack align="stretch" px={2} gap={1.5}>
        {items.map(({ key, label, Icon: LIcon }) => {
          const selected = key === selectedKey
          const button = (
            <Button
              key={key}
              onClick={() => onSelect?.(key)}
              justifyContent="flex-start"
              variant={selected ? 'solid' : 'ghost'}
              colorPalette={selected ? 'gray' : undefined}
              h="48px"
              px={3.5}
              borderRadius="md"
              position="relative"
              color={selected ? 'bg.inverted' : 'fg.muted'}
              bg={selected ? 'brand.subtle' : undefined}
              _hover={{ bg: selected ? 'brand.subtle' : 'bg.subtle' }}
              _focusVisible={{ outline: '2px solid', outlineColor: 'blue.focusRing', outlineOffset: '2px' }}
              aria-current={selected ? 'page' : undefined}
            >
              {/* Active accent bar */}
              {selected && (
                <Box position="absolute" right={1} top={2} bottom={2} w="2px" bg="brand.emphasized" borderRadius="full" />
              )}
              <Icon as={LIcon} boxSize={5} mr={open ? 3 : 0} />
              {open ? (
                <Text as="span" fontSize="sm" fontWeight={selected ? 'semibold' : 'normal'}>
                  {label}
                </Text>
              ) : null}
            </Button>
          )
          return open ? (
            button
          ) : (
            <Tooltip key={key} content={label} wrapperProps={{ display: 'block' }}>
              {button}
            </Tooltip>
          )
        })}
      </VStack>

      {/* Toggle */}
      <Flex position="absolute" bottom={0} left={0} right={0} px={2} py={3} align="center" justify="space-between">
        {/* User initial chip for personalization */}
        {open ? (
          <Box w={8} h={8} borderRadius="full" bg="bg.subtle" color="fg" borderWidth="1px" borderColor="border" display="flex" alignItems="center" justifyContent="center" fontSize="sm" fontWeight="semibold">
            {initial}
          </Box>
        ) : <Box />}
        <Tooltip content={open ? 'Collapse' : 'Expand'}>
          <IconButton
            aria-label={open ? 'Collapse sidebar' : 'Expand sidebar'}
            variant="ghost"
            onClick={onToggle}
            _focusVisible={{ outline: '2px solid', outlineColor: 'blue.focusRing', outlineOffset: '2px' }}
          >
            <Icon as={ChevronsRight} boxSize={5} transform={open ? 'rotate(180deg)' : undefined} transition="transform 0.3s" color="fg.muted" />
          </IconButton>
        </Tooltip>
      </Flex>
    </Box>
  )
}

