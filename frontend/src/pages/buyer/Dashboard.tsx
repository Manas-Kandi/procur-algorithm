import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
// import { formatDistanceToNow } from 'date-fns'
import { TrendingUp, Package, Clock } from 'lucide-react'
import { api } from '../../services/api'
import { SmartAlert } from '../../components/shared/SmartAlert'
import { HeroInput } from '../../components/buyer/dashboard/HeroInput'
import { ProgressTrackerCard } from '../../components/buyer/dashboard/ProgressTrackerCard'
import { NegotiationStoryboard } from '../../components/buyer/dashboard/NegotiationStoryboard'
import { DecisionGate } from '../../components/buyer/dashboard/DecisionGate'
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

  const savingsPercent = metrics?.avg_savings_percent ?? 0
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

  return (
    <div className="space-y-8">
      {/* Hero Input */}
      <div className="space-y-2">
        <h1 className="text-lg font-semibold text-[var(--core-color-text-primary)]">Describe a need</h1>
        <HeroInput />
      </div>

      {/* Quick Stats */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
              <Package className="h-5 w-5" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--core-color-text-primary)]">{metrics?.active_requests ?? 0}</p>
              <p className="text-xs text-[var(--core-color-text-muted)]">Active requests</p>
            </div>
          </div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50 text-amber-600">
              <Clock className="h-5 w-5" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--core-color-text-primary)]">{metrics?.pending_approvals ?? 0}</p>
              <p className="text-xs text-[var(--core-color-text-muted)]">Pending approvals</p>
            </div>
          </div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-50 text-green-600">
              <TrendingUp className="h-5 w-5" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--core-color-text-primary)]">{savingsPercent.toFixed(1)}%</p>
              <p className="text-xs text-[var(--core-color-text-muted)]">Avg savings</p>
            </div>
          </div>
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
          <h2 className="text-lg font-semibold text-[var(--core-color-text-primary)]">Active requests</h2>
          <button
            onClick={() => navigate('/requests')}
            className="text-sm text-[var(--color-ai-primary)] hover:underline"
          >
            View all
          </button>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          {(requests ?? []).slice(0, 6).map((request) => (
            <ProgressTrackerCard
              key={request.request_id}
              title={request.description}
              vendor={request.type}
              stage={request.status as any}
              nextAction={request.status === 'negotiating' ? 'Agent is negotiating, round 2' : undefined}
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
          </div>
        </section>
      )}

      {/* Decision Gate */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-[var(--core-color-text-primary)]">Top picks</h2>
          <span className="text-xs text-[var(--core-color-text-tertiary)]">Agent recommendations</span>
        </div>
        <DecisionGate onSelect={(choice) => {
          // Placeholder: could navigate to a comparison or apply a filter
          if (choice === 'value') {
            // e.g., navigate('/requests?view=best-value')
          }
        }} />
      </section>
    </div>
  )
}
