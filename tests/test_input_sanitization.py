from __future__ import annotations

from procur.models import Request, RequestType
from procur.services.vendor_matching import evaluate_vendor_against_request
from procur.data import load_seed_catalog
from procur.utils.input_sanitizer import sanitize_comma_separated_features, collect_allowed_feature_canonicals


def test_sanitize_removes_progress_prefix(tmp_path):
    allowed = collect_allowed_feature_canonicals()
    features, metadata = sanitize_comma_separated_features(
        "Processing your request...lead management, pipeline tracking",
        remove_prefixes=("processing your request...",),
        allowed_features=allowed,
    )

    assert features == ["lead management", "pipeline tracking"]
    assert metadata["removed_prefixes"]
    assert not metadata["dropped_tokens"]


def test_category_inference_recognises_crm():
    records = load_seed_catalog("assets/seeds.json")
    orbit = next(record for record in records if record.seed_id == "orbit-crm")

    request = Request(
        request_id="req-test",
        requester_id="user-test",
        type=RequestType.SAAS,
        description="Need a CRM with sales pipeline automation",
        specs={
            "_sanitized_inputs": {
                "must_haves": {
                    "sanitized": [
                        "lead management",
                        "contact management",
                        "pipeline tracking",
                        "email integration",
                    ],
                    "dropped_tokens": [],
                    "removed_prefixes": [],
                }
            }
        },
        quantity=100,
        budget_max=90000.0,
        must_haves=[
            "lead management",
            "contact management",
            "pipeline tracking",
            "email integration",
        ],
        compliance_requirements=["SOC2"],
    )

    summary = evaluate_vendor_against_request(request, orbit, budget_per_unit=900.0)
    inference = request.specs.get("_category_inference", {})

    assert summary.category_match is True
    assert inference.get("final") == "crm"
    assert inference.get("scores", {}).get("crm", 0.0) > 0
