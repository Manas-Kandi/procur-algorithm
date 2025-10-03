import { Bot, Building2 } from 'lucide-react'
import clsx from 'clsx'
import { useState } from 'react'

interface Message {
  id: string
  sender: 'agent' | 'vendor'
  content: string
  timestamp?: string
  metadata?: {
    price?: string
    term?: string
    payment?: string
  }
}

interface NegotiationStoryboardProps {
  messages: Message[]
  vendorName?: string
}

export function NegotiationStoryboard({
  messages,
  vendorName = 'Vendor',
}: NegotiationStoryboardProps) {
  const [expanded, setExpanded] = useState(false)

  const visible =
    expanded || messages.length <= 3 ? messages : messages.slice(-3)
  const hasMore = messages.length > 3

  return (
    <div className="space-y-3">
      {visible.map((message) => {
        const isAgent = message.sender === 'agent'
        return (
          <div
            key={message.id}
            className={clsx(
              'flex gap-3',
              isAgent ? 'justify-start' : 'justify-end'
            )}
          >
            {isAgent && (
              <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-[var(--accent-mint)] text-[var(--core-color-text-primary)]">
                <Bot className="h-3.5 w-3.5" />
              </div>
            )}

            <div
              className={clsx(
                'max-w-[75%] rounded-lg px-4 py-2.5',
                isAgent
                  ? 'bg-[var(--accent-mint)]/60'
                  : 'bg-[var(--accent-peach)]/60'
              )}
            >
              <div className="flex items-baseline gap-2">
                <span
                  className={clsx(
                    'text-xs font-semibold',
                    'text-[var(--core-color-text-primary)]'
                  )}
                >
                  {isAgent ? 'Agent' : vendorName}
                </span>
                {message.timestamp && (
                  <span className="text-xs text-[var(--core-color-text-secondary)]">
                    {message.timestamp}
                  </span>
                )}
              </div>
              <p className="mt-1 text-sm text-[var(--core-color-text-primary)]">
                {message.content}
              </p>
            </div>

            {!isAgent && (
              <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-[var(--accent-peach)] text-[var(--core-color-text-primary)]">
                <Building2 className="h-3.5 w-3.5" />
              </div>
            )}
          </div>
        )
      })}

      {hasMore && (
        <div className="pt-1">
          <button
            type="button"
            onClick={() => {
              setExpanded((v) => !v)
            }}
            className="text-xs text-[var(--core-color-text-secondary)] underline-offset-2 hover:underline"
          >
            {expanded ? 'Collapse' : `Show full thread (${messages.length})`}
          </button>
        </div>
      )}
    </div>
  )
}
