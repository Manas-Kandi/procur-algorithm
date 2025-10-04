import { type ReactNode } from 'react'
import { AlertTriangle, CheckCircle2, Info, OctagonAlert } from 'lucide-react'
import { Box, Flex, Text, Icon } from '@chakra-ui/react'
import { Button } from './Button'

interface SmartAlertProps {
  title: string
  message: string
  emphasis?: string
  severity?: 'info' | 'success' | 'warning' | 'critical'
  actionLabel?: string
  onAction?: () => void
  footer?: ReactNode
  compact?: boolean
}

const SEVERITY_ICON = {
  info: Info,
  success: CheckCircle2,
  warning: AlertTriangle,
  critical: OctagonAlert,
} as const

const SEVERITY_PALETTE = {
  info: 'blue',
  success: 'green',
  warning: 'yellow',
  critical: 'red',
} as const

export function SmartAlert({
  title,
  message,
  emphasis,
  severity = 'info',
  actionLabel,
  onAction,
  footer,
  compact = false,
}: SmartAlertProps): JSX.Element {
  const IconCmp = SEVERITY_ICON[severity]
  const palette = SEVERITY_PALETTE[severity]

  return (
    <Box
      display="flex"
      alignItems="flex-start"
      gap={4}
      rounded="sm"
      borderWidth="1px"
      borderColor={`${palette}.emphasized`}
      bg={`${palette}.subtle`}
      px={4}
      py={4}
    >
      <Flex
        h={9}
        w={9}
        flexShrink={0}
        align="center"
        justify="center"
        rounded="sm"
        bg={`${palette}.subtle`}
        color={`${palette}.fg`}
        borderWidth="1px"
        borderColor={`${palette}.emphasized`}
      >
        <Icon as={IconCmp} boxSize={5} aria-hidden="true" />
      </Flex>
      <Box flex={1} minW={0}>
        <Flex wrap="wrap" align="start" justify="space-between" gap={3}>
          <Box flex={1} minW={0}>
            <Text fontSize="sm" fontWeight="semibold" color="fg">
              {title}
            </Text>
            <Text mt={1} fontSize="sm" color="fg.muted" lineHeight="tall">
              {message}{' '}
              {emphasis && (
                <Text as="span" fontWeight="semibold" color="fg">
                  {emphasis}
                </Text>
              )}
            </Text>
          </Box>
          {actionLabel && (
            <Button
              size={compact ? 'sm' : 'md'}
              variant={severity === 'critical' ? 'danger' : 'outline'}
              onClick={onAction}
            >
              {actionLabel}
            </Button>
          )}
        </Flex>
        {footer && (
          <Text mt={3} fontSize="xs" color="fg.muted">
            {footer}
          </Text>
        )}
      </Box>
    </Box>
  )
}
