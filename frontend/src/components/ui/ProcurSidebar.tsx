import React from 'react'
import { Home, FilePlus, Briefcase, ChevronsRight } from 'lucide-react'
import clsx from 'clsx'

export interface ProcurSidebarProps {
  open: boolean
  selectedKey?: string
  onSelect?: (key: string) => void
  onToggle?: () => void
}

const items = [
  { key: 'dashboard', label: 'Dashboard', Icon: Home },
  { key: 'new-request', label: 'New Request', Icon: FilePlus },
  { key: 'portfolio', label: 'Portfolio', Icon: Briefcase },
]

export function ProcurSidebar({ open, selectedKey = 'dashboard', onSelect, onToggle }: ProcurSidebarProps) {
  const widthClass = open ? 'w-64' : 'w-16'

  return (
    <aside
      className={clsx(
        'sticky top-0 h-screen shrink-0 border-r transition-all duration-300 ease-in-out',
        widthClass,
        'border-[var(--muted-2)] bg-[var(--surface)]'
      )}
    >
      {/* Title / Brand */}
      <div className="flex items-center gap-2 px-2 py-3">
        <div className="min-w-0">
          <div className={clsx('text-sm font-semibold', open ? 'text-[var(--text)]' : 'text-[var(--color-text-tertiary)]')}>Procur</div>
        </div>
      </div>

      <div className="px-2">
        {items.map(({ key, label, Icon }) => {
          const selected = key === selectedKey
          return (
            <button
              key={key}
              onClick={() => onSelect?.(key)}
              className={clsx(
                'relative my-1 flex h-11 w-full items-center rounded-[12px] text-left transition-colors',
                selected
                  ? 'bg-[var(--muted-1)] text-[var(--text)]'
                  : 'hover:bg-[var(--muted-1)] text-[var(--core-color-text-secondary)]'
              )}
            >
              <div className="grid h-full w-12 place-content-center">
                <Icon className={clsx('h-4 w-4', selected ? 'text-[var(--text)]' : 'text-[var(--core-color-text-secondary)]')} />
              </div>
              {open && (
                <span className={clsx('text-sm font-medium', selected ? 'text-[var(--text)]' : 'text-[var(--text)]')}>
                  {label}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Toggle */}
      <button
        onClick={onToggle}
        className="absolute bottom-0 left-0 right-0 px-2 py-2 text-left hover:bg-[var(--muted-1)]"
        aria-label={open ? 'Collapse sidebar' : 'Expand sidebar'}
      >
        <div className="flex items-center">
          <div className="grid h-10 w-10 place-content-center">
            <ChevronsRight
              className={clsx(
                'h-4 w-4 text-[var(--core-color-text-secondary)] transition-transform duration-300',
                open && 'rotate-180'
              )}
            />
          </div>
          {open && <span className="text-sm text-[var(--core-color-text-secondary)]">Hide</span>}
        </div>
      </button>
    </aside>
  )
}
