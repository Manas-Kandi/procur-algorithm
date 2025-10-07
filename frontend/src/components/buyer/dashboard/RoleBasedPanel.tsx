import { Box, Text, VStack, HStack, Button, Badge } from '@chakra-ui/react'
import { Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { StatusBadge } from '../../shared/StatusBadge'
import type { Request } from '../../../types'

interface RoleBasedPanelProps {
  role: 'buyer' | 'approver' | 'requester'
  requests?: Request[]
  approvals?: Array<{
    id: string
    requestName: string
    vendorName: string
    price: number
    status: string
  }>
}

export function RoleBasedPanel({
  role,
  requests = [],
  approvals = [],
}: RoleBasedPanelProps): JSX.Element {
  const navigate = useNavigate()

  // Approver View
  if (role === 'approver') {
    const pendingApprovals = approvals.filter((a) => a.status === 'pending')

    return (
      <Box
        borderWidth="1px"
        borderColor="var(--core-color-border-default)"
        borderRadius="lg"
        bg="var(--core-color-surface-canvas)"
        p={6}
      >
        <VStack align="stretch" gap={4}>
          <HStack justify="space-between">
            <Box>
              <Text fontSize="md" fontWeight="semibold" color="var(--core-color-text-primary)">
                Requests Pending Approval
              </Text>
              <Text fontSize="sm" color="var(--core-color-text-muted)" mt={1}>
                Review AI-negotiated offers and make decisions
              </Text>
            </Box>
            <Badge
              fontSize="md"
              px={3}
              py={1}
              borderRadius="md"
              bg="var(--core-color-warning-bg)"
              color="var(--core-color-warning)"
            >
              {pendingApprovals.length}
            </Badge>
          </HStack>

          {pendingApprovals.length === 0 ? (
            <Box
              p={4}
              textAlign="center"
              borderRadius="md"
              bg="var(--core-color-surface-subtle)"
            >
              <CheckCircle className="h-8 w-8 mx-auto mb-2" style={{ color: 'var(--core-color-success)' }} />
              <Text fontSize="sm" color="var(--core-color-text-muted)">
                All caught up! No approvals pending.
              </Text>
            </Box>
          ) : (
            <VStack align="stretch" gap={3}>
              {pendingApprovals.slice(0, 3).map((approval) => (
                <Box
                  key={approval.id}
                  p={4}
                  borderRadius="md"
                  bg="var(--core-color-surface-subtle)"
                  borderWidth="1px"
                  borderColor="var(--core-color-border-subtle)"
                  cursor="pointer"
                  onClick={() => navigate('/approvals')}
                  _hover={{
                    borderColor: 'var(--core-color-border-default)',
                    boxShadow: 'sm',
                  }}
                  transition="all 0.2s"
                >
                  <VStack align="stretch" gap={2}>
                    <HStack justify="space-between">
                      <Text fontSize="sm" fontWeight="medium" color="var(--core-color-text-primary)">
                        {approval.requestName}
                      </Text>
                      <Clock className="h-4 w-4" style={{ color: 'var(--core-color-warning)' }} />
                    </HStack>
                    <HStack justify="space-between">
                      <Text fontSize="xs" color="var(--core-color-text-muted)">
                        {approval.vendorName}
                      </Text>
                      <Text fontSize="sm" fontWeight="semibold" color="var(--core-color-text-primary)">
                        ${approval.price.toLocaleString()}/mo
                      </Text>
                    </HStack>
                  </VStack>
                </Box>
              ))}
              <Button
                size="sm"
                variant="outline"
                onClick={() => navigate('/approvals')}
                w="full"
              >
                View All Approvals
              </Button>
            </VStack>
          )}
        </VStack>
      </Box>
    )
  }

  // Requester View
  if (role === 'requester') {
    const myActiveRequests = requests.filter(
      (r) => !['completed', 'cancelled', 'contracted'].includes(r.status)
    )

    return (
      <Box
        borderWidth="1px"
        borderColor="var(--core-color-border-default)"
        borderRadius="lg"
        bg="var(--core-color-surface-canvas)"
        p={6}
      >
        <VStack align="stretch" gap={4}>
          <HStack justify="space-between">
            <Box>
              <Text fontSize="md" fontWeight="semibold" color="var(--core-color-text-primary)">
                My Active Requests
              </Text>
              <Text fontSize="sm" color="var(--core-color-text-muted)" mt={1}>
                Track your procurement requests
              </Text>
            </Box>
            <Badge
              fontSize="md"
              px={3}
              py={1}
              borderRadius="md"
              bg="var(--core-color-brand-bg)"
              color="var(--core-color-brand-primary)"
            >
              {myActiveRequests.length}
            </Badge>
          </HStack>

          {myActiveRequests.length === 0 ? (
            <Box
              p={4}
              textAlign="center"
              borderRadius="md"
              bg="var(--core-color-surface-subtle)"
            >
              <AlertCircle className="h-8 w-8 mx-auto mb-2" style={{ color: 'var(--core-color-text-muted)' }} />
              <Text fontSize="sm" color="var(--core-color-text-muted)" mb={3}>
                No active requests
              </Text>
              <Button size="sm" colorScheme="blue" onClick={() => navigate('/requests/new')}>
                Create New Request
              </Button>
            </Box>
          ) : (
            <VStack align="stretch" gap={3}>
              {myActiveRequests.slice(0, 3).map((request) => (
                <Box
                  key={request.request_id}
                  p={4}
                  borderRadius="md"
                  bg="var(--core-color-surface-subtle)"
                  borderWidth="1px"
                  borderColor="var(--core-color-border-subtle)"
                  cursor="pointer"
                  onClick={() => navigate(`/requests/${request.request_id}/negotiate`)}
                  _hover={{
                    borderColor: 'var(--core-color-border-default)',
                    boxShadow: 'sm',
                  }}
                  transition="all 0.2s"
                >
                  <VStack align="stretch" gap={2}>
                    <HStack justify="space-between">
                      <Text
                        fontSize="sm"
                        fontWeight="medium"
                        color="var(--core-color-text-primary)"
                        flex="1"
                        overflow="hidden"
                        textOverflow="ellipsis"
                        whiteSpace="nowrap"
                      >
                        {request.description}
                      </Text>
                      <StatusBadge status={request.status} size="sm" />
                    </HStack>
                    {request.budget_max && (
                      <Text fontSize="xs" color="var(--core-color-text-muted)">
                        Budget: ${request.budget_max.toLocaleString()}
                      </Text>
                    )}
                  </VStack>
                </Box>
              ))}
              <Button
                size="sm"
                variant="outline"
                onClick={() => navigate('/requests')}
                w="full"
              >
                View All Requests
              </Button>
            </VStack>
          )}
        </VStack>
      </Box>
    )
  }

  // Default buyer view - can show quick stats
  return (
    <Box
      borderWidth="1px"
      borderColor="var(--core-color-border-default)"
      borderRadius="lg"
      bg="var(--core-color-surface-canvas)"
      p={6}
    >
      <Text fontSize="md" fontWeight="semibold" color="var(--core-color-text-primary)">
        Quick Actions
      </Text>
      <VStack align="stretch" gap={2} mt={4}>
        <Button
          size="sm"
          variant="outline"
          onClick={() => navigate('/requests/new')}
          w="full"
          justifyContent="start"
        >
          Create New Request
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => navigate('/portfolio')}
          w="full"
          justifyContent="start"
        >
          View Portfolio
        </Button>
      </VStack>
    </Box>
  )
}
