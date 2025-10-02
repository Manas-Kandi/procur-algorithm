import { useMemo } from 'react'
import { Clock, TrendingUp } from 'lucide-react'
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

  return (
    <button
      onClick={onClick}
      className={clsx(
        'group relative w-full rounded-lg border bg-white p-4 text-left transition-all hover:shadow-md',
        isActive ? 'border-[var(--color-ai-primary)] ring-2 ring-[var(--color-ai-primary)]/20' : 'border-gray-200'
      )}
    >
      {isActive && (
        <div className="absolute -top-1 -right-1">
          <span className="relative flex h-3 w-3">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[var(--color-ai-primary)] opacity-75" />
            <span className="relative inline-flex h-3 w-3 rounded-full bg-[var(--color-ai-primary)]" />
          </span>
        </div>
      )}

      <div className="flex items-start gap-4">
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
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-semibold text-[var(--core-color-text-primary)] truncate group-hover:text-[var(--color-ai-primary)]">
                {title}
              </h3>
              {vendor && (
                <p className="text-xs text-[var(--core-color-text-muted)] mt-0.5">{vendor}</p>
              )}
            </div>
            {budget && (
              <span className="flex-shrink-0 text-xs font-semibold text-[var(--core-color-text-secondary)]">
                {budget}
              </span>
            )}
          </div>

          {/* Stage Badge */}
          <div className="mt-2 flex items-center gap-2">
            <span className={clsx('inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium', config.bgColor, config.color)}>
              <span className="h-1.5 w-1.5 rounded-full bg-current" />
              {config.label}
            </span>
          </div>

          {/* Next Action */}
          {nextAction && (
            <div className="mt-2 flex items-start gap-1.5 text-xs text-[var(--core-color-text-muted)]">
              <Clock className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" />
              <span>{nextAction}</span>
            </div>
          )}
        </div>
      </div>
    </button>
  )
}
