import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../services/api'
import { Card } from '../../components/shared/Card'
import { Button } from '../../components/shared/Button'
import clsx from 'clsx'

interface Subscription {
  id: string
  vendor_name: string
  category: string
  seats_total: number
  seats_active: number
  monthly_cost: number
  renewal_date: string
  utilization_percent: number
  risk_level: 'low' | 'medium' | 'high'
}

export function Portfolio() {
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'underutilized'>('all')
  const [selectedSubs, setSelectedSubs] = useState<string[]>([])

  // Mock data - replace with actual API call
  const subscriptions: Subscription[] = [
    {
      id: '1',
      vendor_name: 'Salesforce',
      category: 'CRM',
      seats_total: 200,
      seats_active: 142,
      monthly_cost: 15000,
      renewal_date: '2025-12-15',
      utilization_percent: 71,
      risk_level: 'medium',
    },
    {
      id: '2',
      vendor_name: 'Zoom',
      category: 'Video Conferencing',
      seats_total: 500,
      seats_active: 298,
      monthly_cost: 7500,
      renewal_date: '2025-11-20',
      utilization_percent: 60,
      risk_level: 'high',
    },
    {
      id: '3',
      vendor_name: 'Slack',
      category: 'Communication',
      seats_total: 450,
      seats_active: 423,
      monthly_cost: 6750,
      renewal_date: '2026-02-10',
      utilization_percent: 94,
      risk_level: 'low',
    },
  ]

  const { data: renewals } = useQuery({
    queryKey: ['renewals'],
    queryFn: () => api.getUpcomingRenewals(60),
  })

  const filteredSubs = subscriptions.filter(sub => {
    if (filter === 'upcoming') {
      const daysUntil = Math.floor((new Date(sub.renewal_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
      return daysUntil <= 60
    }
    if (filter === 'underutilized') return sub.utilization_percent < 75
    return true
  })

  const toggleSelect = (id: string) => {
    setSelectedSubs(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    )
  }

  const totalMonthlyCost = subscriptions.reduce((sum, sub) => sum + sub.monthly_cost, 0)
  const totalSeats = subscriptions.reduce((sum, sub) => sum + sub.seats_total, 0)
  const activeSeats = subscriptions.reduce((sum, sub) => sum + sub.seats_active, 0)
  const avgUtilization = (activeSeats / totalSeats) * 100

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Portfolio Management</h1>
          <p className="text-gray-600 mt-1">Manage your active subscriptions and renewals</p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <p className="text-sm text-gray-600">Total Subscriptions</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{subscriptions.length}</p>
        </Card>
        <Card>
          <p className="text-sm text-gray-600">Monthly Cost</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">${(totalMonthlyCost / 1000).toFixed(0)}K</p>
        </Card>
        <Card>
          <p className="text-sm text-gray-600">Avg Utilization</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{avgUtilization.toFixed(0)}%</p>
        </Card>
        <Card>
          <p className="text-sm text-gray-600">Renewals (60d)</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">2</p>
        </Card>
      </div>

      {/* Filters & Bulk Actions */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {[
            { value: 'all', label: 'All Subscriptions' },
            { value: 'upcoming', label: 'Upcoming Renewals' },
            { value: 'underutilized', label: 'Underutilized' },
          ].map((opt) => (
            <button
              key={opt.value}
              onClick={() => setFilter(opt.value as any)}
              className={clsx(
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                filter === opt.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              {opt.label}
            </button>
          ))}
        </div>

        {selectedSubs.length > 0 && (
          <div className="flex gap-2">
            <Button size="sm" variant="outline">
              Flag for Renegotiation ({selectedSubs.length})
            </Button>
            <Button size="sm" variant="outline">
              Request Cancellation
            </Button>
          </div>
        )}
      </div>

      {/* Subscriptions Table */}
      <Card padding="none">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="w-12 px-6 py-3">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedSubs(filteredSubs.map(s => s.id))
                      } else {
                        setSelectedSubs([])
                      }
                    }}
                  />
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vendor
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Seats
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Utilization
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Monthly Cost
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Renewal Date
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredSubs.map((sub) => {
                const daysUntil = Math.floor((new Date(sub.renewal_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
                return (
                  <tr key={sub.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        checked={selectedSubs.includes(sub.id)}
                        onChange={() => toggleSelect(sub.id)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{sub.vendor_name}</div>
                          <div className="text-xs text-gray-500">ID: {sub.id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                        {sub.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div>{sub.seats_active} / {sub.seats_total}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-1">
                          <div className="text-sm font-medium text-gray-900">{sub.utilization_percent}%</div>
                          <div className="w-20 bg-gray-200 rounded-full h-1.5 mt-1">
                            <div
                              className={clsx(
                                'h-1.5 rounded-full',
                                sub.utilization_percent >= 80 ? 'bg-green-600' :
                                sub.utilization_percent >= 60 ? 'bg-amber-600' : 'bg-red-600'
                              )}
                              style={{ width: `${sub.utilization_percent}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${sub.monthly_cost.toLocaleString()}/mo
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{new Date(sub.renewal_date).toLocaleDateString()}</div>
                      <div className={clsx(
                        'text-xs',
                        daysUntil <= 30 ? 'text-red-600' : daysUntil <= 60 ? 'text-amber-600' : 'text-gray-500'
                      )}>
                        {daysUntil} days
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button className="text-blue-600 hover:text-blue-900 mr-3">View</button>
                      <button className="text-blue-600 hover:text-blue-900">Renegotiate</button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Renewal Dashboard */}
      {renewals && renewals.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Renewals</h2>
          <div className="space-y-4">
            {renewals.slice(0, 2).map((renewal: any, idx: number) => (
              <Card key={idx}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{renewal.vendor_name || 'Salesforce'}</h3>
                    <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Current</p>
                        <p className="font-medium text-gray-900">$180K/year</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Utilization</p>
                        <p className="font-medium text-gray-900">71% (142/200 seats)</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Market Rate</p>
                        <p className="font-medium text-gray-900">15% lower</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Renewal</p>
                        <p className="font-medium text-red-600">47 days</p>
                      </div>
                    </div>
                    <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm font-medium text-blue-900">AI Recommendation</p>
                      <p className="text-sm text-blue-800 mt-1">
                        Renegotiate + reduce to 150 seats = <span className="font-semibold">$135K (save $45K)</span>
                      </p>
                    </div>
                  </div>
                  <div className="ml-4 flex flex-col gap-2">
                    <Button size="sm">Auto-Renegotiate</Button>
                    <Button size="sm" variant="outline">Review Manually</Button>
                    <Button size="sm" variant="ghost">Auto-Renew</Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
