import { useMemo } from 'react'
import { Clock, TrendingUp, MoreHorizontal, MessageSquare } from 'lucide-react'
import clsx from 'clsx'

type StageKey = 'draft' | 'intake' | 'sourcing' | 'negotiating' | 'approving' | 'contracted' | 'provisioning' | 'completed' | 'cancelled'

interface ProgressTrackerCardProps {
  title: string
  vendor?: string
  stage: StageKey
  nextAction?: string
  budget?: string
  isActive?: boolean
  onClick?: () => void
}

const STAGE_CONFIG: Record<StageKey, { label: string; progress: number; color: string; bgColor: string }> = {
  draft: { label: 'Draft', progress: 5, color: 'text-gray-500', bgColor: 'bg-gray-50' },
  intake: { label: 'Intake', progress: 10, color: 'text-gray-600', bgColor: 'bg-gray-50' },
  sourcing: { label: 'Sourcing vendors', progress: 25, color: 'text-blue-600', bgColor: 'bg-blue-50' },
  negotiating: { label: 'Negotiating', progress: 50, color: 'text-[var(--color-ai-primary)]', bgColor: 'bg-purple-50' },
  approving: { label: 'Awaiting approval', progress: 75, color: 'text-amber-600', bgColor: 'bg-amber-50' },
  contracted: { label: 'Contracted', progress: 100, color: 'text-green-600', bgColor: 'bg-green-50' },
  provisioning: { label: 'Provisioning', progress: 90, color: 'text-teal-600', bgColor: 'bg-teal-50' },
  completed: { label: 'Completed', progress: 100, color: 'text-green-700', bgColor: 'bg-green-50' },
  cancelled: { label: 'Cancelled', progress: 0, color: 'text-red-600', bgColor: 'bg-red-50' },
}

export function ProgressTrackerCard({
  title,
  vendor,
  stage,
  nextAction,
  budget,
  isActive = false,
  onClick,
}: ProgressTrackerCardProps) {
  const config = useMemo(() => {
    return STAGE_CONFIG[stage] ?? { label: 'Unknown', progress: 0, color: 'text-gray-500', bgColor: 'bg-gray-50' }
  }, [stage])
  
  const circumference = 2 * Math.PI * 18 // radius = 18
  const strokeDashoffset = circumference - (config.progress / 100) * circumference

  const TIMELINE: StageKey[] = ['sourcing', 'negotiating', 'approving', 'contracted']
  const currentIndex = TIMELINE.indexOf(stage as StageKey)

  return (
    <button
      onClick={onClick}
      className={clsx(
        'group relative w-full rounded-[12px] border bg-white p-[18px] text-left transition-all duration-200 hover:shadow-md',
        isActive ? 'border-[var(--accent-mint)] ring-2 ring-[var(--accent-mint)]/30' : 'border-gray-200',
        isActive && 'animate-[cardPulse_2s_ease-in-out_infinite]'
      )}
    >
      {isActive && (
        <div className="absolute -top-1 -right-1">
          <span className="relative flex h-3 w-3">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[var(--accent-mint)] opacity-75" />
            <span className="relative inline-flex h-3 w-3 rounded-full bg-[var(--accent-mint)]" />
          </span>
        </div>
      )}

      <div className="flex items-start gap-4">
        {/* Vertical Micro-Timeline */}
        <div className="relative mt-1 flex w-6 flex-col items-center">
          <div className="absolute top-1 bottom-1 w-px bg-[var(--muted-line)]" aria-hidden="true" />
          {TIMELINE.map((step, idx) => {
            const reached = currentIndex >= idx
            const mint = step === 'negotiating'
            return (
              <div key={step} className={clsx('relative z-10 my-1 flex h-3 w-3 items-center justify-center rounded-full',
                reached ? (mint ? 'bg-[var(--accent-mint)]' : 'bg-gray-300') : 'bg-white border border-gray-200'
              )}>
                {isActive && step === stage && <span className="absolute inline-flex h-4 w-4 animate-ping rounded-full bg-[var(--accent-mint)] opacity-60" />}
              </div>
            )
          })}
        </div>

        {/* Progress Ring */}
        <div className="relative flex-shrink-0">
          <svg className="h-12 w-12 -rotate-90 transform">
            <circle
              cx="24"
              cy="24"
              r="18"
              stroke="currentColor"
              strokeWidth="3"
              fill="none"
              className="text-gray-200"
            />
            <circle
              cx="24"
              cy="24"
              r="18"
              stroke="currentColor"
              strokeWidth="3"
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className={clsx('transition-all duration-500', config.color)}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={clsx('text-xs font-bold', config.color)}>{config.progress}%</span>
          </div>
        </div>

        {/* Content */}
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <h3 className="truncate text-sm font-semibold text-[var(--core-color-text-primary)] group-hover:text-[var(--color-ai-primary)]">
                {title}
              </h3>
              {vendor && (
                <p className="mt-0.5 text-xs text-[var(--core-color-text-muted)]">{vendor}</p>
              )}
            </div>
            {budget && (
              <span className="flex-shrink-0 text-xs font-semibold text-[var(--core-color-text-secondary)]">
                {budget}
              </span>
            )}
          </div>

          {/* One-line action summary */}
          <p className="mt-1 text-xs text-[var(--core-color-text-secondary)]">
            {nextAction ?? config.label}
          </p>

          {/* Chips: ETA / Price / Risk */}
          <div className="mt-2 flex flex-wrap gap-2">
            <span className="inline-flex items-center gap-1 rounded-[8px] bg-[var(--accent-blue)]/30 px-2 py-0.5 text-[12px] text-[var(--core-color-text-primary)]">
              <Clock className="h-3 w-3" /> ETA: {stage === 'approving' ? '2-3 days' : stage === 'sourcing' ? '1-2 days' : '—'}
            </span>
            {budget && (
              <span className="inline-flex items-center gap-1 rounded-[8px] bg-[var(--accent-yellow)]/40 px-2 py-0.5 text-[12px] text-[var(--core-color-text-primary)]">
                💰 {budget}
              </span>
            )}
            <span className="inline-flex items-center gap-1 rounded-[8px] bg-[var(--accent-peach)]/40 px-2 py-0.5 text-[12px] text-[var(--core-color-text-primary)]">
              🛡️ {stage === 'negotiating' ? 'Medium risk' : 'Low risk'}
            </span>
          </div>
        </div>
      </div>

      {/* Footer CTAs */}
      <div className="mt-3 flex items-center justify-between">
        <button
          type="button"
          className="inline-flex items-center gap-1 rounded-sm border border-[var(--accent-mint)] bg-white px-2.5 py-1.5 text-xs font-medium text-[var(--core-color-text-primary)] transition hover:bg-[var(--accent-mint)]/30"
          onClick={onClick}
        >
          <MessageSquare className="h-3.5 w-3.5" /> View negotiation
        </button>
        <button
          type="button"
          className="inline-flex h-7 w-7 items-center justify-center rounded-sm border border-gray-200 bg-white text-[var(--core-color-text-secondary)] hover:bg-gray-50"
          aria-label="More options"
        >
          <MoreHorizontal className="h-4 w-4" />
        </button>
      </div>
    </button>
  )
}
