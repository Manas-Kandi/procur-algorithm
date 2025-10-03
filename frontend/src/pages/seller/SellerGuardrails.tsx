export function SellerGuardrails(): JSX.Element {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-[var(--core-color-text-primary)]">
        Guardrail configuration
      </h1>
      <p className="text-sm text-[var(--core-color-text-muted)]">
        Configure pricing floors, ZOPA ranges, and negotiation levers. Detailed
        builder is planned for a follow-up iteration.
      </p>
      <div className="rounded-xl border border-dashed border-[var(--core-color-border-default)] bg-[var(--core-color-surface-subtle)] p-6 text-sm text-[var(--core-color-text-muted)]">
        Layout placeholder for guardrail forms (pricing strategy, volume tiers,
        concession controls).
      </div>
    </div>
  )
}
