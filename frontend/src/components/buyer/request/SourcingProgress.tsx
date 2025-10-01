import { Loader2, CheckCircle2 } from 'lucide-react'

interface SourcingProgressProps {
  status: 'idle' | 'running' | 'completed'
  contacted?: number
  responded?: number
  negotiating?: number
}

export function SourcingProgress ({ status, contacted = 0, responded = 0, negotiating = 0 }: SourcingProgressProps): JSX.Element {
  const steps = [
    { label: 'Vendor outreach initiated', value: contacted, target: 12 },
    { label: 'Responses received', value: responded, target: 8 },
    { label: 'Active negotiations', value: negotiating, target: 3 },
  ]

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        {status === 'completed' ? (
          <CheckCircle2 className="h-5 w-5 text-[var(--core-color-data-positive)]" aria-hidden="true" />
        ) : (
          <Loader2 className="h-5 w-5 animate-spin text-[var(--core-color-brand-primary)]" aria-hidden="true" />
        )}
        <div>
          <p className="text-sm font-semibold text-[var(--core-color-text-primary)]">
            {status === 'completed' ? 'AI sourcing completed' : 'AI sourcing in progress'}
          </p>
          <p className="text-xs text-[var(--core-color-text-muted)]">We will notify you as negotiations mature.</p>
        </div>
      </div>

      <div className="space-y-3">
        {steps.map((step) => {
          const percent = Math.min(100, Math.round((step.value / step.target) * 100))
          return (
            <div key={step.label}>
              <div className="flex items-center justify-between text-xs text-[var(--core-color-text-muted)]">
                <span>{step.label}</span>
                <span className="font-semibold text-[var(--core-color-text-primary)]">{step.value}/{step.target}</span>
              </div>
              <div className="mt-1 h-2 w-full rounded-full bg-[var(--core-color-surface-subtle)]">
                <div
                  className="h-2 rounded-full bg-[var(--core-color-brand-primary)] transition-all"
                  style={{ width: `${percent}%` }}
                  aria-hidden="true"
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
