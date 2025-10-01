import { ReactNode } from 'react'
import clsx from 'clsx'
import { Card } from './Card'
import { StatusBadge } from './StatusBadge'
import type { RequestStatus } from '../../types'

export interface StageBoardItem {
  id: string
  title: string
  subtitle?: string
  status: RequestStatus
  budgetLabel?: string
  timeInStage?: string
  blockers?: string[]
  metadata?: Array<{ label: string; value: string }>
  footer?: ReactNode
  onSelect?: (id: string) => void
}

export interface StageBoardColumn {
  id: string
  title: string
  count?: number
  tone?: 'brand' | 'buyer' | 'seller' | 'neutral'
  items: StageBoardItem[]
}

interface StageBoardProps {
  columns: StageBoardColumn[]
  emptyLabel?: string
}

export function StageBoard ({ columns, emptyLabel }: StageBoardProps): JSX.Element {
  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
      {columns.map((column) => (
        <div key={column.id} className="flex min-w-[240px] flex-col rounded-xl border border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)]">
          <header className="flex items-center justify-between border-b border-[var(--core-color-border-default)] px-4 py-3">
            <div>
              <p className="text-sm font-semibold text-[var(--core-color-text-primary)]">{column.title}</p>
              {column.count !== undefined && (
                <p className="text-xs text-[var(--core-color-text-muted)]">{column.count} in this stage</p>
              )}
            </div>
            <span
              className={clsx('inline-flex h-6 min-w-[2.5rem] items-center justify-center rounded-full px-2 text-xs font-semibold', {
                'bg-[var(--core-color-brand-primary)]/10 text-[var(--core-color-brand-primary)]': column.tone === 'brand',
                'bg-[var(--persona-color-buyer-accent)]/10 text-[var(--persona-color-buyer-accent)]': column.tone === 'buyer',
                'bg-[var(--persona-color-seller-accent)]/10 text-[var(--persona-color-seller-accent)]': column.tone === 'seller',
                'bg-[var(--core-color-surface-subtle)] text-[var(--core-color-text-muted)]': !column.tone || column.tone === 'neutral',
              })}
            >
              {column.count ?? column.items.length}
            </span>
          </header>
          <div className="flex-1 space-y-3 overflow-y-auto px-3 py-3">
            {column.items.length === 0 && (
              <div className="rounded-lg border border-dashed border-[var(--core-color-border-default)] bg-[var(--core-color-surface-subtle)] px-3 py-6 text-center text-xs text-[var(--core-color-text-muted)]">
                {emptyLabel ?? 'Nothing here yet'}
              </div>
            )}
            {column.items.map((item) => (
              <Card
                key={item.id}
                padding="sm"
                hover={!!item.onSelect}
                onClick={() => item.onSelect?.(item.id)}
                className="space-y-3 border-[var(--core-color-border-default)] bg-white"
              >
                <div className="space-y-2">
                  <div>
                    <p className="text-sm font-semibold text-[var(--core-color-text-primary)]">{item.title}</p>
                    {item.subtitle && (
                      <p className="mt-1 text-xs text-[var(--core-color-text-muted)]">{item.subtitle}</p>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-2 text-xs text-[var(--core-color-text-muted)]">
                    {item.budgetLabel && <span className="font-medium text-[var(--core-color-text-primary)]">{item.budgetLabel}</span>}
                    {item.timeInStage && <span>{item.timeInStage}</span>}
                  </div>
                  <StatusBadge status={item.status} size="sm" />
                </div>

                {item.metadata && item.metadata.length > 0 && (
                  <div className="grid gap-1 text-xs">
                    {item.metadata.map((meta) => (
                      <div key={meta.label} className="flex justify-between text-[var(--core-color-text-muted)]">
                        <span>{meta.label}</span>
                        <span className="font-semibold text-[var(--core-color-text-primary)]">{meta.value}</span>
                      </div>
                    ))}
                  </div>
                )}

                {item.blockers && item.blockers.length > 0 && (
                  <div className="rounded-md bg-[rgba(220,38,38,0.05)] p-2 text-xs text-[var(--core-color-data-critical)]">
                    Blockers:
                    <ul className="mt-1 list-disc pl-4">
                      {item.blockers.map((blocker) => (
                        <li key={blocker}>{blocker}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {item.footer}
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
