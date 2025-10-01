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
        <div key={column.id} className="flex min-w-[280px] flex-col rounded-sm bg-background-secondary">
          <header className="flex items-center justify-between px-4 py-3">
            <div>
              <p className="text-sm font-semibold text-text-primary">{column.title}</p>
              {column.count !== undefined && (
                <p className="text-xs text-text-tertiary">{column.count} in stage</p>
              )}
            </div>
            <span
              className={clsx('inline-flex h-5 min-w-[2rem] items-center justify-center rounded-sm px-2 text-xs font-semibold', {
                'bg-brand-primary/10 text-brand-primary': column.tone === 'brand',
                'bg-info/10 text-info': column.tone === 'buyer',
                'bg-warning/10 text-warning': column.tone === 'seller',
                'bg-surface-raised text-text-tertiary': !column.tone || column.tone === 'neutral',
              })}
            >
              {column.count ?? column.items.length}
            </span>
          </header>
          <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4 min-h-[400px]">
            {column.items.length === 0 && (
              <div className="rounded-sm border border-dashed border-border-medium bg-surface-raised px-3 py-8 text-center text-xs text-text-tertiary">
                {emptyLabel ?? 'No items'}
              </div>
            )}
            {column.items.map((item) => (
              <Card
                key={item.id}
                padding="sm"
                hover={!!item.onSelect}
                onClick={() => item.onSelect?.(item.id)}
                className="space-y-3"
              >
                <div className="space-y-2">
                  <div>
                    <p className="text-sm font-semibold text-text-primary">{item.title}</p>
                    {item.subtitle && (
                      <p className="mt-1 text-xs text-text-secondary">{item.subtitle}</p>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-2 text-xs text-text-tertiary">
                    {item.budgetLabel && <span className="font-medium text-text-primary">{item.budgetLabel}</span>}
                    {item.timeInStage && <span>{item.timeInStage}</span>}
                  </div>
                  <StatusBadge status={item.status} size="sm" />
                </div>

                {item.metadata && item.metadata.length > 0 && (
                  <div className="grid gap-1.5 text-xs">
                    {item.metadata.map((meta) => (
                      <div key={meta.label} className="flex justify-between text-text-secondary">
                        <span>{meta.label}</span>
                        <span className="font-semibold text-text-primary">{meta.value}</span>
                      </div>
                    ))}
                  </div>
                )}

                {item.blockers && item.blockers.length > 0 && (
                  <div className="rounded-sm bg-danger-bg border-l-2 border-danger p-2 text-xs text-danger">
                    <span className="font-semibold">Blockers:</span>
                    <ul className="mt-1 space-y-0.5 pl-4 list-disc">
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
