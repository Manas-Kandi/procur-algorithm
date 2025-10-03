import { Sparkles } from 'lucide-react'

interface ScopeDetailsProps {
  description?: string
  type?: string
  quantity?: number
  onChange: (payload: {
    description?: string
    type?: string
    quantity?: number
  }) => void
}

const CATEGORY_OPTIONS = [
  { value: 'saas', label: 'SaaS Software' },
  { value: 'hardware', label: 'Hardware' },
  { value: 'services', label: 'Professional Services' },
  { value: 'consulting', label: 'Consulting' },
]

export function ScopeDetails({
  description,
  type,
  quantity,
  onChange,
}: ScopeDetailsProps): JSX.Element {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-semibold text-[var(--core-color-text-primary)]">
          What are you requesting?
        </h2>
        <p className="text-sm text-[var(--core-color-text-muted)]">
          Use natural language. We will extract category, quantities, and
          sourcing hints.
        </p>
      </div>

      <div>
        <label className="text-xs font-semibold text-[var(--core-color-text-muted)]">
          Description
        </label>
        <textarea
          rows={4}
          value={description ?? ''}
          onChange={(event) => {
            onChange({ description: event.target.value })
          }}
          placeholder="Example: Need enterprise CRM for 200 sales reps with territory management and Salesforce integration."
          className="mt-2 w-full rounded-lg border border-[var(--core-color-border-default)] bg-white px-4 py-3 text-sm text-[var(--core-color-text-primary)] focus:border-[var(--core-color-border-focus)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-border-focus)]/40"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="text-xs font-semibold text-[var(--core-color-text-muted)]">
            Category
          </label>
          <select
            value={type ?? ''}
            onChange={(event) => {
              onChange({ type: event.target.value })
            }}
            className="mt-2 w-full rounded-lg border border-[var(--core-color-border-default)] bg-white px-4 py-2 text-sm text-[var(--core-color-text-primary)] focus:border-[var(--core-color-border-focus)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-border-focus)]/40"
          >
            <option value="">Select category</option>
            {CATEGORY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs font-semibold text-[var(--core-color-text-muted)]">
            Quantity
          </label>
          <input
            type="number"
            value={quantity ?? ''}
            onChange={(event) => {
              onChange({ quantity: Number(event.target.value) })
            }}
            min={1}
            className="mt-2 w-full rounded-lg border border-[var(--core-color-border-default)] bg-white px-4 py-2 text-sm text-[var(--core-color-text-primary)] focus:border-[var(--core-color-border-focus)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-border-focus)]/40"
          />
        </div>
      </div>

      {description && (
        <div className="flex items-start gap-3 rounded-sm bg-[var(--core-color-surface-subtle)] px-4 py-3">
          <Sparkles
            className="mt-0.5 h-4 w-4 text-[var(--core-color-ai-primary)]"
            aria-hidden="true"
          />
          <p className="text-sm text-[var(--core-color-text-secondary)]">
            We will pre-fill vendor outreach based on detected attributes
            (category, headcount sizing, integrations).
          </p>
        </div>
      )}
    </div>
  )
}
