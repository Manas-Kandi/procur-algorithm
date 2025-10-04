from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    yaml = None

from ..services.scoring_service import ScoreWeights


class ProcurementConfigError(RuntimeError):
    """Raised when a procurement configuration file cannot be processed."""


@dataclass(slots=True)
class ProcurementConfig:
    """Centralised configuration for procurement pipeline behaviour."""

    # Negotiation settings
    max_negotiation_rounds: int = 8
    buyer_accept_threshold: float = 0.75
    seller_accept_threshold: float = 0.10

    # Scoring weights (feature/value, compliance/risk, price/cost, SLA/time)
    feature_weight: float = 0.45
    compliance_weight: float = 0.30
    price_weight: float = 0.15
    sla_weight: float = 0.10

    # Company policies
    mandatory_certifications: List[str] = field(
        default_factory=lambda: ["SOC2"]
    )
    budget_approval_threshold: float = 50_000.0

    # Data sources & enrichment
    seed_catalog_path: str = "assets/seeds.json"
    enable_live_enrichment: bool = False

    def get_seed_catalog_path(self) -> "Path":
        """Get absolute path to seed catalog."""
        from pathlib import Path
        if Path(self.seed_catalog_path).is_absolute():
            return Path(self.seed_catalog_path)
        # __file__ is in src/procur/config/procurement_config.py
        # Need to go up 4 levels: procurement_config.py -> config -> procur -> src -> project_root
        project_root = Path(__file__).parent.parent.parent.parent
        return project_root / self.seed_catalog_path

    # Reporting & UX controls
    analytics_enabled: bool = True
    timezone: str = "UTC"

    # Integrations (optional credentials / endpoints)
    slack_webhook_url: Optional[str] = None
    slack_bot_token: Optional[str] = None
    docusign_api_base: Optional[str] = None
    docusign_integration_key: Optional[str] = None
    erp_api_base: Optional[str] = None
    erp_api_key: Optional[str] = None

    # Document generation
    contract_template_path: Optional[str] = None

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ProcurementConfig":
        """Load configuration overrides from a YAML file."""
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file '{config_path}' not found")
        if yaml is None:
            raise ProcurementConfigError(
                "Loading from YAML requires the 'pyyaml' package."
            )
        try:
            payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:  # pragma: no cover - PyYAML specific
            raise ProcurementConfigError(f"Failed to parse config YAML: {exc}") from exc

        normalized = cls._normalize_payload(payload)
        score_weights_blob = normalized.pop("score_weights", None)
        if isinstance(score_weights_blob, dict):
            normalized.setdefault("feature_weight", score_weights_blob.get("feature", cls.feature_weight))
            normalized.setdefault("compliance_weight", score_weights_blob.get("compliance", cls.compliance_weight))
            normalized.setdefault("price_weight", score_weights_blob.get("price", cls.price_weight))
            normalized.setdefault("sla_weight", score_weights_blob.get("sla", cls.sla_weight))

        return cls(**normalized)

    @staticmethod
    def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        normalized: Dict[str, Any] = {}
        for key, value in payload.items():
            key_snake = key.replace("-", "_")
            if isinstance(value, dict):
                normalized[key_snake] = ProcurementConfig._normalize_payload(value)
            else:
                normalized[key_snake] = value
        return normalized

    @property
    def seed_path(self) -> Path:
        return Path(self.seed_catalog_path).expanduser().resolve()

    def to_score_weights(self) -> ScoreWeights:
        """Convert configured weights to the scoring service dataclass."""
        return ScoreWeights(
            value=self.feature_weight,
            risk=self.compliance_weight,
            cost=self.price_weight,
            time=self.sla_weight,
        )

    def with_overrides(self, **updates: Any) -> "ProcurementConfig":
        """Return a new config with provided overrides applied."""
        data = self.__dict__ | updates
        return ProcurementConfig(**data)


__all__ = ["ProcurementConfig", "ProcurementConfigError"]
