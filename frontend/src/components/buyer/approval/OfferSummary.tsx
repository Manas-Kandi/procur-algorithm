import { Card } from '../../shared/Card'
import { AIExplainer } from '../../shared/AIExplainer'

interface OfferSummaryProps {
  vendorName: string
  totalValue: number
  unitPrice: number
  quantity: number
  termMonths: number
  paymentTerms: string
  confidence?: number
}

export function OfferSummary ({ vendorName, totalValue, unitPrice, quantity, termMonths, paymentTerms, confidence }: OfferSummaryProps): JSX.Element {
  const formatter = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })

  return (
    <Card padding="lg" className="space-y-6 border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)]">
      <header className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-[var(--core-color-text-muted)]">Offer summary</p>
          <h2 className="text-xl font-semibold text-[var(--core-color-text-primary)]">{vendorName}</h2>
        </div>
        {confidence !== undefined && (
          <span className="inline-flex items-center rounded-full bg-[rgba(37,99,235,0.12)] px-3 py-1 text-xs font-semibold text-[var(--core-color-brand-primary)]">
            Confidence {Math.round(confidence * 100)}%
          </span>
        )}
      </header>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase tracking-wide text-[var(--core-color-text-muted)]">Total contract value</span>
            <span className="text-2xl font-semibold text-[var(--core-color-text-primary)]">{formatter.format(totalValue)}</span>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm text-[var(--core-color-text-muted)]">
            <div>
              <p>Unit price</p>
              <p className="font-semibold text-[var(--core-color-text-primary)]">{formatter.format(unitPrice)}</p>
            </div>
            <div>
              <p>Quantity</p>
              <p className="font-semibold text-[var(--core-color-text-primary)]">{quantity} seats</p>
            </div>
            <div>
              <p>Term</p>
              <p className="font-semibold text-[var(--core-color-text-primary)]">{termMonths} months</p>
            </div>
            <div>
              <p>Payment terms</p>
              <p className="font-semibold text-[var(--core-color-text-primary)]">{paymentTerms}</p>
            </div>
          </div>
        </div>
        <div className="space-y-3">
          <div className="rounded-lg bg-[var(--core-color-surface-subtle)] p-3 text-xs text-[var(--core-color-text-muted)]">
            <p className="text-sm font-semibold text-[var(--core-color-text-primary)]">Total cost of ownership snapshot</p>
            <ul className="mt-2 space-y-1">
              <li className="flex justify-between"><span>Annual subscription</span><span className="font-semibold text-[var(--core-color-text-primary)]">{formatter.format(unitPrice * quantity)}</span></li>
              <li className="flex justify-between"><span>Implementation</span><span className="font-semibold text-[var(--core-color-text-primary)]">$5,000</span></li>
              <li className="flex justify-between"><span>Training</span><span className="font-semibold text-[var(--core-color-text-primary)]">$2,500</span></li>
            </ul>
          </div>
          <AIExplainer
            title="this recommendation"
            reasoning={[
              { label: 'Savings vs benchmark', value: '15% below' },
              { label: 'Feature coverage', value: '95% match' },
              { label: 'Risk profile', value: 'Low (SOC2 + ISO)' },
            ]}
          />
        </div>
      </div>
    </Card>
  )
}
