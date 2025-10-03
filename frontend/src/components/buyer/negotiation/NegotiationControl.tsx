import { Button } from '../../shared/Button'

interface NegotiationControlProps {
  onAdjustBudget?: () => void
  onAddRequirement?: () => void
  onStop?: () => void
  onAcceptBest?: () => void
}

export function NegotiationControl({
  onAdjustBudget,
  onAddRequirement,
  onStop,
  onAcceptBest,
}: NegotiationControlProps): JSX.Element {
  return (
    <div className="rounded-xl border border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)] p-4 shadow-100">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-semibold text-[var(--core-color-text-primary)]">
            Control panel
          </p>
          <p className="text-xs text-[var(--core-color-text-muted)]">
            Adjust guardrails or intervene. Actions respect permissions and will
            be audited.
          </p>
        </div>
        <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-4">
          <Button variant="outline" onClick={onAdjustBudget}>
            Adjust budget ceiling
          </Button>
          <Button variant="outline" onClick={onAddRequirement}>
            Add requirements
          </Button>
          <Button variant="danger" onClick={onStop}>
            Pause negotiations
          </Button>
          <Button onClick={onAcceptBest}>Accept best offer</Button>
        </div>
      </div>
    </div>
  )
}
