/**
 * Enhanced Portfolio Management
 * Comprehensive contract and subscription management with analytics
 */

import React, { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  Calendar,
  Users,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  PieChart,
  Activity,
  RefreshCw,
  Download,
  Upload,
  Settings,
  Flag,
  X,
  ChevronDown,
  ChevronUp,
  Filter,
  Search,
  Building,
  FileText,
  Zap,
  Shield,
} from 'lucide-react'
import {
  Card,
  Button,
  Badge,
  Alert,
  Tabs,
  Tab,
  Input,
  ProgressBar,
} from '../../components/ui/DesignSystem'
import { EnhancedMetricCard, MetricCardGrid } from '../../components/ui/EnhancedMetricCard'
import { AIReasoningBox, AISuggestionCard } from '../../components/ui/AIReasoningBox'
import { api } from '../../lib/api'
import { toast } from '../../lib/toast'
import { format, addMonths, differenceInDays, isWithinInterval } from 'date-fns'
import clsx from 'clsx'

interface Subscription {
  id: string
  vendor: {
    name: string
    logo?: string
    category: string
  }
  product: {
    name: string
    description: string
    category: string
  }
  contract: {
    id: string
    value: number
    start_date: string
    end_date: string
    auto_renew: boolean
    notice_period_days: number
  }
  usage: {
    licensed_seats: number
    active_users: number
    utilization_percentage: number
    last_activity: string
    trend: 'increasing' | 'stable' | 'decreasing'
  }
  costs: {
    monthly_cost: number
    annual_cost: number
    cost_per_user: number
    total_spent: number
  }
  status: 'active' | 'expiring' | 'expired' | 'cancelled'
  renewal_date: string
  risk_factors?: string[]
  optimization_opportunities?: string[]
}

interface PortfolioMetrics {
  total_contracts: number
  total_annual_spend: number
  total_monthly_spend: number
  average_utilization: number
  contracts_expiring_30d: number
  contracts_expiring_90d: number
  underutilized_contracts: number
  optimization_potential: number
  vendor_concentration: Array<{
    vendor: string
    spend: number
    percentage: number
  }>
  category_breakdown: Array<{
    category: string
    count: number
    spend: number
  }>
}

