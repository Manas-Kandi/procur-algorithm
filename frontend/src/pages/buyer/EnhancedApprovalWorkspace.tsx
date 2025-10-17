/**
 * Enhanced Approval Workspace
 * Complete approval workflow with risk assessments, TCO analysis, and contract generation
 */

import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  DollarSign,
  FileText,
  TrendingUp,
  Calendar,
  Building,
  User,
  Info,
  Download,
  Send,
  Clock,
  BarChart3,
  Lock,
  Unlock,
  Eye,
  MessageSquare,
  Zap,
} from 'lucide-react'
import { Card, Button, Badge, Alert, Tabs, Tab, Input, ProgressBar } from '../../components/ui/DesignSystem'
import { AIReasoningBox } from '../../components/ui/AIReasoningBox'
import { api } from '../../lib/api'
import { toast } from '../../lib/toast'
import { format } from 'date-fns'
import clsx from 'clsx'

interface PendingApproval {
  id: string
  request_id: string
  vendor: {
    name: string
    logo?: string
    rating: number
    certifications: string[]
  }
  offer: {
    total_value: number
    unit_price: number
    quantity: number
    discount_percentage: number
    payment_terms: string
    delivery_date: string
    warranty_months: number
  }
  negotiation: {
    rounds_completed: number
    time_elapsed: string
    savings_achieved: number
    ai_confidence: number
  }
  risk_assessment: {
    overall_score: number
    status: 'low' | 'medium' | 'high'
    factors: Array<{
      category: string
      status: 'pass' | 'warning' | 'fail'
      description: string
      mitigation?: string
    }>
  }
  tco_analysis: {
    year_1: number
    year_3: number
    year_5: number
    breakdown: {
      license: number
      implementation: number
      training: number
      maintenance: number
      support: number
    }
  }
  compliance: {
    required_certifications: string[]
    missing_certifications: string[]
    contract_clauses: Array<{
      name: string
      included: boolean
      negotiable: boolean
    }>
  }
  created_at: string
  deadline?: string
  approver_notes?: string
}

