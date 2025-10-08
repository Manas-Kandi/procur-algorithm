import React from 'react'
import { Home, FilePlus, Briefcase, ChevronsRight, ShieldCheck } from 'lucide-react'
import { Box, VStack, Button, Icon, IconButton, Flex, Text } from '@chakra-ui/react'
import { Tooltip } from '../shared/Tooltip'
import { useAuthStore } from '../../store/auth'

export interface ProcurSidebarProps {
  open: boolean
  selectedKey?: string
  onSelect?: (key: string) => void
  onToggle?: () => void
}

type Item = { key: string; label: string; Icon: any }

export function ProcurSidebar({
  open,
  selectedKey = 'dashboard',
  onSelect,
  onToggle,
}: ProcurSidebarProps) {
  const { user } = useAuthStore()
  const initial = (user?.full_name ?? user?.username ?? 'U').trim().charAt(0).toUpperCase()
  const role = user?.role

  // Minimal, role-aware items
  const items: Item[] = [
    { key: 'dashboard', label: 'Dashboard', Icon: Home },
    { key: 'new-request', label: 'New Request', Icon: FilePlus },
    // Approvals visible for approver/admin roles
    ...(role === 'approver' || role === 'admin' ? [{ key: 'approvals', label: 'Approvals', Icon: ShieldCheck }] : []),
    { key: 'portfolio', label: 'Portfolio', Icon: Briefcase },
  ]

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
      w={open ? '14rem' : '4.25rem'}
      bg="bg.subtle"
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

      {/* Divider */}
      <Box as="hr" borderTopWidth="1px" borderColor="border" />

      {/* Section label */}
      {open && (
        <Box px={3} py={3}>
          <Text fontSize="xs" color="fg.muted" textTransform="uppercase" letterSpacing="0.08em">
            Workspace
          </Text>
        </Box>
      )}

      <VStack align="stretch" px={2} gap={1.5}>
        {items.map(({ key, label, Icon: LIcon }) => {
          const selected = key === selectedKey
          const button = (
            <Button
              key={key}
              onClick={() => onSelect?.(key)}
              justifyContent="flex-start"
              variant={selected ? 'subtle' : 'ghost'}
              h="48px"
              px={3.5}
              borderRadius="sm"
              position="relative"
              color={selected ? 'brand.fg' : 'fg.muted'}
              bg={selected ? 'brand.subtle' : undefined}
              _hover={{ bg: selected ? 'brand.subtle' : 'bg.subtle' }}
              _focusVisible={{ outline: '2px solid', outlineColor: 'blue.focusRing', outlineOffset: '2px' }}
              aria-current={selected ? 'page' : undefined}
            >
              {/* Active accent bar (left) */}
              {selected && (
                <Box position="absolute" left={1} top={2} bottom={2} w="3px" bg="brand.emphasized" borderRadius="full" />
              )}
              <Icon as={LIcon} boxSize={5} mr={open ? 3 : 0} color={selected ? 'brand.fg' : 'fg.muted'} />
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

