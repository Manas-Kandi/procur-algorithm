/**
 * Negotiation Feed Component
 * Real-time feed of negotiation events and messages
 */

import React, { useEffect, useRef, useState } from 'react'
import clsx from 'clsx'
import {
  MessageSquare,
  DollarSign,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Clock,
  Building,
  User,
  Zap,
  Shield,
  FileText,
  ArrowRight,
  ArrowLeft,
  Sparkles,
} from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'
import { AIReasoningBox } from '../ui/AIReasoningBox'

export interface NegotiationMessage {
  id: string
  type: 'offer' | 'counter-offer' | 'message' | 'system' | 'ai-reasoning'
  sender: 'buyer' | 'seller' | 'system'
  vendorName?: string
  timestamp: Date
  content: {
    text?: string
    price?: number
    previousPrice?: number
    discount?: number
    terms?: string[]
    reasoning?: string
    confidence?: number
  }
  status?: 'pending' | 'accepted' | 'rejected' | 'expired'
  round?: number
}

export interface NegotiationFeedProps {
  messages: NegotiationMessage[]
  currentRound?: number
  maxRounds?: number
  status?: 'active' | 'paused' | 'completed' | 'failed'
  onMessageClick?: (message: NegotiationMessage) => void
  autoScroll?: boolean
  showTimestamps?: boolean
  compactMode?: boolean
}

