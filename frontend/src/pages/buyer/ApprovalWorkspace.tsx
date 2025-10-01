import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../../services/api'
import { Card } from '../../components/shared/Card'
import { Button } from '../../components/shared/Button'
import { AIExplainer } from '../../components/shared/AIExplainer'
import { useState } from 'react'

export function ApprovalWorkspace() {
  const queryClient = useQueryClient()
  const { data: approvals } = useQuery({
    queryKey: ['pending-approvals'],
    queryFn: () => api.getPendingApprovals(),
  })

  if (!approvals || approvals.length === 0) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No pending approvals</h3>
          <p className="mt-1 text-sm text-gray-500">All caught up! Check back later.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Pending Approvals</h1>
        <p className="text-gray-600 mt-1">{approvals.length} item{approvals.length > 1 ? 's' : ''} requiring your decision</p>
      </div>

      <div className="space-y-6">
        {approvals.map((approval) => (
          <ApprovalCard key={approval.id} approval={approval} />
        ))}
      </div>
    </div>
  )
}

function ApprovalCard({ approval }: { approval: any }) {
  const queryClient = useQueryClient()
  const [comment, setComment] = useState('')
  const [showCommentBox, setShowCommentBox] = useState(false)

  const approveMutation = useMutation({
    mutationFn: () => api.approveContract(approval.contract_id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
    },
  })

  const handleApprove = () => {
    if (!comment && showCommentBox) {
      alert('Please add a comment')
      return
    }
    approveMutation.mutate()
  }

  return (
    <Card padding="lg" className="max-w-6xl">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left: Offer Summary */}
        <div className="space-y-6">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Offer Summary</h2>
            
            <div className="space-y-4">
              <div className="flex justify-between items-start pb-4 border-b border-gray-200">
                <div>
                  <p className="text-sm text-gray-600">Vendor</p>
                  <p className="text-lg font-semibold text-gray-900">{approval.vendor_name || 'Vendor Inc.'}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">Total Contract Value</p>
                  <p className="text-2xl font-bold text-gray-900">${approval.total_value?.toLocaleString() || '120,000'}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-600">Unit Price</p>
                  <p className="text-sm font-medium text-gray-900">${approval.unit_price || '1,000'}/seat/year</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Quantity</p>
                  <p className="text-sm font-medium text-gray-900">{approval.quantity || 100} seats</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Contract Term</p>
                  <p className="text-sm font-medium text-gray-900">{approval.term_months || 12} months</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Payment Terms</p>
                  <p className="text-sm font-medium text-gray-900">{approval.payment_terms || 'NET 30'}</p>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <p className="text-xs font-medium text-gray-600 mb-2">AI Recommendation</p>
                <div className="flex items-start gap-2 bg-blue-50 p-3 rounded-lg">
                  <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <div className="flex-1">
                    <p className="text-sm text-blue-900 font-medium">Strong Recommendation</p>
                    <p className="text-xs text-blue-800 mt-1">15% below market rate, meets all requirements, vendor has strong compliance profile</p>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <h3 className="text-sm font-medium text-gray-900">TCO Breakdown</h3>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Annual subscription</span>
                    <span className="font-medium">${(approval.unit_price * approval.quantity)?.toLocaleString() || '100,000'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Implementation</span>
                    <span className="font-medium">$5,000</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Training</span>
                    <span className="font-medium">$2,500</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-gray-200 font-semibold">
                    <span className="text-gray-900">Total First Year</span>
                    <span className="text-gray-900">$107,500</span>
                  </div>
                </div>
              </div>

              <AIExplainer
                title="this was recommended"
                reasoning={[
                  { label: 'Market Benchmark', value: '$1,150/seat average' },
                  { label: 'Savings', value: '15% below market' },
                  { label: 'Feature Match', value: '95%' },
                  { label: 'Risk Score', value: 'Low (SOC2 certified)' },
                ]}
              />
            </div>
          </div>
        </div>

        {/* Right: Risk & Compliance */}
        <div className="space-y-6">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk & Compliance</h2>
            
            <div className="space-y-3">
              <ComplianceItem
                label="SOC2 Type II"
                status="pass"
                details="Valid until Dec 2025"
              />
              <ComplianceItem
                label="Data Residency"
                status="pass"
                details="US-based storage confirmed"
              />
              <ComplianceItem
                label="SLA Guarantee"
                status="pass"
                details="99.9% uptime with credits"
              />
              <ComplianceItem
                label="GDPR Compliance"
                status="pass"
                details="DPA template reviewed"
              />
              <ComplianceItem
                label="Security Review"
                status="warning"
                details="Pending penetration test results"
              />
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-3">Required Certifications</h3>
            <div className="flex flex-wrap gap-2">
              {['SOC2', 'ISO 27001', 'GDPR'].map((cert) => (
                <span key={cert} className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                  <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  {cert}
                </span>
              ))}
            </div>
          </div>

          <div className="pt-6 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Your Decision</h3>
            
            {showCommentBox && (
              <div className="mb-4">
                <label className="block text-xs font-medium text-gray-700 mb-2">
                  Comment (required for audit trail)
                </label>
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Add your rationale for this decision..."
                />
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <Button
                variant="primary"
                fullWidth
                onClick={() => {
                  if (!showCommentBox) {
                    setShowCommentBox(true)
                  } else {
                    handleApprove()
                  }
                }}
                loading={approveMutation.isPending}
              >
                Approve
              </Button>
              <Button
                variant="outline"
                fullWidth
                onClick={() => setShowCommentBox(true)}
              >
                Request Changes
              </Button>
            </div>
            <div className="grid grid-cols-2 gap-3 mt-2">
              <Button variant="danger" fullWidth onClick={() => setShowCommentBox(true)}>
                Reject
              </Button>
              <Button variant="outline" fullWidth>
                Escalate
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}

function ComplianceItem({ label, status, details }: { label: string; status: 'pass' | 'warning' | 'fail'; details: string }) {
  const colors = {
    pass: 'text-green-600 bg-green-50',
    warning: 'text-amber-600 bg-amber-50',
    fail: 'text-red-600 bg-red-50',
  }

  const icons = {
    pass: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
      </svg>
    ),
    warning: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
      </svg>
    ),
    fail: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
      </svg>
    ),
  }

  return (
    <div className={`flex items-start gap-3 p-3 rounded-lg ${colors[status]}`}>
      {icons[status]}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">{label}</p>
        <p className="text-xs mt-0.5">{details}</p>
      </div>
    </div>
  )
}
