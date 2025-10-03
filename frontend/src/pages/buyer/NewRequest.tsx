import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { api } from '../../services/api'
import { Card } from '../../components/shared/Card'
import { Button } from '../../components/shared/Button'
// Simplified progress UI replaces FlowStepper
import {
  BudgetSelector,
  type BudgetMode,
} from '../../components/buyer/request/BudgetSelector'
import { ScopeDetails } from '../../components/buyer/request/ScopeDetails'
import { RequirementChecklist } from '../../components/buyer/request/RequirementChecklist'
import { PolicyPreview } from '../../components/buyer/request/PolicyPreview'
import { SourcingProgress } from '../../components/buyer/request/SourcingProgress'

interface RequestDraft {
  budgetMode: BudgetMode
  budgetMin?: number
  budgetMax?: number
  description?: string
  quantity?: number
  type?: string
  mustHaves: string[]
  complianceRequirements: string[]
  specs: Record<string, any>
}

const STEP_ORDER: Array<{ id: StepKey; label: string; description: string }> = [
  { id: 'budget', label: 'Budget context', description: '' },
  { id: 'scope', label: 'What & how many', description: '' },
  { id: 'requirements', label: 'Requirements refinement', description: '' },
  { id: 'policy', label: 'Policy preview', description: '' },
  { id: 'launch', label: 'Launch AI sourcing', description: '' },
]

type StepKey = 'budget' | 'scope' | 'requirements' | 'policy' | 'launch'

