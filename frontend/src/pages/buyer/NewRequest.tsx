import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { api } from '../../services/api'
import { Card } from '../../components/shared/Card'
import { Button } from '../../components/shared/Button'
import clsx from 'clsx'

type Step = 'budget' | 'details' | 'requirements' | 'policy' | 'confirm'

interface RequestData {
  budget_min?: number
  budget_max?: number
  description: string
  quantity: number
  type: string
  must_haves: string[]
  compliance_requirements: string[]
  specs: Record<string, any>
}

export function NewRequest() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState<Step>('budget')
  const [data, setData] = useState<Partial<RequestData>>({
    must_haves: [],
    compliance_requirements: [],
    specs: {},
  })

  const createMutation = useMutation({
    mutationFn: (requestData: Partial<RequestData>) => api.createRequest(requestData),
    onSuccess: (response) => {
      navigate(`/requests/${response.request_id}`)
    },
  })

  const steps: { key: Step; label: string; number: number }[] = [
    { key: 'budget', label: 'Budget Context', number: 1 },
    { key: 'details', label: 'What & How Many', number: 2 },
    { key: 'requirements', label: 'Requirements', number: 3 },
    { key: 'policy', label: 'Policy Review', number: 4 },
    { key: 'confirm', label: 'Confirm', number: 5 },
  ]

  const currentStepIndex = steps.findIndex(s => s.key === currentStep)

  const handleNext = () => {
    if (currentStepIndex < steps.length - 1) {
      setCurrentStep(steps[currentStepIndex + 1].key)
    }
  }

  const handleBack = () => {
    if (currentStepIndex > 0) {
      setCurrentStep(steps[currentStepIndex - 1].key)
    }
  }

  const handleSubmit = () => {
    createMutation.mutate(data as RequestData)
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Progress Steps */}
      <div className="mb-8">
        <nav aria-label="Progress">
          <ol className="flex items-center">
            {steps.map((step, idx) => (
              <li key={step.key} className={clsx('relative', idx !== steps.length - 1 && 'pr-8 sm:pr-20 flex-1')}>
                <div className="flex items-center">
                  <div
                    className={clsx(
                      'relative flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium',
                      idx < currentStepIndex
                        ? 'bg-blue-600 text-white'
                        : idx === currentStepIndex
                        ? 'border-2 border-blue-600 bg-white text-blue-600'
                        : 'border-2 border-gray-300 bg-white text-gray-500'
                    )}
                  >
                    {idx < currentStepIndex ? (
                      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      step.number
                    )}
                  </div>
                  <span className="ml-2 text-sm font-medium text-gray-900">{step.label}</span>
                </div>
                {idx !== steps.length - 1 && (
                  <div className="absolute top-4 left-4 -ml-px mt-0.5 h-0.5 w-full bg-gray-300" />
                )}
              </li>
            ))}
          </ol>
        </nav>
      </div>

      {/* Step Content */}
      <Card padding="lg">
        {currentStep === 'budget' && <BudgetStep data={data} setData={setData} />}
        {currentStep === 'details' && <DetailsStep data={data} setData={setData} />}
        {currentStep === 'requirements' && <RequirementsStep data={data} setData={setData} />}
        {currentStep === 'policy' && <PolicyStep data={data} />}
        {currentStep === 'confirm' && <ConfirmStep data={data} />}

        {/* Navigation */}
        <div className="mt-8 flex justify-between">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={currentStepIndex === 0}
          >
            Back
          </Button>
          {currentStep !== 'confirm' ? (
            <Button onClick={handleNext}>
              Continue
            </Button>
          ) : (
            <Button onClick={handleSubmit} loading={createMutation.isPending}>
              Submit Request
            </Button>
          )}
        </div>
      </Card>
    </div>
  )
}

