/**
 * Enhanced Seller Dashboard
 * Complete seller portal experience with real-time data and analytics
 */

import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  Target,
  AlertTriangle,
  Activity,
  BarChart3,
  Settings,
  MessageSquare,
  Clock,
  CheckCircle,
  XCircle,
  Zap,
  Shield,
  Brain,
  MapPin,
} from 'lucide-react'
import { EnhancedMetricCard, MetricCardGrid } from '../../components/ui/EnhancedMetricCard'
import { Card, Button, Badge, Alert, Tabs, Tab, ProgressBar } from '../../components/ui/DesignSystem'
import { AIActivityIndicator, AISuggestionCard } from '../../components/ui/AIReasoningBox'
import { NegotiationFeed, NegotiationSummary } from '../../components/negotiation/NegotiationFeed'
import { api } from '../../lib/api'
import { formatDistanceToNow } from 'date-fns'

interface SellerMetrics {
  pipeline_value: number
  pipeline_change: number
  active_deals: number
  active_deals_change: number
  win_rate: number
  win_rate_change: number
  avg_deal_size: number
  avg_deal_size_change: number
  deals_at_risk: number
  avg_negotiation_rounds: number
  time_to_close: number
  vendor_score: number
}

interface Deal {
  id: string
  buyer_company: string
  buyer_contact: string
  status: 'negotiating' | 'stalled' | 'won' | 'lost' | 'pending'
  current_round: number
  max_rounds: number
  amount: number
  created_at: string
  updated_at: string
  ai_confidence: number
  next_action?: string
  risk_factors?: string[]
}