export const NegotiationFeed: React.FC<NegotiationFeedProps> = ({
  messages,
  currentRound,
  maxRounds,
  status = 'active',
  onMessageClick,
  autoScroll = true,
  showTimestamps = true,
  compactMode = false,
}) => {
  const feedRef = useRef<HTMLDivElement>(null)
  const [expandedMessages, setExpandedMessages] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (autoScroll && feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight
    }
  }, [messages, autoScroll])

  const toggleExpanded = (messageId: string) => {
    setExpandedMessages((prev) => {
      const next = new Set(prev)
      if (next.has(messageId)) {
        next.delete(messageId)
      } else {
        next.add(messageId)
      }
      return next
    })
  }

  const getMessageIcon = (message: NegotiationMessage) => {
    switch (message.type) {
      case 'offer':
        return message.sender === 'buyer' ? ArrowRight : ArrowLeft
      case 'counter-offer':
        return message.sender === 'buyer' ? ArrowRight : ArrowLeft
      case 'ai-reasoning':
        return Sparkles
      case 'system':
        return AlertCircle
      default:
        return MessageSquare
    }
  }

  const getMessageColor = (message: NegotiationMessage) => {
    if (message.type === 'system') return 'text-text-tertiary'
    if (message.type === 'ai-reasoning') return 'text-ai-primary'
    return message.sender === 'buyer' ? 'text-brand-primary' : 'text-warning'
  }

  const getPriceChangeIndicator = (current?: number, previous?: number) => {
    if (!current || !previous) return null
    
    const change = ((current - previous) / previous) * 100
    const isIncrease = change > 0

    return (
      <span className={clsx(
        'inline-flex items-center gap-1 text-xs font-medium',
        isIncrease ? 'text-danger' : 'text-success'
      )}>
        {isIncrease ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
        {Math.abs(change).toFixed(1)}%
      </span>
    )
  }

  const renderMessageContent = (message: NegotiationMessage) => {
    const { content } = message

    if (message.type === 'ai-reasoning' && content.reasoning) {
      return (
        <AIReasoningBox
          reasoning={content.reasoning}
          confidence={content.confidence}
          variant="default"
          expandable={true}
          defaultExpanded={expandedMessages.has(message.id)}
        />
      )
    }

    return (
      <div className="space-y-2">
        {content.text && (
          <p className="text-sm text-text-primary">{content.text}</p>
        )}

        {content.price && (
          <div className="flex items-center gap-3 p-3 bg-background-secondary rounded-sm">
            <DollarSign className="h-4 w-4 text-text-tertiary" />
            <div className="flex-1">
              <div className="flex items-baseline gap-2">
                <span className="text-lg font-bold text-text-primary">
                  ${content.price.toLocaleString()}
                </span>
                {content.discount && (
                  <span className="text-sm text-success font-medium">
                    {content.discount}% off
                  </span>
                )}
                {getPriceChangeIndicator(content.price, content.previousPrice)}
              </div>
            </div>
          </div>
        )}

        {content.terms && content.terms.length > 0 && (
          <div className="space-y-1">
            <p className="text-xs font-medium text-text-secondary uppercase tracking-wider">
              Terms
            </p>
            <ul className="space-y-1">
              {content.terms.map((term, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-text-secondary">
                  <CheckCircle className="h-3 w-3 text-success mt-0.5" />
                  <span>{term}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {content.reasoning && message.type !== 'ai-reasoning' && (
          <div className="p-3 bg-ai-bg border-l-2 border-ai-primary rounded-sm">
            <p className="text-xs text-ai-primary font-medium mb-1">AI Reasoning</p>
            <p className="text-sm text-text-secondary">{content.reasoning}</p>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-surface-raised border border-border-subtle rounded-sm">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border-subtle">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-semibold text-text-primary">
            Negotiation Feed
          </h3>
          {currentRound && maxRounds && (
            <span className="text-xs text-text-tertiary">
              Round {currentRound} of {maxRounds}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {status === 'active' && (
            <span className="flex items-center gap-1.5 px-2 py-1 bg-success-bg text-success text-xs font-medium rounded-full">
              <span className="w-1.5 h-1.5 bg-success rounded-full animate-pulse" />
              Live
            </span>
          )}
          {status === 'paused' && (
            <span className="flex items-center gap-1.5 px-2 py-1 bg-warning-bg text-warning text-xs font-medium rounded-full">
              <Clock className="h-3 w-3" />
              Paused
            </span>
          )}
          {status === 'completed' && (
            <span className="flex items-center gap-1.5 px-2 py-1 bg-info-bg text-info text-xs font-medium rounded-full">
              <CheckCircle className="h-3 w-3" />
              Complete
            </span>
          )}
        </div>
      </div>

      {/* Messages */}
      <div
        ref={feedRef}
        className="flex-1 overflow-y-auto p-4 space-y-4"
        style={{ maxHeight: '600px' }}
      >
        {messages.map((message, index) => {
          const Icon = getMessageIcon(message)
          const isExpanded = expandedMessages.has(message.id)

          return (
            <div
              key={message.id}
              className={clsx(
                'flex gap-3',
                message.sender === 'buyer' && 'flex-row-reverse',
                compactMode && 'py-2'
              )}
            >
              {/* Avatar */}
              <div className={clsx(
                'flex-shrink-0 w-8 h-8 rounded-sm flex items-center justify-center',
                message.sender === 'buyer' ? 'bg-brand-primary/10' :
                message.sender === 'seller' ? 'bg-warning/10' :
                'bg-background-tertiary'
              )}>
                {message.sender === 'buyer' ? (
                  <User className={clsx('h-4 w-4', getMessageColor(message))} />
                ) : message.sender === 'seller' ? (
                  <Building className={clsx('h-4 w-4', getMessageColor(message))} />
                ) : (
                  <Icon className={clsx('h-4 w-4', getMessageColor(message))} />
                )}
              </div>

              {/* Message Content */}
              <div className={clsx(
                'flex-1 max-w-lg',
                message.sender === 'buyer' && 'text-right'
              )}>
                {/* Header */}
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium text-text-secondary">
                    {message.sender === 'buyer' ? 'You' :
                     message.vendorName || 'Vendor'}
                  </span>
                  {message.round && (
                    <span className="text-xs text-text-tertiary">
                      • Round {message.round}
                    </span>
                  )}
                  {showTimestamps && (
                    <span className="text-xs text-text-tertiary">
                      • {formatDistanceToNow(message.timestamp, { addSuffix: true })}
                    </span>
                  )}
                </div>

                {/* Message Body */}
                <div
                  className={clsx(
                    'rounded-sm p-3 cursor-pointer transition-all',
                    message.sender === 'buyer' 
                      ? 'bg-brand-primary/10 border border-brand-primary/20 ml-auto'
                      : message.sender === 'seller'
                      ? 'bg-warning/10 border border-warning/20'
                      : 'bg-background-secondary border border-border-subtle',
                    onMessageClick && 'hover:shadow-low'
                  )}
                  onClick={() => {
                    if (message.type === 'ai-reasoning') {
                      toggleExpanded(message.id)
                    } else if (onMessageClick) {
                      onMessageClick(message)
                    }
                  }}
                >
                  {renderMessageContent(message)}
                </div>

                {/* Status */}
                {message.status && (
                  <div className={clsx(
                    'flex items-center gap-1 mt-1',
                    message.sender === 'buyer' && 'justify-end'
                  )}>
                    {message.status === 'accepted' && (
                      <>
                        <CheckCircle className="h-3 w-3 text-success" />
                        <span className="text-xs text-success">Accepted</span>
                      </>
                    )}
                    {message.status === 'rejected' && (
                      <>
                        <XCircle className="h-3 w-3 text-danger" />
                        <span className="text-xs text-danger">Rejected</span>
                      </>
                    )}
                    {message.status === 'pending' && (
                      <>
                        <Clock className="h-3 w-3 text-text-tertiary" />
                        <span className="text-xs text-text-tertiary">Pending</span>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ============================================================================
// Negotiation Summary Component
// ============================================================================

export interface NegotiationSummaryProps {
  startPrice: number
  currentPrice: number
  bestPrice: number
  rounds: number
  timeElapsed: string
  savings: number
  vendorCount: number
}

export const NegotiationSummary: React.FC<NegotiationSummaryProps> = ({
  startPrice,
  currentPrice,
  bestPrice,
  rounds,
  timeElapsed,
  savings,
  vendorCount,
}) => {
  const savingsPercentage = ((savings / startPrice) * 100).toFixed(1)

  return (
    <div className="bg-surface-raised border border-border-subtle rounded-sm p-6">
      <h3 className="text-sm font-semibold text-text-primary mb-4">
        Negotiation Summary
      </h3>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-text-tertiary mb-1">Starting Price</p>
          <p className="text-lg font-bold text-text-primary">
            ${startPrice.toLocaleString()}
          </p>
        </div>
        <div>
          <p className="text-xs text-text-tertiary mb-1">Current Best</p>
          <p className="text-lg font-bold text-success">
            ${bestPrice.toLocaleString()}
          </p>
        </div>
        <div>
          <p className="text-xs text-text-tertiary mb-1">Total Savings</p>
          <p className="text-lg font-bold text-success">
            ${savings.toLocaleString()} ({savingsPercentage}%)
          </p>
        </div>
        <div>
          <p className="text-xs text-text-tertiary mb-1">Rounds Completed</p>
          <p className="text-lg font-bold text-text-primary">{rounds}</p>
        </div>
        <div>
          <p className="text-xs text-text-tertiary mb-1">Time Elapsed</p>
          <p className="text-lg font-bold text-text-primary">{timeElapsed}</p>
        </div>
        <div>
          <p className="text-xs text-text-tertiary mb-1">Vendors Engaged</p>
          <p className="text-lg font-bold text-text-primary">{vendorCount}</p>
        </div>
      </div>
    </div>
  )
}

import { XCircle } from 'lucide-react'
