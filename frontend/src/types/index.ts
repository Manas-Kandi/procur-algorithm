// Core data types matching backend models

export type UserRole = 'buyer' | 'seller' | 'approver' | 'admin' | 'auditor'

export interface User {
  id: string
  email: string
  username: string
  role: UserRole
  full_name?: string
  organization_id?: string
}

export interface Request {
  request_id: string
  requester_id: string
  type: string
  description: string
  specs: Record<string, any>
  quantity: number
  budget_min?: number
  budget_max?: number
  currency: string
  status: RequestStatus
  created_at: string
  updated_at: string
  must_haves: string[]
  compliance_requirements: string[]
}

export type RequestStatus =
  | 'draft'
  | 'intake'
  | 'sourcing'
  | 'negotiating'
  | 'approving'
  | 'contracted'
  | 'provisioning'
  | 'completed'
  | 'cancelled'

export interface Vendor {
  vendor_id: string
  name: string
  capability_tags: string[]
  certifications: string[]
  risk_level: 'low' | 'medium' | 'high'
  contact_endpoints: Record<string, string>
  price_tiers?: Record<string, number>
}

export interface OfferComponents {
  unit_price: number
  currency: string
  quantity: number
  term_months: number
  payment_terms: string
  warranty_support?: Record<string, string>
  one_time_fees?: Record<string, number>
  notes?: string
}

export interface OfferScore {
  spec_match: number
  tco: number
  risk: number
  time: number
  utility: number
  matched_features: string[]
  missing_features: string[]
}

export interface Offer {
  offer_id: string
  request_id: string
  vendor_id: string
  components: OfferComponents
  score: OfferScore
  confidence: number
  accepted: boolean
}

export interface NegotiationMessage {
  actor: 'buyer' | 'seller'
  round: number
  proposal: OfferComponents
  justification_bullets: string[]
  machine_rationale: {
    score_components: Record<string, number>
    constraints_respected: string[]
    concession_taken: string
  }
  next_step_hint: string
}

export interface NegotiationSession {
  session_id: string
  request_id: string
  vendor_id: string
  status: 'active' | 'completed' | 'failed' | 'stalled'
  current_round: number
  messages: NegotiationMessage[]
  best_offer?: Offer
  created_at: string
  updated_at: string
}

export interface Contract {
  contract_id: string
  request_id: string
  vendor_id: string
  approval_status: 'draft' | 'pending' | 'approved' | 'rejected'
  signature_status: 'draft' | 'sent' | 'signed' | 'completed'
  created_at: string
  updated_at: string
}

export interface DashboardMetrics {
  active_requests: number
  pending_approvals: number
  upcoming_renewals: number
  monthly_spend: number
  budget_available: number
  negotiations_in_progress: number
  avg_savings_percent: number
}

export interface RenewalAlert {
  vendor_name: string
  current_cost: number
  renewal_date: string
  days_until_renewal: number
  utilization_percent: number
  potential_savings: number
  recommended_action: string
}
