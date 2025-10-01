import clsx from 'clsx'

export type BudgetMode = 'exact' | 'range' | 'see-pricing' | 'need-approval'

interface BudgetSelectorProps {
  mode: BudgetMode
  budgetMin?: number
  budgetMax?: number
  currency?: string
  onChange: (payload: { mode: BudgetMode; budgetMin?: number; budgetMax?: number }) => void
}

const OPTIONS: Array<{ value: BudgetMode; label: string; description: string; icon: string }> = [
  {
    value: 'exact',
    label: 'I know exactly',
    description: 'Provide the amount so we can target matching offers immediately.',
    icon: '💰',
  },
  {
    value: 'range',
    label: 'I have a range',
    description: 'Give us a floor and ceiling. We will balance best value vs. savings.',
    icon: '📊',
  },
  {
    value: 'see-pricing',
    label: 'Show me typical pricing first',
    description: 'We will surface market benchmarks before locking budget.',
    icon: '🔍',
  },
  {
    value: 'need-approval',
    label: 'Need approval to determine budget',
    description: 'We will route to the right approvers to align on spend.',
    icon: '✅',
  },
]

export function BudgetSelector ({ mode, budgetMin, budgetMax, currency = 'USD', onChange }: BudgetSelectorProps): JSX.Element {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-[var(--core-color-text-primary)]">What’s your approximate budget?</h2>
        <p className="text-sm text-[var(--core-color-text-muted)]">This anchors sourcing strategy and policy routing.</p>
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {OPTIONS.map((option) => {
          const isSelected = mode === option.value
          return (
            <button
              key={option.value}
              type="button"
              onClick={() => onChange({ mode: option.value, budgetMin, budgetMax })}
              className={clsx(
                'flex h-full flex-col rounded-xl border p-4 text-left shadow-100 transition-all',
                isSelected
                  ? 'border-[var(--core-color-brand-primary)] bg-[var(--core-color-brand-primary)]/5'
                  : 'border-[var(--core-color-border-default)] hover:border-[var(--core-color-border-focus)] hover:bg-[var(--core-color-surface-subtle)]'
              )}
            >
              <span className="text-2xl" aria-hidden="true">{option.icon}</span>
              <span className="mt-3 text-sm font-semibold text-[var(--core-color-text-primary)]">{option.label}</span>
              <span className="mt-1 text-xs text-[var(--core-color-text-muted)]">{option.description}</span>
            </button>
          )
        })}
      </div>

      {(mode === 'exact' || mode === 'range') && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-[var(--core-color-text-muted)]">
              {mode === 'range' ? 'Minimum' : 'Amount'}
            </label>
            <input
              type="number"
              value={budgetMin ?? ''}
              onChange={(event) => onChange({ mode, budgetMin: Number(event.target.value), budgetMax: mode === 'exact' ? Number(event.target.value) : budgetMax })}
              className="mt-1 w-full rounded-lg border border-[var(--core-color-border-default)] bg-white px-4 py-2 text-sm text-[var(--core-color-text-primary)] focus:border-[var(--core-color-border-focus)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-border-focus)]/40"
              placeholder="50000"
              min={0}
            />
          </div>
          {mode === 'range' && (
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-[var(--core-color-text-muted)]">Maximum</label>
              <input
                type="number"
                value={budgetMax ?? ''}
                onChange={(event) => onChange({ mode, budgetMin, budgetMax: Number(event.target.value) })}
                className="mt-1 w-full rounded-lg border border-[var(--core-color-border-default)] bg-white px-4 py-2 text-sm text-[var(--core-color-text-primary)] focus:border-[var(--core-color-border-focus)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-border-focus)]/40"
                placeholder="120000"
                min={budgetMin ?? 0}
              />
            </div>
          )}
        </div>
      )}

      {(mode === 'see-pricing' || mode === 'need-approval') && (
        <div className="rounded-xl border border-dashed border-[var(--core-color-border-default)] bg-[var(--core-color-surface-subtle)] px-4 py-5 text-sm text-[var(--core-color-text-muted)]">
          <p className="font-medium text-[var(--core-color-text-primary)]">
            We’ll surface benchmark data for {currency} spend before finalizing your budget. Expect a quick policy preview next.
          </p>
        </div>
      )}
    </div>
  )
}
