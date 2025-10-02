import { Bot, Building2 } from 'lucide-react'
import clsx from 'clsx'

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

export function NegotiationStoryboard({ messages, vendorName = 'Vendor' }: NegotiationStoryboardProps) {
  return (
    <div className="space-y-3">
      {messages.map((message) => {
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
              <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[var(--color-ai-primary)] to-[var(--color-brand-primary)] text-white">
                <Bot className="h-4 w-4" />
              </div>
            )}
            
            <div
              className={clsx(
                'max-w-[75%] rounded-lg px-4 py-2.5',
                isAgent
                  ? 'bg-[var(--color-ai-bg)] border border-[var(--color-ai-primary)]/20'
                  : 'bg-gray-50 border border-gray-200'
              )}
            >
              <div className="flex items-baseline gap-2">
                <span className={clsx('text-xs font-semibold', isAgent ? 'text-[var(--color-ai-primary)]' : 'text-[var(--core-color-text-secondary)]')}>
                  {isAgent ? 'Agent' : vendorName}
                </span>
                {message.timestamp && (
                  <span className="text-xs text-[var(--core-color-text-tertiary)]">{message.timestamp}</span>
                )}
              </div>
              <p className="mt-1 text-sm text-[var(--core-color-text-primary)]">{message.content}</p>
              
              {message.metadata && (
                <div className="mt-2 flex flex-wrap gap-2 text-xs">
                  {message.metadata.price && (
                    <span className="rounded-full bg-white px-2 py-0.5 font-medium text-[var(--core-color-text-secondary)]">
                      💰 {message.metadata.price}
                    </span>
                  )}
                  {message.metadata.term && (
                    <span className="rounded-full bg-white px-2 py-0.5 font-medium text-[var(--core-color-text-secondary)]">
                      📅 {message.metadata.term}
                    </span>
                  )}
                  {message.metadata.payment && (
                    <span className="rounded-full bg-white px-2 py-0.5 font-medium text-[var(--core-color-text-secondary)]">
                      ⏱️ {message.metadata.payment}
                    </span>
                  )}
                </div>
              )}
            </div>

            {!isAgent && (
              <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full border border-gray-200 bg-gray-50 text-[var(--core-color-text-secondary)]">
                <Building2 className="h-4 w-4" />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
