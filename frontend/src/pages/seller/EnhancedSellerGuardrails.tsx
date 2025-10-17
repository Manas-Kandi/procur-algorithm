/**
 * Enhanced Seller Guardrails Configuration
 * Configure AI agent negotiation parameters and strategies
 */

import React, { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Shield,
  DollarSign,
  Percent,
  Clock,
  AlertTriangle,
  CheckCircle,
  Info,
  Save,
  RotateCcw,
  TrendingDown,
  Target,
  Zap,
  Lock,
  Unlock,
} from 'lucide-react'
import { Card, Button, Input, Badge, Alert, Tabs, Tab } from '../../components/ui/DesignSystem'
import { AIReasoningBox } from '../../components/ui/AIReasoningBox'
import { api } from '../../lib/api'
import { toast } from '../../lib/toast'

interface Guardrails {
  pricing: {
    min_discount: number
    max_discount: number
    auto_approve_threshold: number
    volume_discount_tiers: Array<{
      min_quantity: number
      max_discount: number
    }>
  }
  negotiation: {
    max_rounds: number
    concession_strategy: 'aggressive' | 'moderate' | 'conservative'
    response_time_minutes: number
    auto_counter: boolean
    walk_away_threshold: number
  }
  compliance: {
    required_certifications: string[]
    payment_terms: string[]
    contract_clauses: string[]
    restricted_industries: string[]
  }
  approval: {
    auto_approve_under: number
    require_approval_over: number
    approval_matrix: Array<{
      min_amount: number
      max_amount: number
      approver_role: string
    }>
  }
}

