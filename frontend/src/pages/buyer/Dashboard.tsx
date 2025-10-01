import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import { api } from '../../services/api'
import { MetricCard } from '../../components/shared/MetricCard'
import { SmartAlert } from '../../components/shared/SmartAlert'
import { StageBoard, type StageBoardColumn } from '../../components/shared/StageBoard'
import type { Request, RequestStatus } from '../../types'

const PIPELINE_ORDER: Array<{ id: RequestStatus; label: string; tone?: StageBoardColumn['tone'] }> = [
  { id: 'draft', label: 'Draft', tone: 'neutral' },
  { id: 'sourcing', label: 'Sourcing', tone: 'buyer' },
  { id: 'negotiating', label: 'Negotiating', tone: 'brand' },
  { id: 'approving', label: 'Approving', tone: 'brand' },
  { id: 'contracted', label: 'Contracted', tone: 'buyer' },
]

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

  const requestsByStatus = useMemo(() => {
    return (requests ?? []).reduce<Record<RequestStatus, Request[]>>((acc, request) => {
      const status = request.status
      if (!acc[status]) acc[status] = []
      acc[status].push(request)
      return acc
    }, {
      draft: [],
      intake: [],
      sourcing: [],
      negotiating: [],
      approving: [],
      contracted: [],
      provisioning: [],
      completed: [],
      cancelled: [],
    })
  }, [requests])

  const pipelineColumns: StageBoardColumn[] = useMemo(() => {
    return PIPELINE_ORDER.map(({ id, label, tone }) => {
      const items = (requestsByStatus[id] ?? []).slice(0, 6).map((request) => ({
        id: request.request_id,
        title: request.description,
        subtitle: `${request.quantity} units • ${request.type.toUpperCase() || 'UNKNOWN'}`,
        status: request.status,
        budgetLabel: request.budget_max
          ? new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: request.currency || 'USD',
            notation: 'compact',
          }).format(request.budget_max)
          : undefined,
        timeInStage: request.updated_at
          ? `${formatDistanceToNow(new Date(request.updated_at), { addSuffix: true })}`
          : undefined,
        metadata: request.must_haves?.length
          ? [
              {
                label: 'Must-haves',
                value: `${request.must_haves.length}`,
              },
            ]
          : undefined,
        onSelect: () => navigate(`/requests/${request.request_id}/negotiate`),
      }))

      return {
        id,
        title: label,
        tone,
        count: requestsByStatus[id]?.length ?? 0,
        items,
      }
    })
  }, [navigate, requestsByStatus])

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--core-color-text-primary)]">Buyer Dashboard</h1>
          <p className="text-sm text-[var(--core-color-text-muted)]">
            Monitor sourcing velocity, approvals, and AI-driven negotiation progress.
          </p>
        </div>
        <button
          onClick={() => navigate('/requests/new')}
          className="inline-flex items-center gap-2 rounded-lg bg-[var(--core-color-brand-primary)] px-4 py-2 text-sm font-semibold text-white shadow-100 transition hover:bg-[var(--core-color-brand-primary)]/90"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Request
        </button>
      </header>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Active Requests"
          value={metrics?.active_requests ?? 0}
          subtitle="Across all stages"
          onClick={() => navigate('/requests')}
        />
        <MetricCard
          title="Pending Approvals"
          value={metrics?.pending_approvals ?? approvals?.length ?? 0}
          subtitle="Requires your decision"
          onClick={() => navigate('/approvals')}
        />
        <MetricCard
          title="Upcoming Renewals"
          value={metrics?.upcoming_renewals ?? renewals?.length ?? 0}
          subtitle="Next 60 days"
          onClick={() => navigate('/portfolio')}
        />
        <MetricCard
          title="Avg Savings vs Market"
          value={`${savingsPercent.toFixed(1)}%`}
          subtitle="Powered by AI negotiation"
          trend={{ value: Math.abs(savingsPercent), direction: savingsDirection }}
        />
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

      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold text-[var(--core-color-text-primary)]">Request pipeline</h2>
          <p className="text-sm text-[var(--core-color-text-muted)]">
            Track every request from intake through contracting. Columns update in real-time as AI agents progress negotiations.
          </p>
        </div>
        <StageBoard columns={pipelineColumns} emptyLabel="No items in this stage" />
      </section>
    </div>
  )
}
