/**
 * AI Reasoning Box Component
 * Displays AI agent's reasoning and decision-making process
 */

import React, { useState } from 'react'
import clsx from 'clsx'
import { 
  Sparkles, 
  ChevronDown, 
  ChevronUp, 
  Brain,
  AlertCircle,
  CheckCircle,
  XCircle,
  Info,
  Zap,
  Target,
  TrendingUp,
  Shield
} from 'lucide-react'

export interface AIReasoningProps {
  title?: string
  reasoning: string | ReasoningStep[]
  confidence?: number
  factors?: DecisionFactor[]
  recommendation?: string
  variant?: 'default' | 'success' | 'warning' | 'danger'
  expandable?: boolean
  defaultExpanded?: boolean
  timestamp?: string
}

export interface ReasoningStep {
  step: number
  description: string
  impact?: 'positive' | 'negative' | 'neutral'
}

export interface DecisionFactor {
  name: string
  value: string | number
  weight?: number
  sentiment?: 'positive' | 'negative' | 'neutral'
}

export const AIReasoningBox: React.FC<AIReasoningProps> = ({
  title = 'AI Analysis',
  reasoning,
  confidence,
  factors,
  recommendation,
  variant = 'default',
  expandable = true,
  defaultExpanded = false,
  timestamp,
}) => {
  const [expanded, setExpanded] = useState(defaultExpanded)

  const getVariantStyles = () => {
    switch (variant) {
      case 'success':
        return 'bg-success/5 border-l-success'
      case 'warning':
        return 'bg-warning/5 border-l-warning'
      case 'danger':
        return 'bg-danger/5 border-l-danger'
      default:
        return 'bg-ai-bg border-l-ai-primary'
    }
  }

  const getConfidenceColor = (level: number) => {
    if (level >= 80) return 'text-success'
    if (level >= 60) return 'text-warning'
    return 'text-danger'
  }

  const getImpactIcon = (impact?: string) => {
    switch (impact) {
      case 'positive':
        return <CheckCircle className="h-4 w-4 text-success" />
      case 'negative':
        return <XCircle className="h-4 w-4 text-danger" />
      default:
        return <Info className="h-4 w-4 text-info" />
    }
  }

  const getSentimentColor = (sentiment?: string) => {
    switch (sentiment) {
      case 'positive':
        return 'text-success'
      case 'negative':
        return 'text-danger'
      default:
        return 'text-text-secondary'
    }
  }

  const renderReasoning = () => {
    if (typeof reasoning === 'string') {
      return (
        <p className="text-sm text-text-secondary leading-relaxed">
          {reasoning}
        </p>
      )
    }

    return (
      <div className="space-y-3">
        {reasoning.map((step) => (
          <div key={step.step} className="flex gap-3">
            <div className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-ai-primary/10 text-ai-primary text-xs font-semibold">
              {step.step}
            </div>
            <div className="flex-1 flex items-start gap-2">
              <p className="text-sm text-text-secondary leading-relaxed">
                {step.description}
              </p>
              {step.impact && getImpactIcon(step.impact)}
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className={clsx(
      'rounded-sm border-l-4 overflow-hidden transition-all duration-200',
      getVariantStyles()
    )}>
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-ai-primary/10 rounded-sm">
              <Sparkles className="h-4 w-4 text-ai-primary" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-ai-primary">
                {title}
              </h3>
              {timestamp && (
                <p className="text-xs text-text-tertiary mt-0.5">
                  {timestamp}
                </p>
              )}
            </div>
          </div>
          {expandable && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-1 hover:bg-background-secondary rounded-sm transition-colors"
            >
              {expanded ? (
                <ChevronUp className="h-4 w-4 text-text-tertiary" />
              ) : (
                <ChevronDown className="h-4 w-4 text-text-tertiary" />
              )}
            </button>
          )}
        </div>

        {/* Confidence Score */}
        {confidence !== undefined && (
          <div className="mb-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-medium text-text-secondary">
                Confidence Level
              </span>
              <span className={clsx(
                'text-xs font-semibold',
                getConfidenceColor(confidence)
              )}>
                {confidence}%
              </span>
            </div>
            <div className="w-full h-1.5 bg-background-tertiary rounded-full overflow-hidden">
              <div
                className={clsx(
                  'h-full transition-all duration-500',
                  confidence >= 80 ? 'bg-success' :
                  confidence >= 60 ? 'bg-warning' : 'bg-danger'
                )}
                style={{ width: `${confidence}%` }}
              />
            </div>
          </div>
        )}

        {/* Main Content */}
        {(!expandable || expanded) && (
          <div className="space-y-4">
            {/* Reasoning */}
            <div>{renderReasoning()}</div>

            {/* Decision Factors */}
            {factors && factors.length > 0 && (
              <div className="pt-3 border-t border-border-subtle">
                <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
                  Key Factors
                </h4>
                <div className="space-y-2">
                  {factors.map((factor, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm text-text-secondary">
                        {factor.name}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className={clsx(
                          'text-sm font-medium',
                          getSentimentColor(factor.sentiment)
                        )}>
                          {factor.value}
                        </span>
                        {factor.weight && (
                          <span className="text-xs text-text-tertiary">
                            ({factor.weight}% weight)
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendation */}
            {recommendation && (
              <div className="pt-3 border-t border-border-subtle">
                <div className="flex items-start gap-2">
                  <Zap className="h-4 w-4 text-ai-primary mt-0.5" />
                  <div>
                    <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1">
                      Recommendation
                    </h4>
                    <p className="text-sm text-text-primary font-medium">
                      {recommendation}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Collapsed State Summary */}
        {expandable && !expanded && recommendation && (
          <p className="text-sm text-text-primary font-medium mt-2">
            {recommendation}
          </p>
        )}
      </div>
    </div>
  )
}

// ============================================================================
// AI Activity Indicator Component
// ============================================================================

export interface AIActivityIndicatorProps {
  status: 'idle' | 'thinking' | 'negotiating' | 'analyzing' | 'complete'
  message?: string
}

export const AIActivityIndicator: React.FC<AIActivityIndicatorProps> = ({
  status,
  message,
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'thinking':
        return {
          icon: Brain,
          color: 'text-ai-primary',
          bgColor: 'bg-ai-primary/10',
          text: message || 'AI is thinking...',
          animate: true,
        }
      case 'negotiating':
        return {
          icon: TrendingUp,
          color: 'text-warning',
          bgColor: 'bg-warning/10',
          text: message || 'Negotiating with vendors...',
          animate: true,
        }
      case 'analyzing':
        return {
          icon: Target,
          color: 'text-info',
          bgColor: 'bg-info/10',
          text: message || 'Analyzing options...',
          animate: true,
        }
      case 'complete':
        return {
          icon: CheckCircle,
          color: 'text-success',
          bgColor: 'bg-success/10',
          text: message || 'Analysis complete',
          animate: false,
        }
      default:
        return {
          icon: Shield,
          color: 'text-text-tertiary',
          bgColor: 'bg-background-tertiary',
          text: message || 'AI ready',
          animate: false,
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon

  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-surface-raised border border-border-subtle rounded-full">
      <div className={clsx(
        'p-1 rounded-full',
        config.bgColor,
        config.animate && 'animate-pulse'
      )}>
        <Icon className={clsx('h-3.5 w-3.5', config.color)} />
      </div>
      <span className="text-xs font-medium text-text-secondary">
        {config.text}
      </span>
      {config.animate && (
        <div className="flex gap-0.5">
          <span className="w-1 h-1 bg-text-tertiary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="w-1 h-1 bg-text-tertiary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="w-1 h-1 bg-text-tertiary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      )}
    </div>
  )
}

// ============================================================================
// AI Suggestion Card Component
// ============================================================================

export interface AISuggestionProps {
  title: string
  description: string
  actions?: Array<{
    label: string
    onClick: () => void
    variant?: 'primary' | 'secondary'
  }>
  icon?: React.ReactNode
  dismissible?: boolean
  onDismiss?: () => void
}

export const AISuggestionCard: React.FC<AISuggestionProps> = ({
  title,
  description,
  actions,
  icon,
  dismissible = true,
  onDismiss,
}) => {
  return (
    <div className="bg-ai-bg border border-ai-primary/20 rounded-sm p-4">
      <div className="flex items-start gap-3">
        {icon || (
          <div className="p-2 bg-ai-primary/10 rounded-sm">
            <Sparkles className="h-5 w-5 text-ai-primary" />
          </div>
        )}
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-text-primary mb-1">
            {title}
          </h3>
          <p className="text-sm text-text-secondary mb-3">
            {description}
          </p>
          {actions && actions.length > 0 && (
            <div className="flex gap-2">
              {actions.map((action, index) => (
                <button
                  key={index}
                  onClick={action.onClick}
                  className={clsx(
                    'px-3 py-1.5 text-xs font-medium rounded-sm transition-colors',
                    action.variant === 'primary'
                      ? 'bg-ai-primary text-white hover:bg-ai-primary/90'
                      : 'bg-background-secondary text-text-primary hover:bg-background-tertiary'
                  )}
                >
                  {action.label}
                </button>
              ))}
            </div>
          )}
        </div>
        {dismissible && onDismiss && (
          <button
            onClick={onDismiss}
            className="p-1 hover:bg-background-secondary rounded-sm transition-colors"
          >
            <XCircle className="h-4 w-4 text-text-tertiary" />
          </button>
        )}
      </div>
    </div>
  )
}
