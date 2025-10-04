import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import { Box, Heading, Text, SimpleGrid, Button as CButton, Spinner } from '@chakra-ui/react'
import { api } from '../../services/api'
import { SmartAlert } from '../../components/shared/SmartAlert'
import { HeroInput } from '../../components/buyer/dashboard/HeroInput'
import { ProgressTrackerCard } from '../../components/buyer/dashboard/ProgressTrackerCard'
import type { Request, DashboardMetrics } from '../../types'

export function BuyerDashboard(): JSX.Element {
  const navigate = useNavigate()

  const {
    data: metrics,
    isLoading: metricsLoading,
    error: metricsError,
  } = useQuery<DashboardMetrics>({
    queryKey: ['dashboard-metrics'],
    queryFn: async () => await api.getDashboardMetrics(),
    retry: false,
  })

  const {
    data: requests,
    isLoading: requestsLoading,
    error: requestsError,
  } = useQuery<Request[]>({
    queryKey: ['requests'],
    queryFn: async () => await api.getRequests(),
    retry: false,
  })

  const { data: renewals } = useQuery<any[]>({
    queryKey: ['renewals'],
    queryFn: async () => await api.getUpcomingRenewals(60),
    retry: false,
  })

  const { data: approvals } = useQuery<any[]>({
    queryKey: ['pending-approvals'],
    queryFn: async () => await api.getPendingApprovals(),
    retry: false,
  })

  const isLoading = metricsLoading || requestsLoading
  const loadError = (metricsError as Error | undefined) ?? (requestsError as Error | undefined)

  const savingsPercent = metrics?.avg_savings_percent ?? 0

  const topActiveRequests = useMemo(() => {
    const list: Request[] = Array.isArray(requests) ? requests : []
    const weight: Record<string, number> = {
      negotiating: 5,
      approving: 4,
      sourcing: 3,
      intake: 2,
      draft: 1,
      provisioning: 1,
      contracted: 0,
      completed: 0,
      cancelled: 0,
    }
    const byKey = new Map<string, Request & { __score: number }>()
    for (const r of list) {
      const key = `${(r.description ?? '').toLowerCase().trim()}|${r.type ?? ''}`
      const ts = new Date(r.updated_at ?? r.created_at ?? Date.now()).getTime()
      const score = (weight[r.status] ?? 0) * 1e12 + ts
      const prev = byKey.get(key)
      if (!prev || score > prev.__score) {
        byKey.set(key, { ...r, __score: score })
      }
    }
    const deduped = Array.from(byKey.values()).sort(
      (a, b) => b.__score - a.__score
    )
    return deduped.slice(0, 3)
  }, [requests])

  const activeCount = useMemo(
    () =>
      Array.isArray(requests)
        ? requests.filter(
            (r) => !['completed', 'cancelled', 'contracted'].includes(r.status)
          ).length
        : 0,
    [requests]
  )

  const approvalsCount = useMemo(
    () => (approvals ? approvals.length : 0),
    [approvals]
  )

  return (
    <Box maxW="1180px" mx="auto" px={{ base: 4, sm: 6 }} py={0}>
      {/* Heading */}
      <Box mb={8}>
        <Heading as="h1" size="xl" fontWeight="thin" color="gray.900" _dark={{ color: '#FAFAFA' }}>
          Dashboard
        </Heading>
      </Box>

      {/* Hero input */}
      <HeroInput />

      {/* Loading / Error states */}
      <Box my={6}>
        {isLoading && (
          <Box display="flex" alignItems="center" justifyContent="center" py={10}>
            <Spinner color="gray.700" _dark={{ color: '#A1A1AA' }} />
            <Text ml={3} color="gray.600" _dark={{ color: '#A1A1AA' }}>
              Loading dashboard...
            </Text>
          </Box>
        )}
        {!isLoading && loadError && (
          <Box display="flex" gap={3} alignItems="flex-start" bg="gray.50" borderColor="gray.200" borderWidth="1px" p={4} _dark={{ bg: '#0A0A0A', borderColor: '#262626' }}>
            <Box boxSize={3} mt={1.5} bg="gray.800" _dark={{ bg: '#A1A1AA' }} borderRadius="full" aria-hidden="true" />
            <Box>
              <Text fontWeight="semibold" color="gray.900" _dark={{ color: '#FAFAFA' }}>Failed to load dashboard</Text>
              <Text mt={1} fontSize="sm" color="gray.600" _dark={{ color: '#A1A1AA' }}>
                {loadError.message || 'Unable to connect to the backend. Please ensure the API server is running.'}
              </Text>
              <CButton mt={3} size="sm" onClick={() => window.location.reload()} variant="outline" colorScheme="gray">
                Retry
              </CButton>
            </Box>
          </Box>
        )}
      </Box>

      {/* Content */}
      {!isLoading && !loadError && (
        <>
          {/* Overview */}
          <Box my={6}>
            <Heading as="h2" size="sm" color="gray.900" _dark={{ color: '#FAFAFA' }} mb={3}>
              Overview
            </Heading>
            <SimpleGrid columns={{ base: 1, sm: 3 }} gap={6}>
              <Box borderWidth="1px" borderColor="gray.200" bg="white" p={4} _dark={{ bg: '#0F0F0F', borderColor: '#262626' }}>
                <Text fontSize="xs" color="gray.600" _dark={{ color: '#A1A1AA' }}>Active</Text>
                <Heading as="p" size="lg" mt={1} color="gray.900" _dark={{ color: '#FAFAFA' }}>{activeCount || '—'}</Heading>
              </Box>
              <Box borderWidth="1px" borderColor="gray.200" bg="white" p={4} _dark={{ bg: '#0F0F0F', borderColor: '#262626' }}>
                <Text fontSize="xs" color="gray.600" _dark={{ color: '#A1A1AA' }}>Approvals</Text>
                <Heading as="p" size="lg" mt={1} color="gray.900" _dark={{ color: '#FAFAFA' }}>{approvalsCount || '—'}</Heading>
              </Box>
              <Box borderWidth="1px" borderColor="gray.200" bg="white" p={4} _dark={{ bg: '#0F0F0F', borderColor: '#262626' }}>
                <Text fontSize="xs" color="gray.600" _dark={{ color: '#A1A1AA' }}>Avg. savings</Text>
                <Heading as="p" size="lg" mt={1} color="gray.900" _dark={{ color: '#FAFAFA' }}>{savingsPercent ? `${savingsPercent.toFixed(1)}%` : '—'}</Heading>
              </Box>
            </SimpleGrid>
          </Box>

          {/* Recent activity */}
          <Box my={6}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Heading as="h2" size="sm" color="gray.900" _dark={{ color: '#FAFAFA' }}>
                Recent activity
              </Heading>
              <CButton onClick={() => void navigate('/requests')} size="sm" variant="plain" colorPalette="gray" _hover={{ textDecoration: 'underline' }}>
                View all
              </CButton>
            </Box>
            <Box mt={2} borderWidth="1px" borderColor="gray.200" bg="white" _dark={{ bg: '#0F0F0F', borderColor: '#262626' }}>
              <Box display="grid" gridTemplateColumns="5fr 3fr 2fr 2fr" borderBottomWidth="1px" borderColor="gray.200" px={3} py={2} fontSize="xs" color="gray.600" _dark={{ borderColor: '#262626', color: '#A1A1AA' }}>
                <Box>Name</Box>
                <Box>Stage</Box>
                <Box>Budget</Box>
                <Box textAlign="right">Updated</Box>
              </Box>
              <Box>
                {(Array.isArray(requests) ? [...requests] : [])
                  .sort((a, b) => new Date(b.updated_at ?? b.created_at ?? 0).getTime() - new Date(a.updated_at ?? a.created_at ?? 0).getTime())
                  .slice(0, 6)
                  .map((r) => (
                    <Box
                      as="button"
                      key={r.request_id}
                      onClick={() => void navigate(`/requests/${r.request_id}/negotiate`)}
                      display="grid"
                      gridTemplateColumns="5fr 3fr 2fr 2fr"
                      w="full"
                      textAlign="left"
                      px={3}
                      py={2}
                      _hover={{ bg: 'gray.50', _dark: { bg: '#1A1A1A' } }}
                    >
                      <Text truncate fontSize="sm" color="gray.900" _dark={{ color: '#FAFAFA' }}>{r.description}</Text>
                      <Text fontSize="xs" color="gray.600" _dark={{ color: '#A1A1AA' }}>{r.status}</Text>
                      <Text fontSize="xs" color="gray.600" _dark={{ color: '#A1A1AA' }}>{r.budget_max ? `$${r.budget_max.toLocaleString()}` : '—'}</Text>
                      <Text fontSize="xs" color="gray.600" _dark={{ color: '#A1A1AA' }} textAlign="right">
                        {formatDistanceToNow(new Date(r.updated_at ?? r.created_at ?? Date.now()), { addSuffix: true })}
                      </Text>
                    </Box>
                  ))}
              </Box>
            </Box>
          </Box>

          {/* Alerts */}
          <Box my={6}>
            {renewals && renewals.length > 0 && (
              <SmartAlert
                severity="warning"
                title="Renewals approaching"
                message={`${renewals.length} subscriptions up for renewal.`}
                emphasis={`Potential savings ~$${renewals.reduce((sum, item) => sum + (item.potential_savings ?? 0), 0).toLocaleString()}`}
                actionLabel="Review portfolio"
                onAction={() => void navigate('/portfolio')}
              />
            )}

            {approvals && approvals.length > 0 && (
              <SmartAlert
                severity="info"
                title="Decisions awaiting you"
                message={`${approvals.length} offers are ready for approval with full AI rationale.`}
                actionLabel="Open approval workspace"
                onAction={() => void navigate('/approvals')}
                compact
              />
            )}
          </Box>

          {/* Active requests */}
          <Box my={6}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Heading as="h2" size="md" color="gray.900" _dark={{ color: '#FAFAFA' }}>
                {activeCount ? `${Math.min(activeCount, 3)} active requests` : 'No active requests'}
              </Heading>
              <CButton onClick={() => void navigate('/requests')} size="sm" variant="plain" colorPalette="gray" _hover={{ textDecoration: 'underline' }}>
                View all
              </CButton>
            </Box>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={6} mt={2}>
              {topActiveRequests.map((request) => (
                <ProgressTrackerCard
                  key={request.request_id}
                  title={request.description}
                  vendor={request.type}
                  stage={request.status as any}
                  nextAction={
                    request.status === 'negotiating'
                      ? 'Negotiating · Round 2'
                      : request.status === 'approving'
                        ? 'Awaiting approval'
                        : undefined
                  }
                  preview={request.status === 'negotiating' ? 'Agent offered $930 · vendor counter pending' : undefined}
                  budget={request.budget_max ? `$${request.budget_max.toLocaleString()}` : undefined}
                  isActive={request.status === 'negotiating'}
                  onClick={() => void navigate(`/requests/${request.request_id}/negotiate`)}
                />
              ))}
            </SimpleGrid>
          </Box>
        </>
      )}
    </Box>
  )
}
