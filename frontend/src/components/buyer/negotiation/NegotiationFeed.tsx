import { Card } from '../../shared/Card'
import { AIExplainer } from '../../shared/AIExplainer'
import type { NegotiationSession } from '../../../types'

interface NegotiationFeedProps {
  session: NegotiationSession
}

export function NegotiationFeed({
  session,
}: NegotiationFeedProps): JSX.Element {
  const latestMessages = session.messages.slice(-3).reverse()

  return (
    <Card variant="canvas" elevation="200" rounded="md" className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-[var(--core-color-text-primary)]">
            Vendor {session.vendor_id.slice(0, 8)}
          </h3>
          <p className="text-xs text-[var(--core-color-text-muted)]">
            Round {session.current_round}
          </p>
        </div>
        <span className="inline-flex items-center rounded-full bg-[rgba(124,58,237,0.12)] px-3 py-1 text-xs font-semibold text-[var(--core-color-brand-secondary)]">
          Active
        </span>
      </div>

      <div className="space-y-3">
        {latestMessages.map((message, index) => {
          const currency = (message as any)?.proposal?.currency ??
            (session.best_offer as any)?.components?.currency ?? 'USD'
          const priceDisplay = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }).format(message.proposal.unit_price)

          return (
            <Card
              key={`${message.actor}-${index}`}
              variant="subtle"
              elevation="none"
              rounded="md"
              padding="sm"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <p className="text-xs font-semibold text-[var(--core-color-text-primary)]">
                    {message.actor === 'buyer' ? 'Our agent' : 'Vendor response'}
                  </p>
                  <p className="mt-1 text-sm text-[var(--core-color-text-primary)]">
                    {priceDisplay}/seat •{' '}
                    {message.proposal.term_months}mo term •{' '}
                    {message.proposal.payment_terms}
                  </p>
                  {message.justification_bullets.length > 0 && (
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-xs text-[var(--core-color-text-muted)]">
                      {message.justification_bullets.map((bullet) => (
                        <li key={bullet}>{bullet}</li>
                      ))}
                    </ul>
                  )}
                </div>
                <AIExplainer
                  title="this move"
                  reasoning={[
                    {
                      label: 'Strategy',
                      value: message.machine_rationale.concession_taken,
                    },
                    { label: 'Next step', value: message.next_step_hint },
                    ...Object.entries(
                      message.machine_rationale.score_components
                    ).map(([label, value]) => ({
                      label,
                      value: value.toFixed(2),
                    })),
                  ]}
                />
              </div>
            </Card>
          )
        })}
      </div>

      <div className="border-t border-[var(--core-color-border-default)] pt-3 text-xs text-[var(--core-color-text-muted)]">
        Next step:{' '}
        <span className="font-semibold text-[var(--core-color-text-primary)]">
          {latestMessages[0]?.next_step_hint ?? 'Waiting for vendor response'}
        </span>
      </div>
    </Card>
  )
}
