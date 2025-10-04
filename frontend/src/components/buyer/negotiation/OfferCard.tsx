import { type ReactNode, useMemo } from 'react'
import clsx from 'clsx'
import { Card } from '../../shared/Card'
import { AIExplainer } from '../../shared/AIExplainer'
import type { NegotiationSession } from '../../../types'

interface OfferCardProps {
  session: NegotiationSession
  rank: number
  status?: 'leading' | 'contender' | 'fallback'
  actions?: ReactNode
}

export function OfferCard({
  session,
  rank,
  status = 'contender',
  actions,
}: OfferCardProps): JSX.Element {
  const bestOffer = session.best_offer
  const currency = bestOffer?.components.currency ?? 'USD'
  const unitPriceDisplay = useMemo(() => {
    if (!bestOffer) return null
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
    }).format(bestOffer.components.unit_price)
  }, [bestOffer, currency])

  return (
    <Card
      variant="canvas"
      elevation="200"
      rounded="md"
      className={clsx('relative h-full', {
        'ring-2 ring-[var(--core-color-brand-primary)]': status === 'leading',
      })}
    >
      <span
        className="absolute top-2 right-2 inline-flex h-7 w-7 items-center justify-center rounded-full bg-[var(--core-color-brand-primary)] text-[10px] font-semibold text-white shadow-200"
        aria-label={`Rank ${rank}`}
      >
        #{rank}
      </span>

      <div className="space-y-4">
        <header className="space-y-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-[var(--core-color-text-muted)]">
            Vendor
          </p>
          <h3 className="text-lg font-semibold text-[var(--core-color-text-primary)]">
            Vendor {session.vendor_id.slice(0, 8)}
          </h3>
          <p className="text-xs text-[var(--core-color-text-muted)]">
            Round {session.current_round}
          </p>
        </header>

        {bestOffer ? (
          <div className="space-y-4">
            <div>
              <p className="text-3xl font-semibold text-[var(--core-color-text-primary)]">
                {unitPriceDisplay}
                <span className="ml-1 text-sm font-normal text-[var(--core-color-text-muted)]">
                  /seat/year
                </span>
              </p>
              <p className="mt-1 text-xs text-[var(--core-color-text-muted)]">
                {bestOffer.components.term_months} month term •{' '}
                {bestOffer.components.payment_terms}
              </p>
            </div>

            <div className="space-y-2 rounded-2xl border border-[var(--core-color-border-default)] bg-[var(--core-color-surface-subtle)] p-3">
              <div className="flex items-center justify-between text-xs text-[var(--core-color-text-muted)]">
                <span>Utility score</span>
                <span className="font-semibold text-[var(--core-color-text-primary)]">
                  {(bestOffer.score.utility * 100).toFixed(0)}%
                </span>
              </div>
              <div className="h-2 w-full rounded-full bg-[var(--core-color-border-default)]/60">
                <div
                  className="h-2 rounded-full bg-[var(--core-color-brand-primary)]"
                  style={{ width: `${bestOffer.score.utility * 100}%` }}
                  aria-hidden="true"
                />
              </div>
            </div>

            <AIExplainer
              title="this offer"
              reasoning={[
                { label: 'Budget alignment', value: unitPriceDisplay ?? '$0' },
                {
                  label: 'Feature match',
                  value: `${(bestOffer.score.spec_match * 100).toFixed(0)}%`,
                },
                {
                  label: 'Risk score',
                  value: `${(bestOffer.score.risk * 100).toFixed(0)}%`,
                },
                {
                  label: 'Value score',
                  value: `${(bestOffer.score.utility * 100).toFixed(0)}%`,
                },
              ]}
            />
          </div>
        ) : (
          <div className="rounded-lg border border-dashed border-[var(--core-color-border-default)] p-4 text-sm text-[var(--core-color-text-muted)]">
            Waiting for first offer from this vendor.
          </div>
        )}

        {actions}
      </div>
    </Card>
  )
}
