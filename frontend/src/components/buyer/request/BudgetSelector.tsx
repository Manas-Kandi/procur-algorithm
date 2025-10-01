import clsx from 'clsx'

export type BudgetMode = 'exact' | 'range' | 'see-pricing' | 'need-approval'

interface BudgetSelectorProps {
  mode: BudgetMode
  budgetMin?: number
  budgetMax?: number
  currency?: string
  onChange: (payload: { mode: BudgetMode; budgetMin?: number; budgetMax?: number }) => void
}

const OPTIONS: Array<{ value: BudgetMode; label: string; description: string }> = [
  {
    value: 'exact',
    label: 'I know exactly',
    description: 'Provide the amount so we can target matching offers immediately.',
  },
  {
    value: 'range',
    label: 'I have a range',
    description: 'Give us a floor and ceiling. We will balance best value vs. savings.',
  },
  {
    value: 'see-pricing',
    label: 'Show me typical pricing first',
    description: 'We will surface market benchmarks before locking budget.',
  },
  {
    value: 'need-approval',
    label: 'Need approval to determine budget',
    description: 'We will route to the right approvers to align on spend.',
  },
]

export function BudgetSelector ({ mode, budgetMin, budgetMax, currency = 'USD', onChange }: BudgetSelectorProps): JSX.Element {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-semibold text-[var(--core-color-text-primary)]">What’s your approximate budget?</h2>
        <p className="text-sm text-[var(--core-color-text-muted)]">This anchors sourcing strategy and policy routing.</p>
      </div>

      <div className="space-y-2">
        {OPTIONS.map((option) => {
          const isSelected = mode === option.value
          return (
            <label
              key={option.value}
              className="flex cursor-pointer items-start gap-3 rounded-sm px-2 py-2 hover:bg-[var(--core-color-surface-subtle)]"
            >
              <input
                type="radio"
                name="budget-mode"
                checked={isSelected}
                onChange={() => onChange({ mode: option.value, budgetMin, budgetMax })}
                className="mt-1 h-4 w-4 rounded-full border-[var(--core-color-border-medium)] text-[var(--core-color-brand-primary)] focus:ring-[var(--core-color-brand-primary)]/40"
              />
              <div className="leading-tight">
                <p className={clsx('text-sm', isSelected ? 'font-semibold text-[var(--core-color-text-primary)]' : 'text-[var(--core-color-text-primary)]')}>
                  {option.label}
                </p>
                <p className="text-xs text-[var(--core-color-text-muted)]">{option.description}</p>
              </div>
            </label>
          )
        })}
      </div>

      {mode === 'exact' && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="text-xs font-semibold text-[var(--core-color-text-muted)]">Amount</label>
            <input
              type="number"
              value={budgetMax ?? budgetMin ?? ''}
              onChange={(event) => onChange({ mode, budgetMin: Number(event.target.value), budgetMax: Number(event.target.value) })}
              className="mt-1 w-full rounded-sm border border-[var(--core-color-border-default)] bg-white px-4 py-2 text-sm text-[var(--core-color-text-primary)] focus:border-[var(--core-color-border-focus)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-border-focus)]/40"
              placeholder="50000"
              min={0}
            />
          </div>
        </div>
      )}

      {mode === 'range' && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="text-xs font-semibold text-[var(--core-color-text-muted)]">Minimum</label>
            <input
              type="number"
              value={budgetMin ?? ''}
              onChange={(event) => onChange({ mode, budgetMin: Number(event.target.value), budgetMax })}
              className="mt-1 w-full rounded-sm border border-[var(--core-color-border-default)] bg-white px-4 py-2 text-sm text-[var(--core-color-text-primary)] focus:border-[var(--core-color-border-focus)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-border-focus)]/40"
              placeholder="50000"
              min={0}
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-[var(--core-color-text-muted)]">Maximum</label>
            <input
              type="number"
              value={budgetMax ?? ''}
              onChange={(event) => onChange({ mode, budgetMin, budgetMax: Number(event.target.value) })}
              className="mt-1 w-full rounded-sm border border-[var(--core-color-border-default)] bg-white px-4 py-2 text-sm text-[var(--core-color-text-primary)] focus:border-[var(--core-color-border-focus)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-border-focus)]/40"
              placeholder="120000"
              min={budgetMin ?? 0}
            />
          </div>
        </div>
      )}

      {(mode === 'see-pricing' || mode === 'need-approval') && (
        <div className="rounded-sm bg-[var(--core-color-surface-subtle)] px-4 py-4 text-sm text-[var(--core-color-text-secondary)]">
          We’ll surface benchmark data for {currency} spend before finalizing your budget. Expect a quick policy preview next.
        </div>
      )}
    </div>
  )
}