function BudgetStep({ data, setData }: { data: Partial<RequestData>; setData: (d: Partial<RequestData>) => void }) {
  const [budgetOption, setBudgetOption] = useState<'exact' | 'range' | 'see-pricing' | 'need-approval'>('exact')

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">What's your approximate budget?</h2>
        <p className="text-gray-600 mt-1">This helps us find the right vendors for your needs.</p>
      </div>

      <div className="space-y-3">
        {[
          { value: 'exact', label: 'I know exactly', icon: '💰' },
          { value: 'range', label: 'I have a range', icon: '📊' },
          { value: 'see-pricing', label: 'I need to see typical pricing first', icon: '🔍' },
          { value: 'need-approval', label: 'I need approval to determine budget', icon: '✅' },
        ].map((option) => (
          <button
            key={option.value}
            onClick={() => setBudgetOption(option.value as any)}
            className={clsx(
              'w-full text-left p-4 rounded-lg border-2 transition-all',
              budgetOption === option.value
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            )}
          >
            <span className="mr-3 text-2xl">{option.icon}</span>
            <span className="font-medium">{option.label}</span>
          </button>
        ))}
      </div>

      {budgetOption === 'exact' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Budget Amount</label>
          <input
            type="number"
            value={data.budget_max || ''}
            onChange={(e) => setData({ ...data, budget_max: Number(e.target.value), budget_min: Number(e.target.value) })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="$100,000"
          />
        </div>
      )}

      {budgetOption === 'range' && (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Minimum</label>
            <input
              type="number"
              value={data.budget_min || ''}
              onChange={(e) => setData({ ...data, budget_min: Number(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="$80,000"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Maximum</label>
            <input
              type="number"
              value={data.budget_max || ''}
              onChange={(e) => setData({ ...data, budget_max: Number(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="$120,000"
            />
          </div>
        </div>
      )}
    </div>
  )
}

function DetailsStep({ data, setData }: { data: Partial<RequestData>; setData: (d: Partial<RequestData>) => void }) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">What do you need?</h2>
        <p className="text-gray-600 mt-1">Describe what you're looking for in natural language.</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
        <textarea
          value={data.description || ''}
          onChange={(e) => setData({ ...data, description: e.target.value })}
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="e.g., I need a CRM system for our sales team to manage leads and track deals..."
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
          <select
            value={data.type || ''}
            onChange={(e) => setData({ ...data, type: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select type</option>
            <option value="saas">SaaS Software</option>
            <option value="hardware">Hardware</option>
            <option value="services">Professional Services</option>
            <option value="consulting">Consulting</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Quantity (seats/units)</label>
          <input
            type="number"
            value={data.quantity || ''}
            onChange={(e) => setData({ ...data, quantity: Number(e.target.value) })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="200"
          />
        </div>
      </div>
    </div>
  )
}

function RequirementsStep({ data, setData }: { data: Partial<RequestData>; setData: (d: Partial<RequestData>) => void }) {
  const [newRequirement, setNewRequirement] = useState('')
  const [selectedCompliance, setSelectedCompliance] = useState<string[]>(data.compliance_requirements || [])

  const complianceOptions = ['SOC2', 'ISO 27001', 'HIPAA', 'GDPR', 'PCI DSS']

  const addRequirement = () => {
    if (newRequirement.trim()) {
      setData({ ...data, must_haves: [...(data.must_haves || []), newRequirement] })
      setNewRequirement('')
    }
  }

  const toggleCompliance = (item: string) => {
    const updated = selectedCompliance.includes(item)
      ? selectedCompliance.filter(c => c !== item)
      : [...selectedCompliance, item]
    setSelectedCompliance(updated)
    setData({ ...data, compliance_requirements: updated })
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Requirements & Compliance</h2>
        <p className="text-gray-600 mt-1">Specify must-have features and compliance needs.</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Must-Have Features</label>
        <div className="flex gap-2">
          <input
            type="text"
            value={newRequirement}
            onChange={(e) => setNewRequirement(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addRequirement()}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="e.g., Lead scoring, Pipeline management"
          />
          <Button onClick={addRequirement}>Add</Button>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {data.must_haves?.map((req, idx) => (
            <span
              key={idx}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-700"
            >
              {req}
              <button
                onClick={() => setData({ ...data, must_haves: data.must_haves?.filter((_, i) => i !== idx) })}
                className="ml-2 text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Compliance Requirements</label>
        <div className="grid grid-cols-2 gap-3">
          {complianceOptions.map((option) => (
            <button
              key={option}
              onClick={() => toggleCompliance(option)}
              className={clsx(
                'p-3 rounded-lg border-2 text-left transition-all',
                selectedCompliance.includes(option)
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              )}
            >
              <span className="font-medium">{option}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

function PolicyStep({ data }: { data: Partial<RequestData> }) {
  const estimatedSpend = ((data.budget_max || 0) * (data.quantity || 1)) / 1000

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Policy Preview</h2>
        <p className="text-gray-600 mt-1">Review approval requirements and timeline.</p>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">Approval Chain</h3>
        <p className="text-sm text-blue-800">
          Based on ${estimatedSpend.toFixed(0)}K spend, this will route to:
        </p>
        <ul className="mt-2 space-y-1">
          <li className="text-sm text-blue-800">✓ Department Manager</li>
          {estimatedSpend > 50 && <li className="text-sm text-blue-800">✓ Finance VP</li>}
          {estimatedSpend > 100 && <li className="text-sm text-blue-800">✓ CFO</li>}
          {data.compliance_requirements && data.compliance_requirements.length > 0 && (
            <li className="text-sm text-blue-800">✓ Legal/Compliance Review</li>
          )}
        </ul>
      </div>

      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="font-medium text-gray-900 mb-2">Estimated Timeline</h3>
        <p className="text-sm text-gray-700">
          Typical approval time: <span className="font-semibold">3-5 business days</span>
        </p>
        <p className="text-sm text-gray-700 mt-1">
          Negotiation duration: <span className="font-semibold">2-4 days</span>
        </p>
      </div>
    </div>
  )
}

function ConfirmStep({ data }: { data: Partial<RequestData> }) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Review & Confirm</h2>
        <p className="text-gray-600 mt-1">Please review your request before submitting.</p>
      </div>

      <div className="space-y-4">
        <div>
          <h3 className="text-sm font-medium text-gray-700">Budget</h3>
          <p className="text-gray-900">
            ${(data.budget_min || 0).toLocaleString()} - ${(data.budget_max || 0).toLocaleString()}
          </p>
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-700">Description</h3>
          <p className="text-gray-900">{data.description}</p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="text-sm font-medium text-gray-700">Type</h3>
            <p className="text-gray-900 capitalize">{data.type}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-700">Quantity</h3>
            <p className="text-gray-900">{data.quantity} units</p>
          </div>
        </div>

        {data.must_haves && data.must_haves.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-700">Must-Have Features</h3>
            <ul className="list-disc list-inside text-gray-900">
              {data.must_haves.map((req, idx) => (
                <li key={idx}>{req}</li>
              ))}
            </ul>
          </div>
        )}

        {data.compliance_requirements && data.compliance_requirements.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-700">Compliance Requirements</h3>
            <div className="flex flex-wrap gap-2 mt-1">
              {data.compliance_requirements.map((req, idx) => (
                <span key={idx} className="px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-700">
                  {req}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
