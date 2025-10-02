import { useMemo } from 'react'
import { MessageSquare, MoreHorizontal } from 'lucide-react'
import clsx from 'clsx'

type StageKey = 'draft' | 'intake' | 'sourcing' | 'negotiating' | 'approving' | 'contracted' | 'provisioning' | 'completed' | 'cancelled'

interface ProgressTrackerCardProps {
  title: string
  vendor?: string
  stage: StageKey
  nextAction?: string
  preview?: string
  budget?: string
  isActive?: boolean
  onClick?: () => void
}

const STAGE_CONFIG: Record<StageKey, { label: string }> = {
  draft: { label: 'Draft' },
  intake: { label: 'Intake' },
  sourcing: { label: 'Sourcing vendors' },
  negotiating: { label: 'Agent negotiating' },
  approving: { label: 'Awaiting approval' },
  contracted: { label: 'Contracted' },
  provisioning: { label: 'Provisioning' },
  completed: { label: 'Completed' },
  cancelled: { label: 'Cancelled' },
}

export function ProgressTrackerCard({
  title,
  vendor,
  stage,
  nextAction,
  preview,
  budget,
  isActive = false,
  onClick,
}: ProgressTrackerCardProps) {
  const config = useMemo(() => {
    return STAGE_CONFIG[stage] ?? { label: 'In progress' }
  }, [stage])

  return (
    <button
      onClick={onClick}
      className={clsx(
        'group relative w-full rounded-[16px] border p-[18px] text-left transition-transform duration-200 bg-[var(--surface)]',
        isActive ? 'border-[var(--agent-accent)] ring-2 ring-[var(--agent-accent)]/20' : 'border-[var(--muted-2)]',
        'hover:-translate-y-0.5 hover:shadow-[var(--shadow-soft)]'
      )}
    >
      <div className="flex items-start gap-3">
        {/* Vendor avatar */}
        <div
          className="mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full border border-gray-200 bg-white text-xs font-semibold text-[var(--core-color-text-primary)]"
          style={isActive ? { boxShadow: '0 0 0 8px var(--agent-accent-soft)', transform: 'scale(1.02)', transition: 'transform 200ms' } : undefined}
        >
          {(vendor || title).charAt(0).toUpperCase()}
        </div>

        {/* Content */}
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <h3 className="truncate text-sm font-semibold text-[var(--core-color-text-primary)]">
                {title}
              </h3>
              {vendor && (<p className="mt-0.5 text-xs text-[var(--core-color-text-muted)]">{vendor}</p>)}
            </div>
          </div>

          {/* Status badge + summary */}
          <div className="mt-1 flex items-center gap-2">
            <span className="inline-flex items-center rounded-[8px] border border-gray-200 bg-white px-2 py-0.5 text-[11px] font-medium text-[var(--core-color-text-secondary)]">
              {nextAction ?? config.label}
            </span>
          </div>

          {/* Inline micro-progress dots (3 steps) */}
          <div className="mt-1 flex items-center gap-1.5" aria-hidden="true">
            {(['sourcing','negotiating','approving'] as StageKey[]).map((s) => {
              const order = ['sourcing','negotiating','approving']
              const reached = order.indexOf(stage as any) >= order.indexOf(s as any)
              return <span key={s} className={clsx('h-1.5 w-1.5 rounded-full', reached ? 'bg-[var(--agent-accent)]' : 'bg-[var(--muted-2)]')} />
            })}
          </div>

          {/* Negotiation preview (subtle bubble) */}
          {preview && (
            <div className="mt-2 inline-flex max-w-full items-center rounded-md bg-gray-50 px-2 py-1 text-[11px] text-[var(--core-color-text-secondary)]">
              <span className="truncate">{preview}</span>
            </div>
          )}
        </div>
      </div>

      {/* Single primary CTA + overflow */}
      <div className="mt-3 flex items-center justify-between">
        <button
          type="button"
          onClick={onClick}
          className="inline-flex items-center gap-1 rounded-sm border border-[var(--accent-mint)] bg-white px-2.5 py-1.5 text-xs font-medium text-[var(--core-color-text-primary)] hover:bg-[var(--accent-mint)]/30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-mint)]/60"
        >
          <MessageSquare className="h-3.5 w-3.5" /> Open negotiation
        </button>
        <button
          type="button"
          aria-label="More options"
          className="inline-flex h-7 w-7 items-center justify-center rounded-sm border border-gray-200 bg-white text-[var(--core-color-text-secondary)] opacity-0 transition-opacity group-hover:opacity-100 hover:bg-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-200"
        >
          <MoreHorizontal className="h-4 w-4" />
        </button>
      </div>
    </button>
  )
}
