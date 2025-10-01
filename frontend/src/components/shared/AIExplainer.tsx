import { useState } from 'react'
import { Card } from './Card'
import clsx from 'clsx'

interface AIExplainerProps {
  title: string
  reasoning: {
    label: string
    value: string | number
  }[]
  className?: string
}

export function AIExplainer({ title, reasoning, className }: AIExplainerProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className={clsx('relative', className)}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="inline-flex items-center gap-1.5 text-sm text-ai-primary hover:text-ai-primary/80 font-medium transition-colors"
      >
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
            clipRule="evenodd"
          />
        </svg>
        Why {title}?
      </button>

      {isExpanded && (
        <div className="absolute z-10 mt-2 w-80 bg-ai-bg border-l-2 border-ai-primary rounded-sm shadow-medium">
          <div className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-ai-primary" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
                </svg>
                <h4 className="text-sm font-semibold text-ai-primary">{title}</h4>
              </div>
              <button
                onClick={() => setIsExpanded(false)}
                className="text-text-tertiary hover:text-text-secondary transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="space-y-2">
              {reasoning.map((item, idx) => (
                <div key={idx} className="text-sm">
                  <span className="text-text-secondary">{item.label}:</span>{' '}
                  <span className="font-medium text-text-primary">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