export function EnhancedSellerGuardrails() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('pricing')
  const [hasChanges, setHasChanges] = useState(false)

  // Fetch current guardrails
  const { data: guardrails, isLoading } = useQuery<Guardrails>({
    queryKey: ['seller-guardrails'],
    queryFn: async () => {
      const response = await api.get('/api/seller/guardrails')
      return response.data
    },
  })

  const [formData, setFormData] = useState<Guardrails>(guardrails || {
    pricing: {
      min_discount: 0,
      max_discount: 30,
      auto_approve_threshold: 10,
      volume_discount_tiers: [
        { min_quantity: 10, max_discount: 15 },
        { min_quantity: 50, max_discount: 25 },
        { min_quantity: 100, max_discount: 35 },
      ],
    },
    negotiation: {
      max_rounds: 8,
      concession_strategy: 'moderate',
      response_time_minutes: 30,
      auto_counter: true,
      walk_away_threshold: 50,
    },
    compliance: {
      required_certifications: ['SOC2', 'ISO27001'],
      payment_terms: ['Net 30', 'Net 60'],
      contract_clauses: ['SLA', 'Data Privacy', 'Termination'],
      restricted_industries: [],
    },
    approval: {
      auto_approve_under: 50000,
      require_approval_over: 250000,
      approval_matrix: [
        { min_amount: 0, max_amount: 50000, approver_role: 'auto' },
        { min_amount: 50001, max_amount: 250000, approver_role: 'sales_manager' },
        { min_amount: 250001, max_amount: 1000000, approver_role: 'vp_sales' },
      ],
    },
  })

  // Save guardrails mutation
  const saveMutation = useMutation({
    mutationFn: async (data: Guardrails) => {
      const response = await api.put('/api/seller/guardrails', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['seller-guardrails'] })
      toast.success('Guardrails updated successfully')
      setHasChanges(false)
    },
    onError: () => {
      toast.error('Failed to update guardrails')
    },
  })

  const handleInputChange = (section: keyof Guardrails, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }))
    setHasChanges(true)
  }

  const handleReset = () => {
    if (guardrails) {
      setFormData(guardrails)
      setHasChanges(false)
    }
  }

  const handleSave = () => {
    saveMutation.mutate(formData)
  }

  return (
    <div className="min-h-screen bg-background-primary">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-text-primary">Negotiation Guardrails</h1>
            <p className="text-text-secondary mt-1">
              Configure how your AI agent negotiates on your behalf
            </p>
          </div>
          <div className="flex items-center gap-3">
            {hasChanges && (
              <Badge variant="warning">Unsaved changes</Badge>
            )}
            <Button
              variant="secondary"
              icon={RotateCcw}
              onClick={handleReset}
              disabled={!hasChanges}
            >
              Reset
            </Button>
            <Button
              variant="primary"
              icon={Save}
              onClick={handleSave}
              loading={saveMutation.isPending}
              disabled={!hasChanges}
            >
              Save Changes
            </Button>
          </div>
        </div>

        {/* AI Recommendation */}
        <AIReasoningBox
          title="AI Recommendations"
          reasoning="Based on your historical win rate and market conditions, I recommend a moderate concession strategy with a maximum discount of 25-30%. Your current settings align well with industry standards."
          confidence={85}
          factors={[
            { name: 'Market Competition', value: 'High', sentiment: 'negative' },
            { name: 'Product Differentiation', value: 'Strong', sentiment: 'positive' },
            { name: 'Historical Win Rate', value: '42%', sentiment: 'neutral' },
          ]}
          recommendation="Consider increasing auto-approval threshold to $75K to speed up deal velocity"
          expandable
        />

        {/* Tabs */}
        <div className="mt-8">
          <Tabs value={activeTab} onChange={setActiveTab}>
            <Tab value="pricing" label="Pricing Strategy" />
            <Tab value="negotiation" label="Negotiation Rules" />
            <Tab value="compliance" label="Compliance" />
            <Tab value="approval" label="Approval Matrix" />
          </Tabs>

          <div className="mt-6">
            {/* Pricing Strategy Tab */}
            {activeTab === 'pricing' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                    <DollarSign className="h-5 w-5 text-brand-primary" />
                    Discount Limits
                  </h3>
                  <div className="space-y-4">
                    <Input
                      label="Minimum Discount (%)"
                      type="number"
                      value={formData.pricing.min_discount}
                      onChange={(e) => handleInputChange('pricing', 'min_discount', Number(e.target.value))}
                      helper="Starting discount for first offer"
                      icon={TrendingDown}
                    />
                    <Input
                      label="Maximum Discount (%)"
                      type="number"
                      value={formData.pricing.max_discount}
                      onChange={(e) => handleInputChange('pricing', 'max_discount', Number(e.target.value))}
                      helper="AI will never exceed this discount"
                      icon={Lock}
                    />
                    <Input
                      label="Auto-Approve Discount (%)"
                      type="number"
                      value={formData.pricing.auto_approve_threshold}
                      onChange={(e) => handleInputChange('pricing', 'auto_approve_threshold', Number(e.target.value))}
                      helper="Automatically accept offers within this discount"
                      icon={Zap}
                    />
                  </div>
                </Card>

                <Card>
                  <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                    <Percent className="h-5 w-5 text-brand-primary" />
                    Volume Discounts
                  </h3>
                  <div className="space-y-3">
                    {formData.pricing.volume_discount_tiers.map((tier, index) => (
                      <div key={index} className="flex items-center gap-3 p-3 bg-background-secondary rounded-sm">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-text-primary">
                            {tier.min_quantity}+ units
                          </p>
                          <p className="text-xs text-text-tertiary">
                            Up to {tier.max_discount}% discount
                          </p>
                        </div>
                        <Badge variant="info">{tier.max_discount}%</Badge>
                      </div>
                    ))}
                    <Button variant="secondary" size="small" fullWidth>
                      Add Tier
                    </Button>
                  </div>
                </Card>

                <Card className="lg:col-span-2">
                  <Alert variant="info" icon={Info}>
                    Your AI agent will use these limits to negotiate pricing. It will start with the minimum discount
                    and gradually increase up to the maximum based on the negotiation dynamics and buyer signals.
                  </Alert>
                </Card>
              </div>
            )}

            {/* Negotiation Rules Tab */}
            {activeTab === 'negotiation' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                    <Target className="h-5 w-5 text-brand-primary" />
                    Negotiation Strategy
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-2">
                        Concession Strategy
                      </label>
                      <div className="grid grid-cols-3 gap-2">
                        {(['aggressive', 'moderate', 'conservative'] as const).map((strategy) => (
                          <button
                            key={strategy}
                            onClick={() => handleInputChange('negotiation', 'concession_strategy', strategy)}
                            className={clsx(
                              'p-3 rounded-sm border text-sm font-medium capitalize transition-all',
                              formData.negotiation.concession_strategy === strategy
                                ? 'bg-brand-primary text-text-inverse border-brand-primary'
                                : 'bg-surface-raised text-text-secondary border-border-medium hover:border-border-strong'
                            )}
                          >
                            {strategy}
                          </button>
                        ))}
                      </div>
                      <p className="text-xs text-text-tertiary mt-2">
                        {formData.negotiation.concession_strategy === 'aggressive' 
                          ? 'Larger concessions, faster deals'
                          : formData.negotiation.concession_strategy === 'conservative'
                          ? 'Smaller concessions, protect margins'
                          : 'Balanced approach for most deals'}
                      </p>
                    </div>

                    <Input
                      label="Maximum Negotiation Rounds"
                      type="number"
                      value={formData.negotiation.max_rounds}
                      onChange={(e) => handleInputChange('negotiation', 'max_rounds', Number(e.target.value))}
                      helper="AI will close or walk away after this many rounds"
                    />

                    <Input
                      label="Walk Away Threshold (%)"
                      type="number"
                      value={formData.negotiation.walk_away_threshold}
                      onChange={(e) => handleInputChange('negotiation', 'walk_away_threshold', Number(e.target.value))}
                      helper="Minimum acceptable margin to continue negotiation"
                      icon={AlertTriangle}
                    />
                  </div>
                </Card>

                <Card>
                  <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                    <Clock className="h-5 w-5 text-brand-primary" />
                    Response Settings
                  </h3>
                  <div className="space-y-4">
                    <Input
                      label="Response Time (minutes)"
                      type="number"
                      value={formData.negotiation.response_time_minutes}
                      onChange={(e) => handleInputChange('negotiation', 'response_time_minutes', Number(e.target.value))}
                      helper="How quickly AI responds to buyer messages"
                    />

                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-2">
                        Auto-Counter Offers
                      </label>
                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => handleInputChange('negotiation', 'auto_counter', !formData.negotiation.auto_counter)}
                          className={clsx(
                            'relative w-12 h-6 rounded-full transition-colors',
                            formData.negotiation.auto_counter ? 'bg-brand-primary' : 'bg-border-strong'
                          )}
                        >
                          <span
                            className={clsx(
                              'absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                              formData.negotiation.auto_counter && 'translate-x-6'
                            )}
                          />
                        </button>
                        <span className="text-sm text-text-secondary">
                          {formData.negotiation.auto_counter ? 'Enabled' : 'Disabled'}
                        </span>
                      </div>
                      <p className="text-xs text-text-tertiary mt-2">
                        AI will automatically respond to buyer offers without manual review
                      </p>
                    </div>
                  </div>
                </Card>
              </div>
            )}

            {/* Compliance Tab */}
            {activeTab === 'compliance' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                    <Shield className="h-5 w-5 text-brand-primary" />
                    Required Certifications
                  </h3>
                  <div className="space-y-2">
                    {formData.compliance.required_certifications.map((cert, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-background-secondary rounded-sm">
                        <span className="text-sm font-medium text-text-primary">{cert}</span>
                        <CheckCircle className="h-4 w-4 text-success" />
                      </div>
                    ))}
                    <Button variant="secondary" size="small" fullWidth>
                      Add Certification
                    </Button>
                  </div>
                </Card>

                <Card>
                  <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                    <Lock className="h-5 w-5 text-brand-primary" />
                    Contract Requirements
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-text-secondary">Payment Terms</label>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {formData.compliance.payment_terms.map((term, index) => (
                          <Badge key={index} variant="neutral">{term}</Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-text-secondary">Required Clauses</label>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {formData.compliance.contract_clauses.map((clause, index) => (
                          <Badge key={index} variant="neutral">{clause}</Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </Card>
              </div>
            )}

            {/* Approval Matrix Tab */}
            {activeTab === 'approval' && (
              <div className="space-y-6">
                <Card>
                  <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-brand-primary" />
                    Approval Thresholds
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label="Auto-Approve Under"
                      type="number"
                      value={formData.approval.auto_approve_under}
                      onChange={(e) => handleInputChange('approval', 'auto_approve_under', Number(e.target.value))}
                      helper="Deals under this amount are auto-approved"
                      icon={Unlock}
                    />
                    <Input
                      label="Require Approval Over"
                      type="number"
                      value={formData.approval.require_approval_over}
                      onChange={(e) => handleInputChange('approval', 'require_approval_over', Number(e.target.value))}
                      helper="Deals over this amount need executive approval"
                      icon={Lock}
                    />
                  </div>
                </Card>

                <Card>
                  <h3 className="text-lg font-semibold text-text-primary mb-4">
                    Approval Matrix
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-border-subtle">
                          <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                            Deal Range
                          </th>
                          <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                            Approver
                          </th>
                          <th className="text-left py-3 px-4 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                            SLA
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {formData.approval.approval_matrix.map((level, index) => (
                          <tr key={index} className="border-b border-border-subtle">
                            <td className="py-3 px-4">
                              <span className="text-sm font-medium text-text-primary">
                                ${level.min_amount.toLocaleString()} - ${level.max_amount.toLocaleString()}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              <Badge variant={level.approver_role === 'auto' ? 'success' : 'info'}>
                                {level.approver_role === 'auto' ? 'Auto-Approved' : level.approver_role.replace('_', ' ')}
                              </Badge>
                            </td>
                            <td className="py-3 px-4">
                              <span className="text-sm text-text-secondary">
                                {level.approver_role === 'auto' ? 'Instant' : '2-4 hours'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

import clsx from 'clsx'
