from enum import Enum


class RequestType(str, Enum):
    SAAS = "saas"
    GOODS = "goods"


class ActorRole(str, Enum):
    BUYER_AGENT = "buyer_agent"
    SELLER_AGENT = "seller_agent"


class PaymentTerms(str, Enum):
    NET_15 = "Net15"
    NET_30 = "Net30"
    NET_45 = "Net45"
    MILESTONES = "Milestones"
    DEPOSIT = "Deposit"


class NextStepHint(str, Enum):
    ACCEPT = "accept"
    COUNTER = "counter"
    REQUEST_INFO = "request_info"
    ESCALATE = "escalate"


class NegotiationDecision(str, Enum):
    ACCEPT = "accept"
    COUNTER = "counter"
    REQUEST_INFO = "request_info"
    DROP = "drop"


class ApprovalStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ContractStatus(str, Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    SIGNATURE_PENDING = "signature_pending"
    EXECUTED = "executed"
    FULFILLMENT = "fulfillment"
    CLOSED = "closed"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
