import { ShieldCheck, Zap, BadgeDollarSign, Info } from 'lucide-react'
import clsx from 'clsx'

interface DecisionCardProps {
  title: string
  highlight: string
  rationale: Array<{ icon: 'cost' | 'speed' | 'risk'; text: string }>
  onSelect?: () => void
}

const ICONS = {
  cost: <BadgeDollarSign className="h-4 w-4" />,
  speed: <Zap className="h-4 w-4" />,
  risk: <ShieldCheck className="h-4 w-4" />,
} as const

function DecisionCard({ title, highlight, rationale, onSelect }: DecisionCardProps) {
  return (
    <button
      onClick={onSelect}
      className="group w-full rounded-lg border border-gray-200 bg-white p-5 text-left transition hover:shadow-md"
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-sm font-semibold text-[var(--core-color-text-primary)]">{title}</h3>
          <p className="mt-1 text-2xl font-bold text-[var(--core-color-text-primary)]">{highlight}</p>
        </div>
        <div className="rounded-full border border-gray-200 bg-gray-50 p-2 text-[var(--color-ai-primary)]">
          <Info className="h-4 w-4" />
        </div>
      </div>

      <div className="mt-3 space-y-1">
        {rationale.map((r, idx) => (
          <div key={idx} className="flex items-center gap-2 text-xs text-[var(--core-color-text-secondary)]">
            <span className="text-[var(--color-ai-primary)]">{ICONS[r.icon]}</span>
            <span>{r.text}</span>
          </div>
        ))}
      </div>
    </button>
  )
}

interface DecisionGateProps {
  onSelect?: (choice: 'value' | 'speed' | 'risk') => void
}

export function DecisionGate({ onSelect }: DecisionGateProps) {
  return (
    <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
      <DecisionCard
        title="Best Value"
        highlight="$1,045 / seat"
        rationale={[
          { icon: 'cost', text: 'Lowest total cost of ownership' },
          { icon: 'risk', text: 'Meets all core requirements' },
          { icon: 'speed', text: 'Standard delivery timeline' },
        ]}
        onSelect={() => onSelect?.('value')}
      />
      <DecisionCard
        title="Fastest Delivery"
        highlight="2-3 business days"
        rationale={[
          { icon: 'speed', text: 'Immediate onboarding available' },
          { icon: 'risk', text: 'Moderate risk — verify SOC2 report' },
          { icon: 'cost', text: 'Slightly higher unit cost' },
        ]}
        onSelect={() => onSelect?.('speed')}
      />
      <DecisionCard
        title="Lowest Risk"
        highlight="SOC2 + ISO 27001"
        rationale={[
          { icon: 'risk', text: 'Highest compliance coverage' },
          { icon: 'speed', text: 'Standard delivery timeline' },
          { icon: 'cost', text: 'Within 5% of best value price' },
        ]}
        onSelect={() => onSelect?.('risk')}
      />
    </div>
  )
}
