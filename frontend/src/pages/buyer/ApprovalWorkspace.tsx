import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../../services/api'
import { SmartAlert } from '../../components/shared/SmartAlert'
import { OfferSummary } from '../../components/buyer/approval/OfferSummary'
import { RiskPanel } from '../../components/buyer/approval/RiskPanel'
import { DecisionBar } from '../../components/buyer/approval/DecisionBar'
import type { Contract } from '../../types'

// Approvals are essentially contracts at a certain stage
// We can reuse the Contract type and add any extra fields if needed
interface PendingApproval extends Contract {
  vendor_name?: string
  total_value?: number
  unit_price?: number
  quantity?: number
  term_months?: number
  payment_terms?: string
  confidence?: number
}

export function ApprovalWorkspace(): JSX.Element {
  const { data: approvals } = useQuery<PendingApproval[]>({
    queryKey: ['pending-approvals'],
    queryFn: async () => await api.getPendingApprovals(),
  })

  if (!approvals || approvals.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-[var(--core-color-text-primary)]">
          Approval workspace
        </h1>
        <SmartAlert
          severity="info"
          title="No pending approvals"
          message="All caught up! We will notify you when new offers are ready for review."
        />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold text-[var(--core-color-text-primary)]">
          Approval workspace
        </h1>
        <p className="text-sm text-[var(--core-color-text-muted)]">
          {approvals.length} offer(s) awaiting your decision.
        </p>
      </header>

      <div className="space-y-10">
        {approvals.map((approval) => (
          <ApprovalCard key={approval.contract_id} approval={approval} />
        ))}
      </div>
    </div>
  )
}

function ApprovalCard({
  approval,
}: {
  approval: PendingApproval
}): JSX.Element {
  const queryClient = useQueryClient()
  const [comment, setComment] = useState('')
  const [commentMode, setCommentMode] = useState(false)

  const approveMutation = useMutation({
    mutationFn: async () => await api.approveContract(approval.contract_id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
    },
  })

  const handleApprove = () => {
    if (commentMode && !comment.trim()) {
      alert('Please add a comment for audit trail.')
      return
    }
    approveMutation.mutate()
  }

  return (
    <div className="rounded-2xl border border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)] shadow-100">
      <div className="space-y-6 p-6">
        <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
          <OfferSummary
            vendorName={approval.vendor_name ?? 'Vendor Inc.'}
            totalValue={approval.total_value ?? 120_000}
            unitPrice={approval.unit_price ?? 1_000}
            quantity={approval.quantity ?? 100}
            termMonths={approval.term_months ?? 12}
            paymentTerms={approval.payment_terms ?? 'NET 30'}
            confidence={approval.confidence ?? 0.9}
          />
          <RiskPanel
            items={[
              {
                label: 'SOC2 Type II',
                status: 'pass',
                details: 'Valid until Dec 2025',
              },
              {
                label: 'Data residency',
                status: 'pass',
                details: 'US-based storage confirmed',
              },
              {
                label: 'Security review',
                status: 'warning',
                details: 'Pending penetration test results',
              },
            ]}
            certifications={['SOC2', 'ISO 27001', 'GDPR']}
          />
        </div>
      </div>
      <DecisionBar
        sticky={false}
        isCommentMode={commentMode}
        comment={comment}
        onCommentChange={setComment}
        onApprove={handleApprove}
        onRequestChanges={() => {
          setCommentMode(true)
        }}
        disableActions={approveMutation.isPending}
      />
    </div>
  )
}
