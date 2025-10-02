import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
// import { formatDistanceToNow } from 'date-fns'
// Minimal dashboard: avoid heavy icons/stats
import { api } from '../../services/api'
import { SmartAlert } from '../../components/shared/SmartAlert'
import { HeroInput } from '../../components/buyer/dashboard/HeroInput'
import { ProgressTrackerCard } from '../../components/buyer/dashboard/ProgressTrackerCard'
import { NegotiationStoryboard } from '../../components/buyer/dashboard/NegotiationStoryboard'
// import { DecisionGate } from '../../components/buyer/dashboard/DecisionGate'
// import type { Request, RequestStatus } from '../../types'


export function BuyerDashboard (): JSX.Element {
  const navigate = useNavigate()

  const { data: metrics } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: () => api.getDashboardMetrics(),
  })

  const { data: requests } = useQuery({
    queryKey: ['requests'],
    queryFn: () => api.getRequests(),
  })

  const { data: renewals } = useQuery({
    queryKey: ['renewals'],
    queryFn: () => api.getUpcomingRenewals(60),
  })

  const { data: approvals } = useQuery({
    queryKey: ['pending-approvals'],
    queryFn: () => api.getPendingApprovals(),
  })

  const savingsPercent = (metrics as any)?.savings_percentage ?? (metrics as any)?.avg_savings_percent ?? 0
  const savingsDirection: 'up' | 'down' | 'neutral' = savingsPercent > 0 ? 'up' : savingsPercent < 0 ? 'down' : 'neutral'

  // Legacy StageBoard removed in favor of progress tracker cards

  // Mock negotiation messages for demo
  const mockMessages = useMemo(() => [
    {
      id: '1',
      sender: 'agent' as const,
      content: 'Offered $920/seat with 12-month term',
      timestamp: '2m ago',
      metadata: { price: '$920/seat', term: '12 months', payment: 'NET30' },
    },
    {
      id: '2',
      sender: 'vendor' as const,
      content: 'Counter at $950/seat, can do NET15 payment',
      timestamp: '1m ago',
      metadata: { price: '$950/seat', payment: 'NET15' },
    },
    {
      id: '3',
      sender: 'agent' as const,
      content: 'Accepted NET15, requesting $930/seat final',
      timestamp: 'Just now',
      metadata: { price: '$930/seat', payment: 'NET15' },
    },
  ], [])

  // Consolidate duplicates and prioritize most active/recent
  const topActiveRequests = useMemo(() => {
    const list: any[] = Array.isArray(requests) ? requests : []
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
    const byKey = new Map<string, any>()
    for (const r of list) {
      const key = `${(r?.description ?? '').toLowerCase().trim()}|${r?.type ?? ''}`
      const ts = new Date(r?.updated_at ?? r?.created_at ?? Date.now()).getTime()
      const score = (weight[r?.status] ?? 0) * 1e12 + ts
      const prev = byKey.get(key)
      if (!prev || score > prev.__score) {
        byKey.set(key, { ...r, __score: score })
      }
    }
    const deduped = Array.from(byKey.values()).sort((a, b) => b.__score - a.__score)
    return deduped.slice(0, 3)
  }, [requests])

  const activeCount = useMemo(() => (Array.isArray(requests) ? requests.filter((r: any) => !['completed', 'cancelled', 'contracted'].includes(r?.status)).length : 0), [requests])
  const approvalsCount = useMemo(() => (Array.isArray(requests) ? requests.filter((r: any) => r?.status === 'approving').length : 0), [requests])

  return (
    <div className="space-y-8">
      {/* Hero Input */}
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold text-[var(--core-color-text-primary)]">Describe a need</h1>
        <HeroInput />
      </div>

      {/* Minimal KPI strip (3 metrics, simplified labels) */}
      <section className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-[var(--core-color-text-secondary)]">Active</p>
          <p className="mt-1 text-2xl font-bold text-[var(--core-color-text-primary)]">{activeCount || '—'}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-[var(--core-color-text-secondary)]">Approvals</p>
          <p className="mt-1 text-2xl font-bold text-[var(--core-color-text-primary)]">{approvalsCount || '—'}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-[var(--core-color-text-secondary)]">Avg. savings</p>
          <p className="mt-1 text-2xl font-bold text-[var(--core-color-text-primary)]">{savingsPercent ? `${savingsPercent.toFixed(1)}%` : '—'}</p>
        </div>
      </section>

      <section className="space-y-4">
        {renewals && renewals.length > 0 && (
          <SmartAlert
            severity="warning"
            title="Renewals approaching"
            message={`${renewals.length} subscriptions up for renewal.`}
            emphasis={`Potential savings ~$${renewals.reduce((sum, item) => sum + (item.potential_savings ?? 0), 0).toLocaleString()}`}
            actionLabel="Review portfolio"
            onAction={() => navigate('/portfolio')}
          />
        )}

        {approvals && approvals.length > 0 && (
          <SmartAlert
            severity="info"
            title="Decisions awaiting you"
            message={`${approvals.length} offers are ready for approval with full AI rationale.`}
            actionLabel="Open approval workspace"
            onAction={() => navigate('/approvals')}
            compact
          />
        )}
      </section>

      {/* Active Requests Timeline */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-[var(--core-color-text-primary)]">{activeCount ? `${Math.min(activeCount, 3)} active requests` : 'No active requests'}</h2>
          <button
            onClick={() => navigate('/requests')}
            className="text-sm text-[var(--color-ai-primary)] hover:underline"
          >
            View all
          </button>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          {topActiveRequests.map((request: any) => (
            <ProgressTrackerCard
              key={request.request_id}
              title={request.description}
              vendor={request.type}
              stage={request.status as any}
              nextAction={request.status === 'negotiating' ? 'Negotiating · Round 2' : request.status === 'approving' ? 'Awaiting approval' : undefined}
              preview={request.status === 'negotiating' ? 'Agent offered $930 · vendor counter pending' : undefined}
              budget={request.budget_max ? `$${request.budget_max.toLocaleString()}` : undefined}
              isActive={request.status === 'negotiating'}
              onClick={() => navigate(`/requests/${request.request_id}/negotiate`)}
            />
          ))}
        </div>
      </section>

      {/* Live Negotiation Feed */}
      {requests && requests.some(r => r.status === 'negotiating') && (
        <section className="space-y-4">
          <div>
            <h2 className="text-lg font-semibold text-[var(--core-color-text-primary)]">Live negotiation</h2>
            <p className="text-sm text-[var(--core-color-text-muted)]">Watch your agent negotiate in real-time</p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <NegotiationStoryboard messages={mockMessages} vendorName="Figma" />
            <div className="mt-4">
              <button
                type="button"
                className="inline-flex items-center gap-2 rounded-sm border border-[var(--accent-mint)] bg-white px-3 py-1.5 text-sm font-medium text-[var(--core-color-text-primary)] hover:bg-[var(--accent-mint)]/30"
              >
                Ask agent for one more round
              </button>
            </div>
          </div>
        </section>
      )}
      {/* Decision Gate removed from default view to reduce layers */}
    </div>
  )
}