export function EnhancedApprovalWorkspace() {
  const queryClient = useQueryClient()
  const [selectedApproval, setSelectedApproval] = useState<PendingApproval | null>(null)
  const [showTcoDetails, setShowTcoDetails] = useState(false)
  const [approverComment, setApproverComment] = useState('')
  const [viewMode, setViewMode] = useState<'summary' | 'detailed'>('summary')

  // Fetch pending approvals
  const { data: approvals, isLoading } = useQuery<PendingApproval[]>({
    queryKey: ['pending-approvals'],
    queryFn: async () => {
      const response = await api.get('/api/approvals/pending')
      return response.data
    },
    refetchInterval: 30000,
  })

  // Approve mutation
  const approveMutation = useMutation({
    mutationFn: async (data: { id: string; comment?: string }) => {
      const response = await api.post(`/api/approvals/${data.id}/approve`, {
        comment: data.comment,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
      toast.success('Approval granted successfully')
      setSelectedApproval(null)
      setApproverComment('')
    },
    onError: () => {
      toast.error('Failed to approve. Please try again.')
    },
  })

  // Reject mutation
  const rejectMutation = useMutation({
    mutationFn: async (data: { id: string; reason: string }) => {
      const response = await api.post(`/api/approvals/${data.id}/reject`, {
        reason: data.reason,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
      toast.success('Approval rejected')
      setSelectedApproval(null)
      setApproverComment('')
    },
  })

  // Request changes mutation
  const requestChangesMutation = useMutation({
    mutationFn: async (data: { id: string; changes: string }) => {
      const response = await api.post(`/api/approvals/${data.id}/request-changes`, {
        changes: data.changes,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
      toast.success('Change request sent to negotiation team')
      setApproverComment('')
    },
  })

  const handleApprove = (approval: PendingApproval) => {
    approveMutation.mutate({
      id: approval.id,
      comment: approverComment,
    })
  }

  const handleReject = (approval: PendingApproval) => {
    if (!approverComment) {
      toast.error('Please provide a reason for rejection')
      return
    }
    rejectMutation.mutate({
      id: approval.id,
      reason: approverComment,
    })
  }

  const handleRequestChanges = (approval: PendingApproval) => {
    if (!approverComment) {
      toast.error('Please specify what changes are needed')
      return
    }
    requestChangesMutation.mutate({
      id: approval.id,
      changes: approverComment,
    })
  }

  const getRiskColor = (status: 'low' | 'medium' | 'high') => {
    switch (status) {
      case 'low':
        return 'text-success'
      case 'medium':
        return 'text-warning'
      case 'high':
        return 'text-danger'
    }
  }

  const getRiskIcon = (status: 'low' | 'medium' | 'high') => {
    switch (status) {
      case 'low':
        return <CheckCircle className="h-5 w-5 text-success" />
      case 'medium':
        return <AlertTriangle className="h-5 w-5 text-warning" />
      case 'high':
        return <XCircle className="h-5 w-5 text-danger" />
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-primary mx-auto"></div>
          <p className="mt-4 text-text-secondary">Loading approvals...</p>
        </div>
      </div>
    )
  }

  if (!approvals || approvals.length === 0) {
    return (
      <div className="min-h-screen bg-background-primary p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-text-primary mb-8">Approval Workspace</h1>
          <Alert variant="info" icon={Info}>
            No pending approvals. All caught up! We'll notify you when new offers need review.
          </Alert>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background-primary">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-text-primary">Approval Workspace</h1>
            <p className="text-text-secondary mt-1">
              {approvals.length} offer{approvals.length !== 1 ? 's' : ''} awaiting your decision
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="small"
              onClick={() => setViewMode(viewMode === 'summary' ? 'detailed' : 'summary')}
            >
              {viewMode === 'summary' ? 'Detailed View' : 'Summary View'}
            </Button>
          </div>
        </div>

        {/* Approvals List */}
        <div className="space-y-6">
          {approvals.map((approval) => (
            <Card key={approval.id} className="overflow-hidden">
              {/* Approval Header */}
              <div className="p-6 border-b border-border-subtle">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    {approval.vendor.logo ? (
                      <img
                        src={approval.vendor.logo}
                        alt={approval.vendor.name}
                        className="w-12 h-12 rounded-sm object-cover"
                      />
                    ) : (
                      <div className="w-12 h-12 bg-background-secondary rounded-sm flex items-center justify-center">
                        <Building className="h-6 w-6 text-text-tertiary" />
                      </div>
                    )}
                    <div>
                      <h2 className="text-xl font-semibold text-text-primary">
                        {approval.vendor.name}
                      </h2>
                      <div className="flex items-center gap-3 mt-1">
                        <span className="text-sm text-text-secondary">
                          Request #{approval.request_id}
                        </span>
                        {approval.deadline && (
                          <>
                            <span className="text-text-tertiary">•</span>
                            <span className="text-sm text-warning flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              Due {format(new Date(approval.deadline), 'MMM d')}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getRiskIcon(approval.risk_assessment.status)}
                    <span className={clsx('text-sm font-medium', getRiskColor(approval.risk_assessment.status))}>
                      {approval.risk_assessment.status.toUpperCase()} RISK
                    </span>
                  </div>
                </div>
              </div>

              {/* Main Content */}
              <div className="p-6">
                {viewMode === 'summary' ? (
                  // Summary View
                  <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    {/* Offer Details */}
                    <div>
                      <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">
                        Offer Details
                      </h3>
                      <div className="space-y-2">
                        <div>
                          <p className="text-2xl font-bold text-text-primary">
                            ${approval.offer.total_value.toLocaleString()}
                          </p>
                          <p className="text-xs text-text-tertiary">Total contract value</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="success" size="small">
                            {approval.offer.discount_percentage}% discount
                          </Badge>
                          <Badge variant="neutral" size="small">
                            {approval.offer.payment_terms}
                          </Badge>
                        </div>
                      </div>
                    </div>

                    {/* Negotiation Summary */}
                    <div>
                      <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">
                        Negotiation
                      </h3>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-text-secondary">Rounds</span>
                          <span className="text-sm font-medium text-text-primary">
                            {approval.negotiation.rounds_completed}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-text-secondary">Savings</span>
                          <span className="text-sm font-medium text-success">
                            ${approval.negotiation.savings_achieved.toLocaleString()}
                          </span>
                        </div>
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs text-text-secondary">AI Confidence</span>
                            <span className="text-xs font-medium text-text-primary">
                              {approval.negotiation.ai_confidence}%
                            </span>
                          </div>
                          <ProgressBar
                            value={approval.negotiation.ai_confidence}
                            variant={approval.negotiation.ai_confidence > 80 ? 'success' : 'warning'}
                            size="small"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Risk Assessment */}
                    <div>
                      <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">
                        Risk Factors
                      </h3>
                      <div className="space-y-2">
                        {approval.risk_assessment.factors.slice(0, 3).map((factor, index) => (
                          <div key={index} className="flex items-center gap-2">
                            {factor.status === 'pass' ? (
                              <CheckCircle className="h-3 w-3 text-success flex-shrink-0" />
                            ) : factor.status === 'warning' ? (
                              <AlertTriangle className="h-3 w-3 text-warning flex-shrink-0" />
                            ) : (
                              <XCircle className="h-3 w-3 text-danger flex-shrink-0" />
                            )}
                            <span className="text-xs text-text-secondary truncate">
                              {factor.category}
                            </span>
                          </div>
                        ))}
                        {approval.risk_assessment.factors.length > 3 && (
                          <button
                            onClick={() => setSelectedApproval(approval)}
                            className="text-xs text-brand-primary hover:underline"
                          >
                            +{approval.risk_assessment.factors.length - 3} more
                          </button>
                        )}
                      </div>
                    </div>

                    {/* 5-Year TCO */}
                    <div>
                      <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">
                        5-Year TCO
                      </h3>
                      <div className="space-y-2">
                        <div>
                          <p className="text-xl font-bold text-text-primary">
                            ${approval.tco_analysis.year_5.toLocaleString()}
                          </p>
                          <p className="text-xs text-text-tertiary">Total cost of ownership</p>
                        </div>
                        <button
                          onClick={() => {
                            setSelectedApproval(approval)
                            setShowTcoDetails(true)
                          }}
                          className="text-xs text-brand-primary hover:underline flex items-center gap-1"
                        >
                          <BarChart3 className="h-3 w-3" />
                          View breakdown
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  // Detailed View
                  <div className="space-y-6">
                    <Tabs value="overview" onChange={() => {}}>
                      <Tab value="overview" label="Overview" />
                      <Tab value="risk" label="Risk Assessment" />
                      <Tab value="tco" label="TCO Analysis" />
                      <Tab value="compliance" label="Compliance" />
                      <Tab value="ai" label="AI Analysis" />
                    </Tabs>

                    {/* Tab Content */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                      <div className="lg:col-span-2 space-y-6">
                        {/* Offer Summary */}
                        <Card>
                          <h3 className="text-lg font-semibold text-text-primary mb-4">
                            Offer Summary
                          </h3>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <p className="text-sm text-text-secondary">Unit Price</p>
                              <p className="text-lg font-semibold text-text-primary">
                                ${approval.offer.unit_price.toLocaleString()}
                              </p>
                            </div>
                            <div>
                              <p className="text-sm text-text-secondary">Quantity</p>
                              <p className="text-lg font-semibold text-text-primary">
                                {approval.offer.quantity} units
                              </p>
                            </div>
                            <div>
                              <p className="text-sm text-text-secondary">Delivery</p>
                              <p className="text-lg font-semibold text-text-primary">
                                {format(new Date(approval.offer.delivery_date), 'MMM d, yyyy')}
                              </p>
                            </div>
                            <div>
                              <p className="text-sm text-text-secondary">Warranty</p>
                              <p className="text-lg font-semibold text-text-primary">
                                {approval.offer.warranty_months} months
                              </p>
                            </div>
                          </div>
                        </Card>

                        {/* Risk Assessment Details */}
                        <Card>
                          <h3 className="text-lg font-semibold text-text-primary mb-4">
                            Risk Assessment
                          </h3>
                          <div className="space-y-3">
                            {approval.risk_assessment.factors.map((factor, index) => (
                              <div key={index} className="border-l-2 border-border-subtle pl-4">
                                <div className="flex items-start justify-between">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                      <span className="text-sm font-medium text-text-primary">
                                        {factor.category}
                                      </span>
                                      {factor.status === 'pass' ? (
                                        <Badge variant="success" size="small">Pass</Badge>
                                      ) : factor.status === 'warning' ? (
                                        <Badge variant="warning" size="small">Warning</Badge>
                                      ) : (
                                        <Badge variant="danger" size="small">Fail</Badge>
                                      )}
                                    </div>
                                    <p className="text-xs text-text-secondary mt-1">
                                      {factor.description}
                                    </p>
                                    {factor.mitigation && (
                                      <p className="text-xs text-info mt-1">
                                        Mitigation: {factor.mitigation}
                                      </p>
                                    )}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </Card>
                      </div>

                      {/* Right Sidebar */}
                      <div className="space-y-6">
                        {/* AI Reasoning */}
                        <AIReasoningBox
                          title="AI Recommendation"
                          reasoning={`Based on the negotiation outcome and risk assessment, this offer represents good value. The ${approval.offer.discount_percentage}% discount achieved exceeds our target, and all critical compliance requirements are met.`}
                          confidence={approval.negotiation.ai_confidence}
                          factors={[
                            { name: 'Price competitiveness', value: 'Strong', sentiment: 'positive' },
                            { name: 'Vendor reliability', value: `${approval.vendor.rating}/5`, sentiment: 'positive' },
                            { name: 'Risk level', value: approval.risk_assessment.status, sentiment: approval.risk_assessment.status === 'low' ? 'positive' : 'neutral' },
                          ]}
                          recommendation="Recommend approval with standard terms"
                        />

                        {/* Compliance Status */}
                        <Card>
                          <h3 className="text-sm font-semibold text-text-primary mb-3">
                            Compliance Check
                          </h3>
                          <div className="space-y-2">
                            {approval.vendor.certifications.map((cert, index) => (
                              <div key={index} className="flex items-center justify-between">
                                <span className="text-sm text-text-secondary">{cert}</span>
                                <CheckCircle className="h-4 w-4 text-success" />
                              </div>
                            ))}
                            {approval.compliance.missing_certifications.map((cert, index) => (
                              <div key={index} className="flex items-center justify-between">
                                <span className="text-sm text-text-secondary">{cert}</span>
                                <XCircle className="h-4 w-4 text-danger" />
                              </div>
                            ))}
                          </div>
                        </Card>
                      </div>
                    </div>
                  </div>
                )}

                {/* Action Bar */}
                <div className="mt-6 pt-6 border-t border-border-subtle">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 max-w-md">
                      <Input
                        placeholder="Add approval comment or rejection reason..."
                        value={approverComment}
                        onChange={(e) => setApproverComment(e.target.value)}
                      />
                    </div>
                    <div className="flex items-center gap-3">
                      <Button
                        variant="secondary"
                        onClick={() => handleRequestChanges(approval)}
                        loading={requestChangesMutation.isPending}
                      >
                        Request Changes
                      </Button>
                      <Button
                        variant="danger"
                        onClick={() => handleReject(approval)}
                        loading={rejectMutation.isPending}
                      >
                        Reject
                      </Button>
                      <Button
                        variant="primary"
                        icon={CheckCircle}
                        onClick={() => handleApprove(approval)}
                        loading={approveMutation.isPending}
                      >
                        Approve & Generate Contract
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