export function NewRequest(): JSX.Element {
  const navigate = useNavigate()
  const location = useLocation() as { state?: { description?: string } }
  const [currentStep, setCurrentStep] = useState<StepKey>('budget')
  const [draft, setDraft] = useState<RequestDraft>({
    budgetMode: 'see-pricing',
    mustHaves: [],
    complianceRequirements: [],
    specs: {},
  })
  const [showSourcingProgress, setShowSourcingProgress] = useState(false)

  // Prefill description from hero input and move to Scope step
  useEffect(() => {
    const prefill = location.state?.description?.trim()
    if (prefill) {
      setDraft((prev) => ({ ...prev, description: prefill }))
      setCurrentStep('scope')
    }
  }, [location.state])

  const createRequest = useMutation({
    mutationFn: async () => {
      const { budgetMode, ...payload } = draft
      // Create the request
      const request = await api.createRequest({
        ...payload,
        budget_min: payload.budgetMin,
        budget_max: payload.budgetMax,
        must_haves: payload.mustHaves,
        compliance_requirements: payload.complianceRequirements,
        specs: { ...payload.specs, budget_mode: budgetMode },
      })
      // Automatically start negotiations with vendors
      await api.startNegotiations(request.request_id)
      return request
    },
    onMutate: () => {
      setShowSourcingProgress(true)
    },
    onSuccess: (response) => {
      // Navigate to negotiation theater
      void navigate(`/requests/${response.request_id}/negotiate`)
    },
  })

  const currentIndex = STEP_ORDER.findIndex((step) => step.id === currentStep)

  const canGoNext = (): boolean => {
    switch (currentStep) {
      case 'budget':
        if (draft.budgetMode === 'exact') return Boolean(draft.budgetMax)
        if (draft.budgetMode === 'range')
          return Boolean(draft.budgetMin && draft.budgetMax)
        return true
      case 'scope':
        return Boolean(draft.description && draft.quantity && draft.type)
      case 'requirements':
        return draft.mustHaves.length > 0
      default:
        return true
    }
  }

  const handleNext = () => {
    if (!canGoNext()) return
    if (currentIndex < STEP_ORDER.length - 1) {
      setCurrentStep(STEP_ORDER[currentIndex + 1].id)
    }
  }

  const handleBack = () => {
    if (currentIndex > 0) {
      setCurrentStep(STEP_ORDER[currentIndex - 1].id)
    }
  }

  const launchSourcing = () => {
    if (!canGoNext()) return
    createRequest.mutate()
  }

  const estimatedVendors = useMemo(() => {
    if (draft.type === 'saas') return 12
    if (draft.type === 'hardware') return 6
    return 8
  }, [draft.type])

  return (
    <div className="space-y-8">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold text-[var(--core-color-text-primary)]">
          New procurement request
        </h1>
        <p className="text-sm text-[var(--core-color-text-muted)]">
          Provide context once—our AI agents will scope vendors, negotiate, and
          keep you in control.
        </p>
      </header>

      {/* Minimal progress bar */}
      <div className="space-y-2">
        <div
          className="h-1.5 w-full rounded-full bg-[var(--core-color-surface-subtle)]"
          aria-hidden="true"
        >
          <div
            className="h-1.5 rounded-full bg-[var(--core-color-brand-primary)] transition-all"
            style={{
              width: `${Math.round(((currentIndex + 1) / STEP_ORDER.length) * 100)}%`,
            }}
          />
        </div>
        <p className="text-xs text-[var(--core-color-text-tertiary)]">
          Step {currentIndex + 1} of {STEP_ORDER.length}
        </p>
      </div>

      <Card
        padding="lg"
        className="space-y-8 border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)]"
      >
        {currentStep === 'budget' && (
          <BudgetSelector
            mode={draft.budgetMode}
            budgetMin={draft.budgetMin}
            budgetMax={draft.budgetMax}
            onChange={({ mode, budgetMin, budgetMax }) => {
              setDraft((prev) => ({
                ...prev,
                budgetMode: mode,
                budgetMin,
                budgetMax,
              }))
            }}
          />
        )}

        {currentStep === 'scope' && (
          <ScopeDetails
            description={draft.description}
            type={draft.type}
            quantity={draft.quantity}
            onChange={(payload) => {
              setDraft((prev) => ({ ...prev, ...payload }))
            }}
          />
        )}

        {currentStep === 'requirements' && (
          <RequirementChecklist
            category={draft.type}
            mustHaves={draft.mustHaves}
            compliance={draft.complianceRequirements}
            onChange={({ mustHaves, compliance }) => {
              setDraft((prev) => ({
                ...prev,
                mustHaves,
                complianceRequirements: compliance,
              }))
            }}
          />
        )}

        {currentStep === 'policy' && (
          <PolicyPreview
            budgetMin={draft.budgetMin}
            budgetMax={draft.budgetMax}
            quantity={draft.quantity}
            complianceCount={draft.complianceRequirements.length}
          />
        )}

        {currentStep === 'launch' && (
          <div className="space-y-6">
            <div className="rounded-xl border border-[var(--core-color-border-default)] bg-[var(--core-color-surface-subtle)] p-4">
              <p className="text-sm font-semibold text-[var(--core-color-text-primary)]">
                Launch AI sourcing
              </p>
              <p className="mt-1 text-xs text-[var(--core-color-text-muted)]">
                We’ll reach out to {estimatedVendors}+ vendors and start
                negotiations instantly. You can monitor progress in the
                negotiation theater.
              </p>
            </div>
            <SourcingProgress
              status={showSourcingProgress ? 'running' : 'idle'}
              contacted={showSourcingProgress ? estimatedVendors : 0}
              responded={
                showSourcingProgress
                  ? Math.max(3, Math.round(estimatedVendors * 0.5))
                  : 0
              }
              negotiating={
                showSourcingProgress
                  ? Math.max(1, Math.round(estimatedVendors * 0.25))
                  : 0
              }
            />
          </div>
        )}

        <div className="flex flex-col gap-3 border-t border-[var(--core-color-border-default)] pt-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex-1" />
          <div className="flex flex-1 justify-center">
            <span className="text-xs text-[var(--core-color-text-tertiary)]">
              Step {currentIndex + 1} of {STEP_ORDER.length}
            </span>
          </div>
          <div className="flex flex-1 flex-col gap-3 sm:flex-row sm:justify-end">
            <Button
              variant="outline"
              onClick={handleBack}
              disabled={currentIndex === 0}
            >
              Back
            </Button>
            {currentStep !== 'launch' ? (
              <Button onClick={handleNext} disabled={!canGoNext()}>
                Continue
              </Button>
            ) : (
              <Button
                onClick={launchSourcing}
                loading={createRequest.isPending}
              >
                Launch AI sourcing
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  )
}
