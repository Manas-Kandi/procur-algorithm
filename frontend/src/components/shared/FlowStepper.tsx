import clsx from 'clsx'

export interface FlowStep {
  id: string
  label: string
  description?: string
  status: 'complete' | 'current' | 'upcoming'
}

interface FlowStepperProps {
  steps: FlowStep[]
  onStepSelect?: (id: string) => void
}

export function FlowStepper({
  steps,
  onStepSelect,
}: FlowStepperProps): JSX.Element {
  return (
    <nav aria-label="Request flow" className="w-full">
      <ol className="flex flex-col gap-4 sm:flex-row sm:items-stretch">
        {steps.map((step, index) => {
          const isLast = index === steps.length - 1
          const statusClass = {
            complete: 'border-none bg-brand-primary text-text-inverse',
            current:
              'border-2 border-brand-primary text-brand-primary bg-surface-raised',
            upcoming:
              'border-2 border-border-subtle text-text-tertiary bg-surface-raised',
          }[step.status]

          return (
            <li
              key={step.id}
              className={clsx(
                'relative flex flex-1 flex-col sm:flex-row sm:items-center',
                !isLast && 'sm:pr-10'
              )}
            >
              <button
                type="button"
                onClick={() => onStepSelect?.(step.id)}
                className="flex items-center text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-primary focus-visible:ring-offset-2 transition-all"
              >
                <span
                  className={clsx(
                    'flex h-9 w-9 shrink-0 items-center justify-center rounded-sm text-sm font-semibold transition-all duration-150',
                    statusClass
                  )}
                >
                  {step.status === 'complete' ? (
                    <svg
                      className="h-5 w-5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                      aria-hidden="true"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  ) : (
                    index + 1
                  )}
                </span>
                <span className="ml-3">
                  <span className="block text-sm font-semibold text-text-primary">
                    {step.label}
                  </span>
                  {step.description && (
                    <span className="mt-1 block text-xs text-text-secondary">
                      {step.description}
                    </span>
                  )}
                </span>
              </button>

              {!isLast && (
                <span
                  className="absolute left-12 top-4 hidden h-0.5 w-[calc(100%_-_3rem)] bg-border-subtle sm:block"
                  aria-hidden="true"
                />
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
