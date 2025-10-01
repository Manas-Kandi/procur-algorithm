import { ShieldCheck, Clock, Users } from 'lucide-react'

interface PolicyPreviewProps {
  budgetMin?: number
  budgetMax?: number
  quantity?: number
  complianceCount: number
}

export function PolicyPreview ({ budgetMin, budgetMax, quantity, complianceCount }: PolicyPreviewProps): JSX.Element {
  const spendCeiling = budgetMax ?? budgetMin ?? 0
  const approvals: string[] = ['Security', 'Procurement Ops']
  if (spendCeiling > 100_000) approvals.push('Finance VP')
  if (complianceCount > 2) approvals.push('Legal')

  const estimatedTimeline = spendCeiling > 150_000 ? '5-7 business days' : '3-5 business days'
  const riskLevel = complianceCount >= 3 ? 'Low risk — requirements covered' : 'Medium risk — confirm security posture'

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold text-[var(--core-color-text-primary)]">Policy preview</h2>
        <p className="text-sm text-[var(--core-color-text-muted)]">Based on spend and scope, here’s the expected approval routing.</p>
      </div>

      <div className="grid gap-4 rounded-xl border border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)] p-4 shadow-100 md:grid-cols-2">
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 rounded-full bg-[rgba(37,99,235,0.1)] px-3 py-1 text-xs font-semibold text-[var(--core-color-brand-primary)]">
            <ShieldCheck className="h-4 w-4" aria-hidden="true" />
            Approval route
          </div>
          <ul className="space-y-2 text-sm text-[var(--core-color-text-primary)]">
            {approvals.map((step) => (
              <li key={step} className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[var(--core-color-brand-primary)]" aria-hidden="true" />
                {step}
              </li>
            ))}
          </ul>
        </div>
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-sm text-[var(--core-color-text-muted)]">
            <Clock className="h-4 w-4 text-[var(--core-color-brand-primary)]" aria-hidden="true" />
            Typical timeline: <span className="font-semibold text-[var(--core-color-text-primary)]">{estimatedTimeline}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-[var(--core-color-text-muted)]">
            <Users className="h-4 w-4 text-[var(--core-color-brand-primary)]" aria-hidden="true" />
            Seats requested: <span className="font-semibold text-[var(--core-color-text-primary)]">{quantity ?? '—'}</span>
          </div>
          <div className="rounded-lg bg-[rgba(22,163,74,0.12)] px-3 py-2 text-xs text-[var(--core-color-data-positive)]">
            {riskLevel}
          </div>
        </div>
      </div>
    </div>
  )
}
