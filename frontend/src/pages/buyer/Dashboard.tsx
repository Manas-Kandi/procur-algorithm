import { useQuery } from '@tanstack/react-query'
import { api } from '../../services/api'
import { MetricCard } from '../../components/shared/MetricCard'
import { Card } from '../../components/shared/Card'
import { StatusBadge } from '../../components/shared/StatusBadge'
import { Button } from '../../components/shared/Button'
import { useNavigate } from 'react-router-dom'
import type { Request } from '../../types'

export function BuyerDashboard() {
  const navigate = useNavigate()

  const { data: metrics } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: () => api.getDashboardMetrics(),
  })

  const { data: requests } = useQuery({
    queryKey: ['requests'],
    queryFn: () => api.getRequests(),
  })

  const { data: renewals } = useQuery({
    queryKey: ['renewals'],
    queryFn: () => api.getUpcomingRenewals(60),
  })

  const { data: approvals } = useQuery({
    queryKey: ['pending-approvals'],
    queryFn: () => api.getPendingApprovals(),
  })

  // Group requests by status for Kanban board
  const requestsByStatus = requests?.reduce((acc, req) => {
    if (!acc[req.status]) acc[req.status] = []
    acc[req.status].push(req)
    return acc
  }, {} as Record<string, Request[]>) || {}

  const columns = [
    { status: 'draft', label: 'Draft' },
    { status: 'sourcing', label: 'Sourcing' },
    { status: 'negotiating', label: 'Negotiating' },
    { status: 'approving', label: 'Approving' },
    { status: 'contracted', label: 'Contracted' },
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back! Here's your procurement overview.</p>
        </div>
        <Button onClick={() => navigate('/requests/new')}>
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Request
        </Button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Requests"
          value={metrics?.active_requests || 0}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          }
        />
        <MetricCard
          title="Pending Approvals"
          value={metrics?.pending_approvals || 0}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
          onClick={() => navigate('/approvals')}
        />
        <MetricCard
          title="Upcoming Renewals"
          value={metrics?.upcoming_renewals || 0}
          subtitle="Next 60 days"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        <MetricCard
          title="Monthly Spend"
          value={`$${((metrics?.monthly_spend || 0) / 1000).toFixed(0)}K`}
          trend={{ value: metrics?.avg_savings_percent || 0, direction: 'down' }}
          subtitle={`${metrics?.avg_savings_percent || 0}% savings vs market`}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
      </div>

      {/* Smart Alerts */}
      {renewals && renewals.length > 0 && (
        <Card className="border-l-4 border-amber-500">
          <div className="flex items-start">
            <svg className="w-6 h-6 text-amber-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-gray-900">Renewals Approaching</h3>
              <p className="text-sm text-gray-600 mt-1">
                {renewals.length} subscription{renewals.length > 1 ? 's' : ''} renewing soon - potential savings opportunity
              </p>
            </div>
            <Button size="sm" variant="outline" onClick={() => navigate('/portfolio')}>
              Review
            </Button>
          </div>
        </Card>
      )}

      {/* Request Status Board (Kanban) */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Request Pipeline</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 overflow-x-auto">
          {columns.map((column) => (
            <div key={column.status} className="flex flex-col min-w-[240px]">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium text-gray-700">{column.label}</h3>
                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                  {requestsByStatus[column.status]?.length || 0}
                </span>
              </div>
              <div className="space-y-2 flex-1">
                {requestsByStatus[column.status]?.slice(0, 5).map((request) => (
                  <Card
                    key={request.request_id}
                    padding="sm"
                    hover
                    onClick={() => navigate(`/requests/${request.request_id}`)}
                  >
                    <div className="space-y-2">
                      <div>
                        <p className="text-sm font-medium text-gray-900 line-clamp-2">
                          {request.description}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {request.quantity} units
                        </p>
                      </div>
                      {request.budget_max && (
                        <p className="text-xs text-gray-600">
                          Budget: ${(request.budget_max / 1000).toFixed(0)}K
                        </p>
                      )}
                      <StatusBadge status={request.status} size="sm" />
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
