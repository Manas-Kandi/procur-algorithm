import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import { api } from '../../services/api'
import { SmartAlert } from '../../components/shared/SmartAlert'
import { HeroInput } from '../../components/buyer/dashboard/HeroInput'
import { ProgressTrackerCard } from '../../components/buyer/dashboard/ProgressTrackerCard'
import type { Request, DashboardMetrics } from '../../types'

export function BuyerDashboard(): JSX.Element {
  const navigate = useNavigate()

  const { data: metrics } = useQuery<DashboardMetrics>({
    queryKey: ['dashboard-metrics'],
    queryFn: async () => await api.getDashboardMetrics(),
  })

  const { data: requests } = useQuery<Request[]>({
    queryKey: ['requests'],
    queryFn: async () => await api.getRequests(),
  })

  const { data: renewals } = useQuery<any[]>({
    queryKey: ['renewals'],
    queryFn: async () => await api.getUpcomingRenewals(60),
  })

  const { data: approvals } = useQuery<any[]>({
    queryKey: ['pending-approvals'],
    queryFn: async () => await api.getPendingApprovals(),
  })

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
    <div className="mx-auto max-w-[1180px] space-y-8 px-4 sm:px-6">
      <div>
        <h1 className="text-3xl font-thin text-[var(--core-color-text-primary)]">
          Dashboard
        </h1>
      </div>

      <HeroInput />

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-[var(--core-color-text-primary)]">
            Overview
          </h2>
        </div>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          <div className="border border-gray-200 bg-white/50 p-4">
            <p className="text-xs text-[var(--core-color-text-secondary)]">
              Active
            </p>
            <p className="mt-1 text-2xl font-bold text-[var(--core-color-text-primary)]">
              {activeCount || '—'}
            </p>
          </div>
          <div className="border border-gray-200 bg-white/50 p-4">
            <p className="text-xs text-[var(--core-color-text-secondary)]">
              Approvals
            </p>
            <p className="mt-1 text-2xl font-bold text-[var(--core-color-text-primary)]">
              {approvalsCount || '—'}
            </p>
          </div>
          <div className="border border-gray-200 bg-white/50 p-4">
            <p className="text-xs text-[var(--core-color-text-secondary)]">
              Avg. savings
            </p>
            <p className="mt-1 text-2xl font-bold text-[var(--core-color-text-primary)]">
              {savingsPercent ? `${savingsPercent.toFixed(1)}%` : '—'}
            </p>
            <svg width="100%" height="28" viewBox="0 0 200 28" className="mt-1">
              <path
                d="M0 20 L20 18 L40 22 L60 14 L80 16 L100 10 L120 12 L140 8 L160 14 L180 12 L200 6"
                stroke="var(--agent-accent)"
                strokeWidth="2.5"
                fill="none"
              />
              <path
                d="M0 28 L0 20 L200 6 L200 28 Z"
                fill="var(--agent-accent-soft)"
              />
            </svg>
          </div>
        </div>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-[var(--core-color-text-primary)]">
            Recent activity
          </h2>
          <button
            onClick={() => {
              void navigate('/requests')
            }}
            className="text-sm text-[var(--agent-accent)] hover:underline"
          >
            View all
          </button>
        </div>
        <div className="border border-[var(--muted-2)] bg-white">
          <div className="grid grid-cols-12 border-b border-[var(--muted-2)] px-3 py-2 text-xs text-[var(--core-color-text-secondary)]">
            <div className="col-span-5">Name</div>
            <div className="col-span-3">Stage</div>
            <div className="col-span-2">Budget</div>
            <div className="col-span-2 text-right">Updated</div>
          </div>
          <div className="divide-y divide-[var(--muted-2)]">
            {(Array.isArray(requests) ? [...requests] : [])
              .sort(
                (a, b) =>
                  new Date(b.updated_at ?? b.created_at ?? 0).getTime() -
                  new Date(a.updated_at ?? a.created_at ?? 0).getTime()
              )
              .slice(0, 6)
              .map((r) => (
                <button
                  key={r.request_id}
                  onClick={() => {
                    void navigate(`/requests/${r.request_id}/negotiate`)
                  }}
                  className="grid w-full grid-cols-12 items-center px-3 py-2 text-left hover:bg-[var(--muted-1)]"
                >
                  <div className="col-span-5 truncate text-sm text-[var(--core-color-text-primary)]">
                    {r.description}
                  </div>
                  <div className="col-span-3 text-xs text-[var(--core-color-text-secondary)]">
                    {r.status}
                  </div>
                  <div className="col-span-2 text-xs text-[var(--core-color-text-secondary)]">
                    {r.budget_max ? `$${r.budget_max.toLocaleString()}` : '—'}
                  </div>
                  <div className="col-span-2 text-right text-xs text-[var(--core-color-text-secondary)]">
                    {formatDistanceToNow(
                      new Date(r.updated_at ?? r.created_at ?? Date.now()),
                      { addSuffix: true }
                    )}
                  </div>
                </button>
              ))}
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
            onAction={() => {
              void navigate('/portfolio')
            }}
          />
        )}

        {approvals && approvals.length > 0 && (
          <SmartAlert
            severity="info"
            title="Decisions awaiting you"
            message={`${approvals.length} offers are ready for approval with full AI rationale.`}
            actionLabel="Open approval workspace"
            onAction={() => {
              void navigate('/approvals')
            }}
            compact
          />
        )}
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-[var(--core-color-text-primary)]">
            {activeCount
              ? `${Math.min(activeCount, 3)} active requests`
              : 'No active requests'}
          </h2>
          <button
            onClick={() => {
              void navigate('/requests')
            }}
            className="text-sm text-[var(--agent-accent)] hover:underline"
          >
            View all
          </button>
        </div>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {topActiveRequests.map((request) => (
            <ProgressTrackerCard
              key={request.request_id}
              title={request.description}
              vendor={request.type}
              stage={request.status as any} // Status from DB might not match StageKey
              nextAction={
                request.status === 'negotiating'
                  ? 'Negotiating · Round 2'
                  : request.status === 'approving'
                    ? 'Awaiting approval'
                    : undefined
              }
              preview={
                request.status === 'negotiating'
                  ? 'Agent offered $930 · vendor counter pending'
                  : undefined
              }
              budget={
                request.budget_max
                  ? `$${request.budget_max.toLocaleString()}`
                  : undefined
              }
              isActive={request.status === 'negotiating'}
              onClick={() => {
                void navigate(`/requests/${request.request_id}/negotiate`)
              }}
            />
          ))}
        </div>
      </section>
    </div>
  )
}