export function EnhancedPortfolio() {
  const queryClient = useQueryClient()
  const [selectedView, setSelectedView] = useState<'grid' | 'table'>('grid')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedSubscriptions, setSelectedSubscriptions] = useState<Set<string>>(new Set())
  const [bulkAction, setBulkAction] = useState<string>('')

  // Fetch portfolio data
  const { data: subscriptions, isLoading: subscriptionsLoading } = useQuery<Subscription[]>({
    queryKey: ['portfolio-subscriptions'],
    queryFn: async () => {
      const response = await api.get('/api/portfolio/subscriptions')
      return response.data
    },
    refetchInterval: 60000, // Refresh every minute
  })

  // Fetch portfolio metrics
  const { data: metrics, isLoading: metricsLoading } = useQuery<PortfolioMetrics>({
    queryKey: ['portfolio-metrics'],
    queryFn: async () => {
      const response = await api.get('/api/portfolio/metrics')
      return response.data
    },
  })

  // Flag for renegotiation mutation
  const flagMutation = useMutation({
    mutationFn: async (subscriptionId: string) => {
      const response = await api.post(`/api/portfolio/subscriptions/${subscriptionId}/flag`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio-subscriptions'] })
      toast.success('Subscription flagged for renegotiation')
    },
  })

  // Cancel subscription mutation
  const cancelMutation = useMutation({
    mutationFn: async (subscriptionId: string) => {
      const response = await api.post(`/api/portfolio/subscriptions/${subscriptionId}/cancel`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio-subscriptions'] })
      toast.success('Cancellation request submitted')
    },
  })

  // Bulk action mutation
  const bulkActionMutation = useMutation({
    mutationFn: async (data: { action: string; subscriptionIds: string[] }) => {
      const response = await api.post('/api/portfolio/bulk-action', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio-subscriptions'] })
      toast.success('Bulk action completed')
      setSelectedSubscriptions(new Set())
      setBulkAction('')
    },
  })

  // Filter subscriptions
  const filteredSubscriptions = useMemo(() => {
    if (!subscriptions) return []
    
    return subscriptions.filter(sub => {
      // Category filter
      if (selectedCategory !== 'all' && sub.product.category !== selectedCategory) {
        return false
      }
      
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        return (
          sub.vendor.name.toLowerCase().includes(query) ||
          sub.product.name.toLowerCase().includes(query) ||
          sub.product.description.toLowerCase().includes(query)
        )
      }
      
      return true
    })
  }, [subscriptions, selectedCategory, searchQuery])

  // Group subscriptions by status
  const groupedSubscriptions = useMemo(() => {
    const groups = {
      expiring: [] as Subscription[],
      underutilized: [] as Subscription[],
      optimized: [] as Subscription[],
      all: filteredSubscriptions,
    }
    
    filteredSubscriptions.forEach(sub => {
      // Expiring soon (within 30 days)
      const daysUntilRenewal = differenceInDays(new Date(sub.renewal_date), new Date())
      if (daysUntilRenewal <= 30 && daysUntilRenewal > 0) {
        groups.expiring.push(sub)
      }
      
      // Underutilized (< 50% utilization)
      if (sub.usage.utilization_percentage < 50) {
        groups.underutilized.push(sub)
      }
      
      // Well optimized (> 80% utilization)
      if (sub.usage.utilization_percentage >= 80) {
        groups.optimized.push(sub)
      }
    })
    
    return groups
  }, [filteredSubscriptions])

  const handleSelectAll = () => {
    if (selectedSubscriptions.size === filteredSubscriptions.length) {
      setSelectedSubscriptions(new Set())
    } else {
      setSelectedSubscriptions(new Set(filteredSubscriptions.map(s => s.id)))
    }
  }

  const handleSelect = (id: string) => {
    const newSelection = new Set(selectedSubscriptions)
    if (newSelection.has(id)) {
      newSelection.delete(id)
    } else {
      newSelection.add(id)
    }
    setSelectedSubscriptions(newSelection)
  }

  const handleBulkAction = () => {
    if (!bulkAction || selectedSubscriptions.size === 0) return
    
    bulkActionMutation.mutate({
      action: bulkAction,
      subscriptionIds: Array.from(selectedSubscriptions),
    })
  }

  return (
    <div className="min-h-screen bg-background-primary">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-text-primary">Portfolio Management</h1>
            <p className="text-text-secondary mt-1">
              Manage {metrics?.total_contracts || 0} active contracts and subscriptions
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" icon={Download}>
              Export
            </Button>
            <Button variant="secondary" icon={Upload}>
              Import
            </Button>
            <Button variant="primary" icon={Zap}>
              Optimize Portfolio
            </Button>
          </div>
        </div>

        {/* AI Insights */}
        {metrics && metrics.optimization_potential > 10000 && (
          <AISuggestionCard
            title="Portfolio Optimization Opportunity"
            description={`Analysis shows potential savings of $${metrics.optimization_potential.toLocaleString()} through consolidation and renegotiation. ${metrics.underutilized_contracts} contracts are underutilized.`}
            actions={[
              {
                label: 'View Recommendations',
                onClick: () => console.log('View recommendations'),
                variant: 'primary',
              },
              {
                label: 'Start Optimization',
                onClick: () => console.log('Start optimization'),
                variant: 'secondary',
              },
            ]}
          />
        )}

        {/* Metrics */}
        <MetricCardGrid columns={{ mobile: 1, tablet: 2, desktop: 4 }}>
          <EnhancedMetricCard
            title="Annual Spend"
            value={`$${((metrics?.total_annual_spend || 0) / 1000000).toFixed(2)}M`}
            change={{ value: -8, type: 'percentage' }}
            trend="down"
            sparklineData={[2.1, 2.3, 2.2, 2.0, 1.9, 1.85, 1.8]}
            icon={DollarSign}
            loading={metricsLoading}
          />
          <EnhancedMetricCard
            title="Avg Utilization"
            value={`${metrics?.average_utilization || 0}%`}
            change={{ value: 5, type: 'percentage' }}
            trend="up"
            sparklineData={[65, 68, 70, 72, 74, 76, 78]}
            icon={Activity}
            variant={metrics?.average_utilization && metrics.average_utilization < 60 ? 'warning' : 'default'}
            loading={metricsLoading}
          />
          <EnhancedMetricCard
            title="Expiring Soon"
            value={metrics?.contracts_expiring_30d || 0}
            change={{ value: 2, type: 'absolute' }}
            trend="up"
            icon={Clock}
            variant={metrics?.contracts_expiring_30d && metrics.contracts_expiring_30d > 5 ? 'warning' : 'default'}
            loading={metricsLoading}
          />
          <EnhancedMetricCard
            title="Underutilized"
            value={metrics?.underutilized_contracts || 0}
            change={{ value: -3, type: 'absolute' }}
            trend="down"
            icon={AlertTriangle}
            variant="warning"
            loading={metricsLoading}
          />
        </MetricCardGrid>

        {/* Filters and Search */}
        <Card className="mt-6">
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 flex-1">
                <div className="relative flex-1 max-w-md">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary" />
                  <input
                    type="text"
                    placeholder="Search vendors, products, or categories..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-surface-sunken border border-border-subtle rounded-sm text-sm focus:outline-none focus:border-brand-primary"
                  />
                </div>
                <Button
                  variant="secondary"
                  icon={Filter}
                  onClick={() => setShowFilters(!showFilters)}
                >
                  Filters
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSelectedView('grid')}
                  className={clsx(
                    'p-2 rounded-sm',
                    selectedView === 'grid' ? 'bg-brand-primary text-text-inverse' : 'text-text-secondary hover:bg-background-secondary'
                  )}
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <rect x="3" y="3" width="7" height="7" strokeWidth="2" />
                    <rect x="14" y="3" width="7" height="7" strokeWidth="2" />
                    <rect x="3" y="14" width="7" height="7" strokeWidth="2" />
                    <rect x="14" y="14" width="7" height="7" strokeWidth="2" />
                  </svg>
                </button>
                <button
                  onClick={() => setSelectedView('table')}
                  className={clsx(
                    'p-2 rounded-sm',
                    selectedView === 'table' ? 'bg-brand-primary text-text-inverse' : 'text-text-secondary hover:bg-background-secondary'
                  )}
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <line x1="3" y1="6" x2="21" y2="6" strokeWidth="2" />
                    <line x1="3" y1="12" x2="21" y2="12" strokeWidth="2" />
                    <line x1="3" y1="18" x2="21" y2="18" strokeWidth="2" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Expanded Filters */}
            {showFilters && (
              <div className="mt-4 pt-4 border-t border-border-subtle">
                <div className="flex items-center gap-3">
                  <span className="text-sm text-text-secondary">Category:</span>
                  <div className="flex gap-2">
                    {['all', 'software', 'infrastructure', 'services', 'hardware'].map(cat => (
                      <button
                        key={cat}
                        onClick={() => setSelectedCategory(cat)}
                        className={clsx(
                          'px-3 py-1 text-sm rounded-sm capitalize',
                          selectedCategory === cat
                            ? 'bg-brand-primary text-text-inverse'
                            : 'bg-background-secondary text-text-secondary hover:bg-background-tertiary'
                        )}
                      >
                        {cat}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Bulk Actions */}
            {selectedSubscriptions.size > 0 && (
              <div className="mt-4 pt-4 border-t border-border-subtle">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-text-secondary">
                      {selectedSubscriptions.size} selected
                    </span>
                    <button
                      onClick={() => setSelectedSubscriptions(new Set())}
                      className="text-sm text-brand-primary hover:underline"
                    >
                      Clear selection
                    </button>
                  </div>
                  <div className="flex items-center gap-3">
                    <select
                      value={bulkAction}
                      onChange={(e) => setBulkAction(e.target.value)}
                      className="px-3 py-1.5 bg-surface-sunken border border-border-subtle rounded-sm text-sm"
                    >
                      <option value="">Select action...</option>
                      <option value="flag_renegotiation">Flag for Renegotiation</option>
                      <option value="request_cancellation">Request Cancellation</option>
                      <option value="export">Export Selected</option>
                    </select>
                    <Button
                      variant="primary"
                      size="small"
                      onClick={handleBulkAction}
                      disabled={!bulkAction}
                      loading={bulkActionMutation.isPending}
                    >
                      Apply
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Tabs */}
        <div className="mt-6">
          <Tabs value="all" onChange={() => {}}>
            <Tab value="all" label={`All (${filteredSubscriptions.length})`} />
            <Tab value="expiring" label={`Expiring (${groupedSubscriptions.expiring.length})`} />
            <Tab value="underutilized" label={`Underutilized (${groupedSubscriptions.underutilized.length})`} />
            <Tab value="optimized" label={`Optimized (${groupedSubscriptions.optimized.length})`} />
          </Tabs>

          {/* Subscriptions Grid/Table */}
          <div className="mt-6">
            {selectedView === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredSubscriptions.map(subscription => (
                  <SubscriptionCard
                    key={subscription.id}
                    subscription={subscription}
                    selected={selectedSubscriptions.has(subscription.id)}
                    onSelect={() => handleSelect(subscription.id)}
                    onFlag={() => flagMutation.mutate(subscription.id)}
                    onCancel={() => cancelMutation.mutate(subscription.id)}
                  />
                ))}
              </div>
            ) : (
              <SubscriptionTable
                subscriptions={filteredSubscriptions}
                selectedSubscriptions={selectedSubscriptions}
                onSelectAll={handleSelectAll}
                onSelect={handleSelect}
                onFlag={(id) => flagMutation.mutate(id)}
                onCancel={(id) => cancelMutation.mutate(id)}
              />
            )}

            {filteredSubscriptions.length === 0 && (
              <div className="text-center py-12">
                <Building className="h-12 w-12 text-text-tertiary mx-auto mb-3" />
                <p className="text-text-secondary">No subscriptions found</p>
                <p className="text-sm text-text-tertiary mt-1">
                  Try adjusting your filters or search query
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Subscription Card Component
interface SubscriptionCardProps {
  subscription: Subscription
  selected: boolean
  onSelect: () => void
  onFlag: () => void
  onCancel: () => void
}

const SubscriptionCard: React.FC<SubscriptionCardProps> = ({
  subscription,
  selected,
  onSelect,
  onFlag,
  onCancel,
}) => {
  const daysUntilRenewal = differenceInDays(new Date(subscription.renewal_date), new Date())
  const isExpiringSoon = daysUntilRenewal <= 30 && daysUntilRenewal > 0
  const isUnderutilized = subscription.usage.utilization_percentage < 50

  return (
    <Card
      hover
      className={clsx(
        'relative overflow-hidden',
        selected && 'ring-2 ring-brand-primary'
      )}
    >
      {/* Selection Checkbox */}
      <div className="absolute top-4 left-4">
        <input
          type="checkbox"
          checked={selected}
          onChange={onSelect}
          className="h-4 w-4 text-brand-primary rounded border-border-medium"
        />
      </div>

      {/* Status Indicator */}
      {(isExpiringSoon || isUnderutilized) && (
        <div className="absolute top-0 right-0 p-2">
          {isExpiringSoon && (
            <Badge variant="warning" size="small">
              Expires in {daysUntilRenewal}d
            </Badge>
          )}
          {isUnderutilized && (
            <Badge variant="danger" size="small">
              Low usage
            </Badge>
          )}
        </div>
      )}

      <div className="p-6 pt-10">
        {/* Vendor & Product */}
        <div className="flex items-start gap-3 mb-4">
          {subscription.vendor.logo ? (
            <img
              src={subscription.vendor.logo}
              alt={subscription.vendor.name}
              className="w-10 h-10 rounded-sm object-cover"
            />
          ) : (
            <div className="w-10 h-10 bg-background-secondary rounded-sm flex items-center justify-center">
              <Building className="h-5 w-5 text-text-tertiary" />
            </div>
          )}
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-text-primary">
              {subscription.product.name}
            </h3>
            <p className="text-xs text-text-secondary">{subscription.vendor.name}</p>
          </div>
        </div>

        {/* Metrics */}
        <div className="space-y-3">
          {/* Cost */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-text-secondary">Monthly Cost</span>
            <span className="text-sm font-semibold text-text-primary">
              ${subscription.costs.monthly_cost.toLocaleString()}
            </span>
          </div>

          {/* Utilization */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-text-secondary">Utilization</span>
              <span className="text-sm font-medium text-text-primary">
                {subscription.usage.active_users}/{subscription.usage.licensed_seats} users
              </span>
            </div>
            <ProgressBar
              value={subscription.usage.utilization_percentage}
              variant={
                subscription.usage.utilization_percentage >= 80 ? 'success' :
                subscription.usage.utilization_percentage >= 50 ? 'warning' : 'danger'
              }
              size="small"
            />
          </div>

          {/* Renewal */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-text-secondary">Renewal</span>
            <span className="text-sm text-text-primary">
              {format(new Date(subscription.renewal_date), 'MMM d, yyyy')}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-4 pt-4 border-t border-border-subtle flex gap-2">
          <Button variant="secondary" size="small" fullWidth onClick={onFlag}>
            <Flag className="h-3 w-3" />
            Renegotiate
          </Button>
          <Button variant="secondary" size="small" fullWidth onClick={onCancel}>
            <X className="h-3 w-3" />
            Cancel
          </Button>
        </div>
      </div>
    </Card>
  )
}

// Subscription Table Component
interface SubscriptionTableProps {
  subscriptions: Subscription[]
  selectedSubscriptions: Set<string>
  onSelectAll: () => void
  onSelect: (id: string) => void
  onFlag: (id: string) => void
  onCancel: (id: string) => void
}

const SubscriptionTable: React.FC<SubscriptionTableProps> = ({
  subscriptions,
  selectedSubscriptions,
  onSelectAll,
  onSelect,
  onFlag,
  onCancel,
}) => {
  return (
    <Card padding="none">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border-subtle bg-background-secondary">
              <th className="p-4">
                <input
                  type="checkbox"
                  checked={selectedSubscriptions.size === subscriptions.length}
                  onChange={onSelectAll}
                  className="h-4 w-4 text-brand-primary rounded border-border-medium"
                />
              </th>
              <th className="text-left p-4 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Product
              </th>
              <th className="text-left p-4 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Cost
              </th>
              <th className="text-left p-4 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Utilization
              </th>
              <th className="text-left p-4 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Renewal
              </th>
              <th className="text-left p-4 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Status
              </th>
              <th className="text-left p-4 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {subscriptions.map(subscription => {
              const daysUntilRenewal = differenceInDays(new Date(subscription.renewal_date), new Date())
              const isExpiringSoon = daysUntilRenewal <= 30 && daysUntilRenewal > 0

              return (
                <tr key={subscription.id} className="border-b border-border-subtle hover:bg-background-secondary">
                  <td className="p-4">
                    <input
                      type="checkbox"
                      checked={selectedSubscriptions.has(subscription.id)}
                      onChange={() => onSelect(subscription.id)}
                      className="h-4 w-4 text-brand-primary rounded border-border-medium"
                    />
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      {subscription.vendor.logo ? (
                        <img
                          src={subscription.vendor.logo}
                          alt={subscription.vendor.name}
                          className="w-8 h-8 rounded-sm object-cover"
                        />
                      ) : (
                        <div className="w-8 h-8 bg-background-tertiary rounded-sm flex items-center justify-center">
                          <Building className="h-4 w-4 text-text-tertiary" />
                        </div>
                      )}
                      <div>
                        <p className="text-sm font-medium text-text-primary">
                          {subscription.product.name}
                        </p>
                        <p className="text-xs text-text-secondary">
                          {subscription.vendor.name}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <p className="text-sm font-medium text-text-primary">
                      ${subscription.costs.monthly_cost.toLocaleString()}/mo
                    </p>
                    <p className="text-xs text-text-secondary">
                      ${subscription.costs.annual_cost.toLocaleString()}/yr
                    </p>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <ProgressBar
                        value={subscription.usage.utilization_percentage}
                        variant={
                          subscription.usage.utilization_percentage >= 80 ? 'success' :
                          subscription.usage.utilization_percentage >= 50 ? 'warning' : 'danger'
                        }
                        size="small"
                      />
                      <span className="text-sm text-text-secondary">
                        {subscription.usage.utilization_percentage}%
                      </span>
                    </div>
                  </td>
                  <td className="p-4">
                    <p className="text-sm text-text-primary">
                      {format(new Date(subscription.renewal_date), 'MMM d, yyyy')}
                    </p>
                    {isExpiringSoon && (
                      <p className="text-xs text-warning">
                        {daysUntilRenewal} days
                      </p>
                    )}
                  </td>
                  <td className="p-4">
                    <Badge
                      variant={
                        subscription.status === 'active' ? 'success' :
                        subscription.status === 'expiring' ? 'warning' : 'danger'
                      }
                      size="small"
                    >
                      {subscription.status}
                    </Badge>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => onFlag(subscription.id)}
                        className="p-1 hover:bg-background-tertiary rounded-sm"
                        title="Flag for renegotiation"
                      >
                        <Flag className="h-4 w-4 text-text-secondary" />
                      </button>
                      <button
                        onClick={() => onCancel(subscription.id)}
                        className="p-1 hover:bg-background-tertiary rounded-sm"
                        title="Request cancellation"
                      >
                        <X className="h-4 w-4 text-text-secondary" />
                      </button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </Card>
  )
}