export function EnhancedSellerDashboard() {
  const [selectedTimeRange, setSelectedTimeRange] = useState<'7d' | '30d' | '90d'>('30d')
  const [aiStatus, setAiStatus] = useState<'idle' | 'thinking' | 'negotiating' | 'analyzing'>('idle')
  const [selectedDeal, setSelectedDeal] = useState<Deal | null>(null)

  // Fetch seller metrics
  const { data: metrics, isLoading: metricsLoading } = useQuery<SellerMetrics>({
    queryKey: ['seller-metrics', selectedTimeRange],
    queryFn: async () => {
      const response = await api.get(`/api/seller/metrics?range=${selectedTimeRange}`)
      return response.data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  // Fetch active deals
  const { data: deals, isLoading: dealsLoading } = useQuery<Deal[]>({
    queryKey: ['seller-deals'],
    queryFn: async () => {
      const response = await api.get('/api/seller/deals')
      return response.data
    },
    refetchInterval: 10000, // Refresh every 10 seconds for real-time updates
  })

  // Fetch negotiation messages for selected deal
  const { data: negotiationMessages } = useQuery({
    queryKey: ['negotiation-messages', selectedDeal?.id],
    queryFn: async () => {
      if (!selectedDeal) return []
      const response = await api.get(`/api/negotiations/${selectedDeal.id}/messages`)
      return response.data
    },
    enabled: !!selectedDeal,
  })

  // Simulate AI status changes
  useEffect(() => {
    const interval = setInterval(() => {
      const statuses: Array<'idle' | 'thinking' | 'negotiating' | 'analyzing'> = 
        ['idle', 'thinking', 'negotiating', 'analyzing']
      setAiStatus(statuses[Math.floor(Math.random() * statuses.length)])
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const dealsAtRisk = deals?.filter(d => d.status === 'stalled') || []
  const activeNegotiations = deals?.filter(d => d.status === 'negotiating') || []
  const recentWins = deals?.filter(d => d.status === 'won') || []

  return (
    <div className="min-h-screen bg-background-primary">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-text-primary">Seller Command Center</h1>
            <p className="text-text-secondary mt-1">
              Your AI agent is managing {activeNegotiations.length} active negotiations
            </p>
          </div>
          <div className="flex items-center gap-3">
            <AIActivityIndicator status={aiStatus} />
            <Button
              variant="secondary"
              icon={Settings}
              onClick={() => window.location.href = '/seller/guardrails'}
            >
              Configure Guardrails
            </Button>
          </div>
        </div>

        {/* Time Range Selector */}
        <div className="flex items-center gap-2 mb-6">
          <span className="text-sm text-text-secondary">Time Range:</span>
          <div className="flex gap-1 bg-background-secondary rounded-sm p-1">
            {(['7d', '30d', '90d'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setSelectedTimeRange(range)}
                className={clsx(
                  'px-3 py-1.5 text-sm font-medium rounded-sm transition-all',
                  selectedTimeRange === range
                    ? 'bg-brand-primary text-text-inverse'
                    : 'text-text-secondary hover:text-text-primary'
                )}
              >
                {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
              </button>
            ))}
          </div>
        </div>

        {/* Key Metrics */}
        <MetricCardGrid columns={{ mobile: 1, tablet: 2, desktop: 4 }}>
          <EnhancedMetricCard
            title="Pipeline Value"
            value={`$${((metrics?.pipeline_value || 0) / 1000000).toFixed(2)}M`}
            change={{
              value: metrics?.pipeline_change || 0,
              type: 'percentage'
            }}
            trend={metrics?.pipeline_change ? (metrics.pipeline_change > 0 ? 'up' : 'down') : 'neutral'}
            sparklineData={[65, 72, 68, 75, 82, 88, 95]}
            icon={DollarSign}
            loading={metricsLoading}
          />
          <EnhancedMetricCard
            title="Win Rate"
            value={`${metrics?.win_rate || 0}%`}
            change={{
              value: metrics?.win_rate_change || 0,
              type: 'percentage'
            }}
            trend={metrics?.win_rate_change ? (metrics.win_rate_change > 0 ? 'up' : 'down') : 'neutral'}
            sparklineData={[38, 42, 40, 45, 42, 48, 52]}
            icon={Target}
            variant={metrics?.win_rate && metrics.win_rate > 50 ? 'success' : 'default'}
            loading={metricsLoading}
          />
          <EnhancedMetricCard
            title="Active Deals"
            value={metrics?.active_deals || 0}
            change={{
              value: metrics?.active_deals_change || 0,
              type: 'absolute'
            }}
            trend={metrics?.active_deals_change ? (metrics.active_deals_change > 0 ? 'up' : 'down') : 'neutral'}
            icon={MessageSquare}
            loading={metricsLoading}
          />
          <EnhancedMetricCard
            title="Avg Deal Size"
            value={`$${((metrics?.avg_deal_size || 0) / 1000).toFixed(0)}K`}
            change={{
              value: metrics?.avg_deal_size_change || 0,
              type: 'percentage'
            }}
            trend={metrics?.avg_deal_size_change ? (metrics.avg_deal_size_change > 0 ? 'up' : 'down') : 'neutral'}
            icon={BarChart3}
            loading={metricsLoading}
          />
        </MetricCardGrid>

        {/* AI Suggestions */}
        {dealsAtRisk.length > 0 && (
          <div className="mt-6">
            <AISuggestionCard
              title="Deals Need Attention"
              description={`${dealsAtRisk.length} deals have been stalled for over 48 hours. Your AI agent recommends manual intervention to move these forward.`}
              actions={[
                {
                  label: 'Review Deals',
                  onClick: () => console.log('Review deals'),
                  variant: 'primary'
                },
                {
                  label: 'Adjust Strategy',
                  onClick: () => window.location.href = '/seller/guardrails',
                  variant: 'secondary'
                }
              ]}
            />
          </div>
        )}

        {/* Main Content Area */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Active Negotiations Feed */}
          <div className="lg:col-span-2">
            <Card padding="none">
              <div className="p-6 border-b border-border-subtle">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-text-primary">Live Negotiations</h2>
                  <Badge variant="success" size="small">
                    {activeNegotiations.length} Active
                  </Badge>
                </div>
              </div>
              
              <div className="p-6">
                <Tabs value={selectedDeal?.id || 'overview'} onChange={(id) => {
                  const deal = deals?.find(d => d.id === id)
                  setSelectedDeal(deal || null)
                }}>
                  <Tab value="overview" label="Overview" />
                  {activeNegotiations.slice(0, 3).map(deal => (
                    <Tab key={deal.id} value={deal.id} label={deal.buyer_company} />
                  ))}
                </Tabs>

                <div className="mt-6">
                  {selectedDeal ? (
                    <div className="space-y-6">
                      {/* Deal Summary */}
                      <div className="grid grid-cols-2 gap-4 p-4 bg-background-secondary rounded-sm">
                        <div>
                          <p className="text-xs text-text-tertiary">Current Value</p>
                          <p className="text-lg font-bold text-text-primary">
                            ${selectedDeal.amount.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-text-tertiary">Round</p>
                          <p className="text-lg font-bold text-text-primary">
                            {selectedDeal.current_round} / {selectedDeal.max_rounds}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-text-tertiary">AI Confidence</p>
                          <div className="mt-1">
                            <ProgressBar
                              value={selectedDeal.ai_confidence}
                              variant={selectedDeal.ai_confidence > 70 ? 'success' : 'warning'}
                              showLabel
                            />
                          </div>
                        </div>
                        <div>
                          <p className="text-xs text-text-tertiary">Next Action</p>
                          <p className="text-sm font-medium text-text-primary">
                            {selectedDeal.next_action || 'Awaiting response'}
                          </p>
                        </div>
                      </div>

                      {/* Negotiation Feed */}
                      {negotiationMessages && (
                        <NegotiationFeed
                          messages={negotiationMessages}
                          currentRound={selectedDeal.current_round}
                          maxRounds={selectedDeal.max_rounds}
                          status="active"
                          compactMode
                        />
                      )}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {activeNegotiations.map(deal => (
                        <DealCard
                          key={deal.id}
                          deal={deal}
                          onClick={() => setSelectedDeal(deal)}
                        />
                      ))}
                      {activeNegotiations.length === 0 && (
                        <div className="text-center py-8">
                          <MessageSquare className="h-12 w-12 text-text-tertiary mx-auto mb-3" />
                          <p className="text-text-secondary">No active negotiations</p>
                          <p className="text-sm text-text-tertiary mt-1">
                            Your AI agent will start negotiating when new requests come in
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </Card>
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            {/* Performance Stats */}
            <Card>
              <h3 className="text-sm font-semibold text-text-primary mb-4">
                AI Agent Performance
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-secondary">Avg Rounds</span>
                  <span className="text-sm font-medium text-text-primary">
                    {metrics?.avg_negotiation_rounds?.toFixed(1) || '-'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-secondary">Time to Close</span>
                  <span className="text-sm font-medium text-text-primary">
                    {metrics?.time_to_close || '-'} hrs
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-secondary">Vendor Score</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-text-primary">
                      {metrics?.vendor_score || '-'}/100
                    </span>
                    <Badge
                      variant={
                        metrics?.vendor_score && metrics.vendor_score > 80 ? 'success' :
                        metrics?.vendor_score && metrics.vendor_score > 60 ? 'warning' : 'danger'
                      }
                      size="small"
                    >
                      {metrics?.vendor_score && metrics.vendor_score > 80 ? 'Excellent' :
                       metrics?.vendor_score && metrics.vendor_score > 60 ? 'Good' : 'Needs Work'}
                    </Badge>
                  </div>
                </div>
              </div>
            </Card>

            {/* Recent Wins */}
            <Card>
              <h3 className="text-sm font-semibold text-text-primary mb-4">
                Recent Wins
              </h3>
              <div className="space-y-3">
                {recentWins.slice(0, 3).map(deal => (
                  <div key={deal.id} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-text-primary">
                        {deal.buyer_company}
                      </p>
                      <p className="text-xs text-text-tertiary">
                        ${(deal.amount / 1000).toFixed(0)}K • {formatDistanceToNow(new Date(deal.updated_at), { addSuffix: true })}
                      </p>
                    </div>
                    <CheckCircle className="h-4 w-4 text-success" />
                  </div>
                ))}
                {recentWins.length === 0 && (
                  <p className="text-sm text-text-tertiary text-center py-2">
                    No recent wins
                  </p>
                )}
              </div>
            </Card>

            {/* Quick Actions */}
            <Card>
              <h3 className="text-sm font-semibold text-text-primary mb-4">
                Quick Actions
              </h3>
              <div className="space-y-2">
                <Button
                  fullWidth
                  variant="secondary"
                  icon={Shield}
                  onClick={() => window.location.href = '/seller/guardrails'}
                >
                  Adjust Guardrails
                </Button>
                <Button
                  fullWidth
                  variant="secondary"
                  icon={Brain}
                  onClick={() => window.location.href = '/seller/intelligence'}
                >
                  View Intelligence
                </Button>
                <Button
                  fullWidth
                  variant="secondary"
                  icon={MapPin}
                  onClick={() => window.location.href = '/seller/territory'}
                >
                  Manage Territory
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

// Deal Card Component
interface DealCardProps {
  deal: Deal
  onClick: () => void
}

const DealCard: React.FC<DealCardProps> = ({ deal, onClick }) => {
  const getStatusColor = () => {
    switch (deal.status) {
      case 'negotiating':
        return 'border-l-ai-primary'
      case 'stalled':
        return 'border-l-warning'
      case 'won':
        return 'border-l-success'
      case 'lost':
        return 'border-l-danger'
      default:
        return 'border-l-border-medium'
    }
  }

  return (
    <div
      className={clsx(
        'p-4 bg-background-secondary rounded-sm border-l-4 cursor-pointer transition-all hover:shadow-low',
        getStatusColor()
      )}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-semibold text-text-primary">
              {deal.buyer_company}
            </h4>
            <Badge
              variant={
                deal.status === 'negotiating' ? 'info' :
                deal.status === 'stalled' ? 'warning' :
                deal.status === 'won' ? 'success' : 'danger'
              }
              size="small"
            >
              {deal.status}
            </Badge>
          </div>
          <p className="text-xs text-text-tertiary mt-1">
            {deal.buyer_contact} • Round {deal.current_round}/{deal.max_rounds}
          </p>
          <div className="flex items-center gap-4 mt-2">
            <span className="text-sm font-medium text-text-primary">
              ${(deal.amount / 1000).toFixed(0)}K
            </span>
            <span className="text-xs text-text-tertiary">
              Updated {formatDistanceToNow(new Date(deal.updated_at), { addSuffix: true })}
            </span>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-text-tertiary">AI Confidence</p>
          <p className="text-lg font-bold text-text-primary">{deal.ai_confidence}%</p>
        </div>
      </div>
      {deal.risk_factors && deal.risk_factors.length > 0 && (
        <div className="mt-3 flex items-center gap-2">
          <AlertTriangle className="h-3 w-3 text-warning" />
          <p className="text-xs text-warning">
            {deal.risk_factors.join(', ')}
          </p>
        </div>
      )}
    </div>
  )
}

import clsx from 'clsx'
