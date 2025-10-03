import { Button } from '../../shared/Button'

interface DecisionBarProps {
  isCommentMode: boolean
  comment: string
  onCommentChange: (value: string) => void
  onApprove: () => void
  onRequestChanges: () => void
  disableActions?: boolean
  sticky?: boolean
}

export function DecisionBar({
  isCommentMode,
  comment,
  onCommentChange,
  onApprove,
  onRequestChanges,
  disableActions,
  sticky = true,
}: DecisionBarProps): JSX.Element {
  return (
    <div
      className={
        sticky
          ? 'sticky bottom-0 left-0 right-0 border-t border-[var(--core-color-border-default)] bg-[var(--core-color-surface-canvas)] px-4 py-4 shadow-200 sm:px-6'
          : 'border-t border-[var(--core-color-border-default)] px-3 py-3 sm:px-4'
      }
    >
      <div className="mx-auto flex max-w-[960px] flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex-1">
          {isCommentMode && (
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-[var(--core-color-text-muted)]">
                Comment (required for audit trail)
              </label>
              <textarea
                value={comment}
                onChange={(event) => {
                  onCommentChange(event.target.value)
                }}
                rows={3}
                className="mt-2 w-full rounded-lg border border-[var(--core-color-border-default)] bg-white px-3 py-2 text-sm text-[var(--core-color-text-primary)] focus:border-[var(--core-color-border-focus)] focus:outline-none focus:ring-2 focus:ring-[var(--core-color-border-focus)]/40"
                placeholder="Add your rationale for this decision…"
              />
            </div>
          )}
        </div>
        <div className="flex flex-col gap-2 sm:flex-row">
          <Button
            variant="primary"
            onClick={onApprove}
            disabled={disableActions}
          >
            Approve
          </Button>
          <Button
            variant="outline"
            onClick={onRequestChanges}
            disabled={disableActions}
          >
            Request changes
          </Button>
        </div>
      </div>
    </div>
  )
}
