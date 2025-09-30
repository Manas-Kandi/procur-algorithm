"""Dashboard configurations for Grafana."""

# Grafana dashboard JSON configurations

NEGOTIATION_DASHBOARD = {
    "dashboard": {
        "title": "Procur - Negotiation Metrics",
        "tags": ["procur", "negotiation"],
        "timezone": "browser",
        "panels": [
            {
                "id": 1,
                "title": "Negotiation Success Rate",
                "type": "stat",
                "targets": [
                    {
                        "expr": "rate(procur_negotiation_completed_total{outcome=\"success\"}[5m]) / rate(procur_negotiation_completed_total[5m])",
                        "legendFormat": "Success Rate",
                    }
                ],
                "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
            },
            {
                "id": 2,
                "title": "Active Negotiations",
                "type": "stat",
                "targets": [
                    {
                        "expr": "procur_active_negotiations",
                        "legendFormat": "Active",
                    }
                ],
                "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0},
            },
            {
                "id": 3,
                "title": "Average Negotiation Duration",
                "type": "stat",
                "targets": [
                    {
                        "expr": "rate(procur_negotiation_duration_seconds_sum[5m]) / rate(procur_negotiation_duration_seconds_count[5m])",
                        "legendFormat": "Avg Duration (s)",
                    }
                ],
                "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0},
            },
            {
                "id": 4,
                "title": "Total Cost Savings",
                "type": "stat",
                "targets": [
                    {
                        "expr": "sum(procur_cost_savings_dollars_sum)",
                        "legendFormat": "Total Savings ($)",
                    }
                ],
                "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0},
            },
            {
                "id": 5,
                "title": "Negotiations by Vendor",
                "type": "timeseries",
                "targets": [
                    {
                        "expr": "rate(procur_negotiation_completed_total[5m])",
                        "legendFormat": "{{vendor}}",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
            },
            {
                "id": 6,
                "title": "Negotiation Rounds Distribution",
                "type": "heatmap",
                "targets": [
                    {
                        "expr": "rate(procur_negotiation_rounds_bucket[5m])",
                        "legendFormat": "{{le}}",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
            },
            {
                "id": 7,
                "title": "Cost Savings by Category",
                "type": "bargauge",
                "targets": [
                    {
                        "expr": "sum by (category) (procur_cost_savings_dollars_sum)",
                        "legendFormat": "{{category}}",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16},
            },
            {
                "id": 8,
                "title": "Negotiation Outcomes",
                "type": "piechart",
                "targets": [
                    {
                        "expr": "sum by (outcome) (procur_negotiation_completed_total)",
                        "legendFormat": "{{outcome}}",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16},
            },
        ],
    }
}

SYSTEM_HEALTH_DASHBOARD = {
    "dashboard": {
        "title": "Procur - System Health",
        "tags": ["procur", "system"],
        "timezone": "browser",
        "panels": [
            {
                "id": 1,
                "title": "HTTP Request Rate",
                "type": "timeseries",
                "targets": [
                    {
                        "expr": "rate(procur_http_requests_total[5m])",
                        "legendFormat": "{{method}} {{endpoint}}",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
            },
            {
                "id": 2,
                "title": "HTTP Request Duration (p95)",
                "type": "timeseries",
                "targets": [
                    {
                        "expr": "histogram_quantile(0.95, rate(procur_http_request_duration_seconds_bucket[5m]))",
                        "legendFormat": "{{method}} {{endpoint}}",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
            },
            {
                "id": 3,
                "title": "Integration Latency",
                "type": "timeseries",
                "targets": [
                    {
                        "expr": "rate(procur_integration_latency_seconds_sum[5m]) / rate(procur_integration_latency_seconds_count[5m])",
                        "legendFormat": "{{integration}} - {{method}}",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
            },
            {
                "id": 4,
                "title": "Integration Errors",
                "type": "timeseries",
                "targets": [
                    {
                        "expr": "rate(procur_integration_errors_total[5m])",
                        "legendFormat": "{{integration}} - {{error_type}}",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
            },
            {
                "id": 5,
                "title": "Event Processing Rate",
                "type": "timeseries",
                "targets": [
                    {
                        "expr": "rate(procur_events_processed_total[5m])",
                        "legendFormat": "{{event_type}} - {{status}}",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16},
            },
            {
                "id": 6,
                "title": "Database Connections",
                "type": "timeseries",
                "targets": [
                    {
                        "expr": "procur_database_connections",
                        "legendFormat": "Connections",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16},
            },
        ],
    }
}

INTEGRATION_DASHBOARD = {
    "dashboard": {
        "title": "Procur - Integrations",
        "tags": ["procur", "integrations"],
        "timezone": "browser",
        "panels": [
            {
                "id": 1,
                "title": "Integration Call Success Rate",
                "type": "stat",
                "targets": [
                    {
                        "expr": "rate(procur_integration_calls_total{status=\"success\"}[5m]) / rate(procur_integration_calls_total[5m])",
                        "legendFormat": "Success Rate",
                    }
                ],
                "gridPos": {"h": 8, "w": 8, "x": 0, "y": 0},
            },
            {
                "id": 2,
                "title": "Slack Notifications Sent",
                "type": "stat",
                "targets": [
                    {
                        "expr": "sum(rate(procur_integration_calls_total{integration=\"slack\"}[5m]))",
                        "legendFormat": "Notifications/s",
                    }
                ],
                "gridPos": {"h": 8, "w": 8, "x": 8, "y": 0},
            },
            {
                "id": 3,
                "title": "DocuSign Envelopes Created",
                "type": "stat",
                "targets": [
                    {
                        "expr": "sum(rate(procur_integration_calls_total{integration=\"docusign\",method=\"create_envelope\"}[5m]))",
                        "legendFormat": "Envelopes/s",
                    }
                ],
                "gridPos": {"h": 8, "w": 8, "x": 16, "y": 0},
            },
            {
                "id": 4,
                "title": "Integration Calls by Service",
                "type": "timeseries",
                "targets": [
                    {
                        "expr": "rate(procur_integration_calls_total[5m])",
                        "legendFormat": "{{integration}} - {{method}}",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
            },
            {
                "id": 5,
                "title": "Integration Latency by Service",
                "type": "timeseries",
                "targets": [
                    {
                        "expr": "histogram_quantile(0.95, rate(procur_integration_latency_seconds_bucket[5m]))",
                        "legendFormat": "{{integration}} p95",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
            },
        ],
    }
}


def export_dashboards_to_files():
    """Export dashboard configurations to JSON files."""
    import json
    from pathlib import Path
    
    dashboards_dir = Path(__file__).parent.parent.parent.parent / "dashboards"
    dashboards_dir.mkdir(exist_ok=True)
    
    dashboards = {
        "negotiation": NEGOTIATION_DASHBOARD,
        "system_health": SYSTEM_HEALTH_DASHBOARD,
        "integrations": INTEGRATION_DASHBOARD,
    }
    
    for name, config in dashboards.items():
        file_path = dashboards_dir / f"{name}_dashboard.json"
        with open(file_path, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"Exported {name} dashboard to {file_path}")
