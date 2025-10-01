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
        className="inline-flex items-center gap-1 text-sm text-purple-600 hover:text-purple-700 font-medium"
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
        <Card className="absolute z-10 mt-2 w-80 shadow-lg" padding="sm">
          <div className="flex items-start justify-between mb-3">
            <h4 className="text-sm font-semibold text-gray-900">{title}</h4>
            <button
              onClick={() => setIsExpanded(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="space-y-2">
            {reasoning.map((item, idx) => (
              <div key={idx} className="text-xs">
                <span className="text-gray-600">{item.label}:</span>{' '}
                <span className="font-medium text-gray-900">{item.value}</span>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
