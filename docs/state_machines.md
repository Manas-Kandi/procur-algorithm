# State Machines

## Buyer-Led Flow
```
Intake -> Sourcing -> Negotiating(round k) -> BundleSelection -> Approvals -> Contracting -> Fulfillment -> Aftercare
```

- **Transitions**
  - `Intake -> Sourcing`: `PolicyEngine.validate_request` passes.
  - `Sourcing -> Negotiating`: shortlist contains at least one compliant vendor.
  - `Negotiating -> BundleSelection`: negotiation engine stop conditions met or ladders exhausted.
  - `BundleSelection -> Approvals`: bundles constructed with deterministic score + explanation.
  - `Approvals -> Contracting`: approval chain resolved without blockers.
  - `Contracting -> Fulfillment`: contract executed & PO issued.
  - `Fulfillment -> Aftercare`: delivery/provision confirmations logged.

## Seller Flow
```
Ready -> Qualifying -> Negotiating(round k) -> Selected -> Contracting -> Fulfillment -> RenewalPrep
```

- Guardrails and policy checks protect price floors, non-negotiables, and compliance obligations at every transition.
