import { ShieldCheck, AlertTriangle } from 'lucide-react'
import { Card } from '../../shared/Card'

interface RiskItem {
  label: string
  status: 'pass' | 'warning' | 'fail'
  details: string
}

interface RiskPanelProps {
  items: RiskItem[]
  certifications: string[]
}

const STATUS_CLASSES = {
  pass: 'text-[var(--core-color-data-positive)]',
  warning: 'text-[var(--core-color-data-warning)]',
  fail: 'text-[var(--core-color-data-critical)]',
}

export function RiskPanel ({ items, certifications }: RiskPanelProps): JSX.Element {
  return (
    <Card padding="lg" className="space-y-5 border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)]">
      <header className="flex items-center gap-2">
        <ShieldCheck className="h-5 w-5 text-[var(--core-color-brand-primary)]" aria-hidden="true" />
        <div>
          <p className="text-sm font-semibold text-[var(--core-color-text-primary)]">Risk & compliance</p>
          <p className="text-xs text-[var(--core-color-text-muted)]">Policy coverage with remediation guidance.</p>
        </div>
      </header>

      <div className="space-y-3">
        {items.map((item) => (
          <div key={item.label} className="rounded-lg border border-[var(--core-color-border-default)] px-3 py-2">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-semibold text-[var(--core-color-text-primary)]">{item.label}</p>
                <p className="text-xs text-[var(--core-color-text-muted)]">{item.details}</p>
              </div>
              {item.status === 'warning' ? (
                <AlertTriangle className={`h-4 w-4 ${STATUS_CLASSES[item.status]}`} aria-hidden="true" />
              ) : (
                <span className={`text-xs font-semibold ${STATUS_CLASSES[item.status]}`}>
                  {item.status === 'pass' ? 'Pass' : 'Fail'}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-wide text-[var(--core-color-text-muted)]">Certifications</p>
        <div className="flex flex-wrap gap-2">
          {certifications.map((cert) => (
            <span key={cert} className="inline-flex items-center rounded-full bg-[rgba(22,163,74,0.12)] px-3 py-1 text-xs font-semibold text-[var(--core-color-data-positive)]">
              {cert}
            </span>
          ))}
        </div>
      </div>
    </Card>
  )
}
