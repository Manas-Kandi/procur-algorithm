import { useState } from 'react'

interface ProcurementGoalProps {
  goal?: string
  timeline_deadline?: string
  timeline_urgency?: 'low' | 'medium' | 'high' | 'critical'
  risk_notes?: string
  onChange: (data: {
    goal?: string
    timeline_deadline?: string
    timeline_urgency?: 'low' | 'medium' | 'high' | 'critical'
    risk_notes?: string
  }) => void
}

const URGENCY_OPTIONS = [
  { value: 'low', label: 'Low - Planning ahead', color: 'text-blue-600' },
  { value: 'medium', label: 'Medium - Standard timeline', color: 'text-yellow-600' },
  { value: 'high', label: 'High - Urgent need', color: 'text-orange-600' },
  { value: 'critical', label: 'Critical - Immediate requirement', color: 'text-red-600' },
] as const

export function ProcurementGoal({
  goal,
  timeline_deadline,
  timeline_urgency,
  risk_notes,
  onChange,
}: ProcurementGoalProps): JSX.Element {
  const [localGoal, setLocalGoal] = useState(goal || '')
  const [localDeadline, setLocalDeadline] = useState(timeline_deadline || '')
  const [localUrgency, setLocalUrgency] = useState<
    'low' | 'medium' | 'high' | 'critical' | undefined
  >(timeline_urgency)
  const [localRiskNotes, setLocalRiskNotes] = useState(risk_notes || '')

  const handleGoalChange = (value: string) => {
    setLocalGoal(value)
    onChange({
      goal: value,
      timeline_deadline: localDeadline,
      timeline_urgency: localUrgency,
      risk_notes: localRiskNotes,
    })
  }

  const handleDeadlineChange = (value: string) => {
    setLocalDeadline(value)
    onChange({
      goal: localGoal,
      timeline_deadline: value,
      timeline_urgency: localUrgency,
      risk_notes: localRiskNotes,
    })
  }

  const handleUrgencyChange = (value: 'low' | 'medium' | 'high' | 'critical') => {
    setLocalUrgency(value)
    onChange({
      goal: localGoal,
      timeline_deadline: localDeadline,
      timeline_urgency: value,
      risk_notes: localRiskNotes,
    })
  }

  const handleRiskNotesChange = (value: string) => {
    setLocalRiskNotes(value)
    onChange({
      goal: localGoal,
      timeline_deadline: localDeadline,
      timeline_urgency: localUrgency,
      risk_notes: value,
    })
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-lg font-semibold text-[var(--core-color-text-primary)]">
          Procurement goal
        </h2>
        <p className="mt-1 text-sm text-[var(--core-color-text-muted)]">
          Tell us the business outcome you're trying to achieve. This helps our AI
          agents find the right vendors and negotiate effectively.
        </p>
      </div>

      {/* Procurement Goal */}
      <div className="space-y-3">
        <label
          htmlFor="procurement-goal"
          className="block text-sm font-medium text-[var(--core-color-text-primary)]"
        >
          What are you trying to accomplish?
          <span className="ml-1 text-[var(--core-color-text-error)]">*</span>
        </label>
        <textarea
          id="procurement-goal"
          rows={4}
          className="w-full rounded-lg border border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)] px-4 py-3 text-sm text-[var(--core-color-text-primary)] placeholder-[var(--core-color-text-tertiary)] focus:border-[var(--core-color-brand-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-brand-primary)] focus:ring-opacity-20"
          placeholder="e.g., 'We need to streamline our customer support operations by implementing a help desk system that integrates with our existing tools and scales with our growing team.'"
          value={localGoal}
          onChange={(e) => handleGoalChange(e.target.value)}
        />
        <p className="text-xs text-[var(--core-color-text-muted)]">
          Be specific about the problem you're solving or the capability you need.
        </p>
      </div>

      {/* Timeline Section */}
      <div className="space-y-4">
        <div>
          <h3 className="text-sm font-semibold text-[var(--core-color-text-primary)]">
            Timeline
          </h3>
          <p className="mt-1 text-xs text-[var(--core-color-text-muted)]">
            Help us prioritize and find vendors who can meet your timeline.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {/* Deadline */}
          <div className="space-y-2">
            <label
              htmlFor="deadline"
              className="block text-sm font-medium text-[var(--core-color-text-primary)]"
            >
              Target deadline
            </label>
            <input
              id="deadline"
              type="date"
              className="w-full rounded-lg border border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)] px-4 py-2.5 text-sm text-[var(--core-color-text-primary)] focus:border-[var(--core-color-brand-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-brand-primary)] focus:ring-opacity-20"
              value={localDeadline}
              onChange={(e) => handleDeadlineChange(e.target.value)}
            />
          </div>

          {/* Urgency */}
          <div className="space-y-2">
            <label
              htmlFor="urgency"
              className="block text-sm font-medium text-[var(--core-color-text-primary)]"
            >
              Urgency level
            </label>
            <select
              id="urgency"
              className="w-full rounded-lg border border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)] px-4 py-2.5 text-sm text-[var(--core-color-text-primary)] focus:border-[var(--core-color-brand-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-brand-primary)] focus:ring-opacity-20"
              value={localUrgency || ''}
              onChange={(e) =>
                handleUrgencyChange(
                  e.target.value as 'low' | 'medium' | 'high' | 'critical'
                )
              }
            >
              <option value="">Select urgency...</option>
              {URGENCY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Risk & Compliance Notes */}
      <div className="space-y-3">
        <label
          htmlFor="risk-notes"
          className="block text-sm font-medium text-[var(--core-color-text-primary)]"
        >
          Risk & compliance considerations
        </label>
        <textarea
          id="risk-notes"
          rows={3}
          className="w-full rounded-lg border border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)] px-4 py-3 text-sm text-[var(--core-color-text-primary)] placeholder-[var(--core-color-text-tertiary)] focus:border-[var(--core-color-brand-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-brand-primary)] focus:ring-opacity-20"
          placeholder="e.g., 'Must be SOC 2 compliant. Data residency requirements for EU customers. Need vendor to sign our DPA.'"
          value={localRiskNotes}
          onChange={(e) => handleRiskNotesChange(e.target.value)}
        />
        <p className="text-xs text-[var(--core-color-text-muted)]">
          Include any security, compliance, or legal requirements the vendor must meet.
        </p>
      </div>

      {/* Helpful hints */}
      <div className="rounded-lg border border-[var(--core-color-border-subtle)] bg-[var(--core-color-surface-subtle)] p-4">
        <h4 className="text-sm font-semibold text-[var(--core-color-text-primary)]">
          💡 Pro tips
        </h4>
        <ul className="mt-2 space-y-1 text-xs text-[var(--core-color-text-muted)]">
          <li>• Focus on the outcome, not the solution</li>
          <li>• Be clear about any hard constraints or dealbreakers</li>
          <li>• Mention stakeholders or teams who'll be affected</li>
          <li>• Include integration requirements if relevant</li>
        </ul>
      </div>
    </div>
  )
}
