import { useState } from 'react'
import clsx from 'clsx'

const BASE_REQUIREMENTS: Record<string, string[]> = {
  saas: [
    'Single sign-on',
    'API access',
    'Usage analytics',
    'Role-based permissions',
  ],
  hardware: ['Next-day replacement', 'Uptime SLA 99.9%', 'Remote management'],
  services: [
    'Dedicated success manager',
    'Quarterly business reviews',
    'Escalation path',
  ],
  consulting: [
    'Certified practitioners',
    'Change management plan',
    'Executive sponsor',
  ],
}

const COMPLIANCE_OPTIONS = ['SOC2', 'ISO 27001', 'HIPAA', 'GDPR', 'PCI-DSS']

interface RequirementChecklistProps {
  category?: string
  mustHaves: string[]
  compliance: string[]
  onChange: (payload: { mustHaves: string[]; compliance: string[] }) => void
}

export function RequirementChecklist({
  category,
  mustHaves,
  compliance,
  onChange,
}: RequirementChecklistProps): JSX.Element {
  const [customRequirement, setCustomRequirement] = useState('')
  const defaults = BASE_REQUIREMENTS[category ?? ''] ?? BASE_REQUIREMENTS.saas

  const toggleMustHave = (item: string) => {
    const next = mustHaves.includes(item)
      ? mustHaves.filter((value) => value !== item)
      : [...mustHaves, item]
    onChange({ mustHaves: next, compliance })
  }

  const toggleCompliance = (item: string) => {
    const next = compliance.includes(item)
      ? compliance.filter((value) => value !== item)
      : [...compliance, item]
    onChange({ mustHaves, compliance: next })
  }

  const addCustomRequirement = () => {
    if (!customRequirement.trim()) return
    const value = customRequirement.trim()
    setCustomRequirement('')
    onChange({ mustHaves: [...mustHaves, value], compliance })
  }

  const requirementOptions = defaults.map((item) => {
    const selected = mustHaves.includes(item)
    return (
      <button
        key={item}
        type="button"
        onClick={() => {
          toggleMustHave(item)
        }}
        className={clsx(
          'rounded-full border px-3 py-1 text-xs font-medium transition-colors',
          selected
            ? 'border-transparent bg-[var(--core-color-brand-primary)] text-white'
            : 'border-[var(--core-color-border-medium)] text-[var(--core-color-text-secondary)] hover:border-[var(--core-color-border-focus)] hover:text-[var(--core-color-text-primary)]'
        )}
      >
        {item}
      </button>
    )
  })

  const complianceOptions = COMPLIANCE_OPTIONS.map((item) => {
    const selected = compliance.includes(item)
    return (
      <button
        key={item}
        type="button"
        onClick={() => {
          toggleCompliance(item)
        }}
        className={clsx(
          'inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium transition-colors',
          selected
            ? 'border-transparent bg-[var(--core-color-brand-primary)] text-white'
            : 'border-[var(--core-color-border-medium)] text-[var(--core-color-text-secondary)] hover:border-[var(--core-color-border-focus)] hover:text-[var(--core-color-text-primary)]'
        )}
      >
        <span
          className={clsx(
            'h-2 w-2 rounded-full',
            selected ? 'bg-white' : 'bg-[var(--core-color-border-medium)]'
          )}
          aria-hidden="true"
        />
        {item}
      </button>
    )
  })

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-semibold text-[var(--core-color-text-primary)]">
          Refine requirements
        </h2>
        <p className="text-sm text-[var(--core-color-text-muted)]">
          We pre-populate based on category. Add anything else that matters for
          sourcing.
        </p>
      </div>

      <div className="space-y-4">
        <p className="text-xs font-semibold text-[var(--core-color-text-muted)]">
          Must-have capabilities
        </p>
        <div className="flex flex-wrap gap-2">{requirementOptions}</div>
        {mustHaves.filter((item) => !defaults.includes(item)).length > 0 && (
          <div className="rounded-sm border border-[var(--core-color-border-default)] bg-[var(--core-color-surface-subtle)] p-3 text-xs">
            <p className="font-semibold text-[var(--core-color-text-primary)]">
              Custom requirements
            </p>
            <ul className="mt-1 list-disc space-y-1 pl-5 text-[var(--core-color-text-muted)]">
              {mustHaves
                .filter((item) => !defaults.includes(item))
                .map((item) => (
                  <li key={item}>{item}</li>
                ))}
            </ul>
          </div>
        )}
        <div className="flex">
          <input
            type="text"
            value={customRequirement}
            onChange={(event) => {
              setCustomRequirement(event.target.value)
            }}
            placeholder="Add custom requirement"
            className="flex-1 rounded-l-sm border border-[var(--core-color-border-default)] bg-white px-3 py-2 text-sm text-[var(--core-color-text-primary)] focus:border-[var(--core-color-border-focus)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-border-focus)]/40"
          />
          <button
            type="button"
            onClick={addCustomRequirement}
            className="rounded-r-sm border border-l-0 border-[var(--core-color-brand-primary)] bg-[var(--core-color-brand-primary)] px-3 py-2 text-xs font-semibold text-white hover:bg-[var(--core-color-brand-primary)]/90"
          >
            Add
          </button>
        </div>
      </div>

      <div className="space-y-4">
        <p className="text-xs font-semibold text-[var(--core-color-text-muted)]">
          Compliance & risk
        </p>
        <div className="flex flex-wrap gap-2">{complianceOptions}</div>
      </div>
    </div>
  )
}
