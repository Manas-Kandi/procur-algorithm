import { Card } from '../../components/shared/Card'
import { MetricCard } from '../../components/shared/MetricCard'
import { Button } from '../../components/shared/Button'

export function SellerDashboard() {
  // Mock data - replace with actual API calls
  const metrics = {
    pipeline_value: 2450000,
    active_deals: 18,
    win_rate: 42,
    avg_deal_size: 136000,
    deals_at_risk: 3,
  }

  const recentActivity = [
    {
      id: '1',
      buyer: 'Acme Corp',
      status: 'negotiating',
      round: 3,
      amount: 125000,
      stage: 'Pricing discussion',
    },
    {
      id: '2',
      buyer: 'TechStart Inc',
      status: 'stalled',
      round: 2,
      amount: 89000,
      stage: 'Waiting 48hrs',
    },
    {
      id: '3',
      buyer: 'Global Systems',
      status: 'won',
      round: 4,
      amount: 215000,
      stage: 'Contract signed',
    },
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Seller Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Monitor your AI agent&apos;s performance and deal pipeline
          </p>
        </div>
        <Button>Configure Guardrails</Button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Pipeline Value"
          value={`$${(metrics.pipeline_value / 1000000).toFixed(1)}M`}
          trend={{ value: 12, direction: 'up' }}
          icon={
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
              />
            </svg>
          }
        />
        <MetricCard
          title="Active Deals"
          value={metrics.active_deals}
          subtitle="Your agent is negotiating"
          icon={
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
          }
        />
        <MetricCard
          title="Win Rate"
          value={`${metrics.win_rate}%`}
          trend={{ value: 5, direction: 'up' }}
          subtitle="This quarter"
          icon={
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
              />
            </svg>
          }
        />
        <MetricCard
          title="Avg Deal Size"
          value={`$${(metrics.avg_deal_size / 1000).toFixed(0)}K`}
          trend={{ value: 8, direction: 'up' }}
          icon={
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          }
        />
      </div>

      {/* AI Agent Activity Feed */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              AI Agent Activity
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Your agent is negotiating {metrics.active_deals} deals right now
            </p>
          </div>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-700">
            <span className="w-2 h-2 bg-green-600 rounded-full mr-2 animate-pulse"></span>
            Active
          </span>
        </div>

        <div className="space-y-3">
          {recentActivity.map((activity) => (
            <div
              key={activity.id}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <h3 className="font-medium text-gray-900">
                    {activity.buyer}
                  </h3>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                      activity.status === 'negotiating'
                        ? 'bg-purple-100 text-purple-700'
                        : activity.status === 'stalled'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-green-100 text-green-700'
                    }`}
                  >
                    {activity.status}
                  </span>
                </div>
                <div className="mt-1 flex items-center gap-4 text-sm text-gray-600">
                  <span>Round {activity.round}</span>
                  <span>•</span>
                  <span>${(activity.amount / 1000).toFixed(0)}K deal</span>
                  <span>•</span>
                  <span>{activity.stage}</span>
                </div>
              </div>
              <Button size="sm" variant="outline">
                View
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* Deals at Risk */}
      {metrics.deals_at_risk > 0 && (
        <Card className="border-l-4 border-amber-500">
          <div className="flex items-start">
            <svg
              className="w-6 h-6 text-amber-500 mr-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-gray-900">
                Deals Requiring Attention
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                {metrics.deals_at_risk} deal
                {metrics.deals_at_risk > 1 ? 's' : ''} stalled &gt;48 hours -
                consider manual intervention
              </p>
            </div>
            <Button size="sm" variant="outline">
              Review
            </Button>
          </div>
        </Card>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card hover className="text-center p-6">
          <svg
            className="w-8 h-8 mx-auto text-blue-600 mb-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
            />
          </svg>
          <h3 className="font-medium text-gray-900">Configure Guardrails</h3>
          <p className="text-sm text-gray-600 mt-1">
            Set pricing floors and strategies
          </p>
        </Card>

        <Card hover className="text-center p-6">
          <svg
            className="w-8 h-8 mx-auto text-blue-600 mb-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>
          <h3 className="font-medium text-gray-900">View Analytics</h3>
          <p className="text-sm text-gray-600 mt-1">
            Win/loss analysis and insights
          </p>
        </Card>

        <Card hover className="text-center p-6">
          <svg
            className="w-8 h-8 mx-auto text-blue-600 mb-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
            />
          </svg>
          <h3 className="font-medium text-gray-900">Team Performance</h3>
          <p className="text-sm text-gray-600 mt-1">
            Territory and rep analytics
          </p>
        </Card>
      </div>
    </div>
  )
}
