import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import { Box, Heading, Text, SimpleGrid, Button as CButton, Spinner } from '@chakra-ui/react'
import { StatCard } from '../../components/ui/StatCard'
import { SurfaceCard } from '../../components/ui/SurfaceCard'
import { api } from '../../services/api'
import { SmartAlert } from '../../components/shared/SmartAlert'
import { Tooltip } from '../../components/shared/Tooltip'
import { HeroInput } from '../../components/buyer/dashboard/HeroInput'
import { BreathingNumber } from '../../components/ui/BreathingNumber'
import { OverviewCards } from '../../components/ui/OverviewCards'
import { ProgressTrackerCard } from '../../components/buyer/dashboard/ProgressTrackerCard'
import type { Request, DashboardMetrics } from '../../types'
import { useAuthStore } from '../../store/auth'

export function BuyerDashboard(): JSX.Element {
  const navigate = useNavigate()
  const { user } = useAuthStore()

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

  // Count repeated activity entries by normalized key for subtle repetition chip (×n)
  const activityCounts = useMemo(() => {
    const list: Request[] = Array.isArray(requests) ? requests : []
    const map = new Map<string, number>()
    for (const r of list) {
      const key = `${(r.description ?? '').toLowerCase().trim()}|${(r.type ?? '').toLowerCase().trim()}`
      map.set(key, (map.get(key) ?? 0) + 1)
    }
    return map
  }, [requests])

  return (
    <Box maxW="1180px" mx="auto" px={{ base: 4, sm: 6 }} py={0}>
      {/* Heading */}
      <Box mb={8}>
        <Heading as="h1" size="xl" fontWeight="thin" color="fg">
          Dashboard
        </Heading>
      </Box>

      {/* Hero input */}
      <HeroInput />

      {/* Loading / Error states */}
      <Box my={6}>
        {isLoading && (
          <Box display="flex" alignItems="center" justifyContent="center" py={10}>
            <Spinner color="fg.muted" />
            <Text ml={3} color="fg.muted">
              Loading dashboard...
            </Text>
          </Box>
        )}
        {!isLoading && loadError && (
          <Box display="flex" gap={3} alignItems="flex-start" bg="bg.subtle" borderColor="border" borderWidth="1px" p={4}>
            <Box boxSize={3} mt={1.5} bg="fg.muted" borderRadius="full" aria-hidden="true" />
            <Box>
              <Text fontWeight="semibold" color="fg">Failed to load dashboard</Text>
              <Text mt={1} fontSize="sm" color="fg.muted">
                {loadError.message || 'Unable to connect to the backend. Please ensure the API server is running.'}
              </Text>
              <CButton mt={3} size="sm" onClick={() => window.location.reload()} variant="outline" colorPalette="gray">
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
            <OverviewCards
              income={(metrics as any)?.income_total ?? null}
              paid={(metrics as any)?.paid_total ?? null}
              active={<BreathingNumber base={activeCount || 0} amplitude={2} periodMs={2400} />}
              avatarName={user?.full_name ?? user?.username}
            />
          </Box>

          {/* Recent activity */}
          <SurfaceCard
            title="Recent activity"
            actions={(
              <CButton onClick={() => void navigate('/requests')} size="sm" variant="plain" colorPalette="gray" _hover={{ textDecoration: 'underline' }}>
                View all
              </CButton>
            )}
            my={6}
          >
            <Box borderWidth="1px" borderColor="border" bg="bg.panel">
              <Box display="grid" gridTemplateColumns={{ base: 'minmax(0, 1fr) 120px 120px 140px', md: 'minmax(0, 1fr) 180px 140px 160px' }} borderBottomWidth="1px" borderColor="border" px={3} py={2} fontSize="xs" color="fg.muted">
                <Box>Name</Box>
                <Box>Stage</Box>
                <Box>Budget</Box>
                <Box textAlign="right">Updated</Box>
              </Box>
              <Box>
                {(Array.isArray(requests) ? [...requests] : [])
                  .sort((a, b) => new Date(b.updated_at ?? b.created_at ?? 0).getTime() - new Date(a.updated_at ?? a.created_at ?? 0).getTime())
                  .slice(0, 6)
                  .map((r, idx) => {
                    const key = `${(r.description ?? '').toLowerCase().trim()}|${(r.type ?? '').toLowerCase().trim()}`
                    const repeatCount = activityCounts.get(key) ?? 1
                    return (
                      <Box
                        as="button"
                        key={r.request_id}
                        onClick={() => void navigate(`/requests/${r.request_id}/negotiate`)}
                        display="grid"
                        gridTemplateColumns={{ base: 'minmax(0, 1fr) 120px 120px 140px', md: 'minmax(0, 1fr) 180px 140px 160px' }}
                        alignItems="center"
                        w="full"
                        textAlign="left"
                        px={3}
                        py={3}
                        borderTopWidth={idx === 0 ? '0' : '1px'}
                        borderColor="border"
                        _hover={{ bg: 'bg.subtle' }}
                      >
                        {/* Name with optional repetition chip */}
                        <Box display="flex" alignItems="center" minW={0} overflow="hidden" gap={2} pr={3}>
                          <Tooltip content={r.description} wrapperProps={{ display: 'block', flex: 1, minW: 0, maxW: '100%', overflow: 'hidden' }}>
                            <Text as="span" display="block" width="100%" overflow="hidden" textOverflow="ellipsis" whiteSpace="nowrap" fontSize="sm" color="fg">
                              {r.description}
                            </Text>
                          </Tooltip>
                          {repeatCount > 1 && (
                            <Box as="span" px={1.5} py={0.5} fontSize="xs" opacity={0.9} color="fg.muted" bg="bg.subtle" borderWidth="1px" borderColor="border" borderRadius="sm">
                              ×{repeatCount}
                            </Box>
                          )}
                        </Box>

                        {/* Stage as a soft badge */}
                        <Box as="span" justifySelf="start" px={2} py={0.5} fontSize="xs" opacity={0.9} color="fg.muted" bg="bg.subtle" borderWidth="1px" borderColor="border" borderRadius="sm">
                          {r.status}
                        </Box>

                        {/* Budget */}
                        <Text fontSize="xs" color="fg.muted">{r.budget_max ? `$${r.budget_max.toLocaleString()}` : '—'}</Text>

                        {/* Updated time + Open action badge aligned right */}
                        <Box display="flex" alignItems="center" gap={2} justifyContent="flex-end">
                          <Box as="span" px={2} py={0.5} fontSize="xs" opacity={0.9} color="fg.muted" bg="bg.subtle" borderWidth="1px" borderColor="border" borderRadius="sm">
                            Open
                          </Box>
                          <Text fontSize="xs" color="fg.muted" opacity={0.75} textAlign="right">
                            {formatDistanceToNow(new Date(r.updated_at ?? r.created_at ?? Date.now()), { addSuffix: true })}
                          </Text>
                        </Box>
                      </Box>
                    )
                  })}
              </Box>
            </Box>
          </SurfaceCard>

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
          <SurfaceCard
            title={activeCount ? `${Math.min(activeCount, 3)} active requests` : 'No active requests'}
            actions={(
              <CButton onClick={() => void navigate('/requests')} size="sm" variant="plain" colorPalette="gray" _hover={{ textDecoration: 'underline' }}>
                View all
              </CButton>
            )}
            my={6}
          >
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
          </SurfaceCard>
        </>
      )}
    </Box>
  )
}
