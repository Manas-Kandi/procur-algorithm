"""Alerting rules for Prometheus Alertmanager."""

# Prometheus alerting rules in YAML format

ALERTING_RULES = """
groups:
  - name: procur_negotiation_alerts
    interval: 30s
    rules:
      - alert: HighNegotiationFailureRate
        expr: |
          rate(procur_negotiation_completed_total{outcome="failed"}[5m]) 
          / rate(procur_negotiation_completed_total[5m]) > 0.2
        for: 5m
        labels:
          severity: warning
          component: negotiation
        annotations:
          summary: "High negotiation failure rate"
          description: "Negotiation failure rate is {{ $value | humanizePercentage }} (threshold: 20%)"
      
      - alert: NegotiationStalled
        expr: procur_active_negotiations > 0 and rate(procur_negotiation_completed_total[10m]) == 0
        for: 10m
        labels:
          severity: warning
          component: negotiation
        annotations:
          summary: "Negotiations appear stalled"
          description: "{{ $value }} active negotiations but no completions in 10 minutes"
      
      - alert: LowCostSavings
        expr: |
          rate(procur_cost_savings_dollars_sum[1h]) 
          / rate(procur_cost_savings_dollars_count[1h]) < 1000
        for: 1h
        labels:
          severity: info
          component: negotiation
        annotations:
          summary: "Low average cost savings"
          description: "Average cost savings is ${{ $value | humanize }} (threshold: $1000)"

  - name: procur_integration_alerts
    interval: 30s
    rules:
      - alert: IntegrationHighErrorRate
        expr: |
          rate(procur_integration_errors_total[5m]) 
          / rate(procur_integration_calls_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
          component: integration
        annotations:
          summary: "High integration error rate for {{ $labels.integration }}"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 10%)"
      
      - alert: IntegrationHighLatency
        expr: |
          histogram_quantile(0.95, 
            rate(procur_integration_latency_seconds_bucket[5m])
          ) > 5
        for: 5m
        labels:
          severity: warning
          component: integration
        annotations:
          summary: "High latency for {{ $labels.integration }}"
          description: "P95 latency is {{ $value }}s (threshold: 5s)"
      
      - alert: SlackIntegrationDown
        expr: |
          rate(procur_integration_calls_total{integration="slack",status="success"}[5m]) == 0
          and rate(procur_integration_calls_total{integration="slack"}[5m]) > 0
        for: 5m
        labels:
          severity: critical
          component: integration
        annotations:
          summary: "Slack integration is failing"
          description: "All Slack API calls are failing"
      
      - alert: DocuSignIntegrationDown
        expr: |
          rate(procur_integration_calls_total{integration="docusign",status="success"}[5m]) == 0
          and rate(procur_integration_calls_total{integration="docusign"}[5m]) > 0
        for: 5m
        labels:
          severity: critical
          component: integration
        annotations:
          summary: "DocuSign integration is failing"
          description: "All DocuSign API calls are failing"
      
      - alert: ERPIntegrationDown
        expr: |
          rate(procur_integration_calls_total{integration=~"sap|netsuite",status="success"}[5m]) == 0
          and rate(procur_integration_calls_total{integration=~"sap|netsuite"}[5m]) > 0
        for: 5m
        labels:
          severity: critical
          component: integration
        annotations:
          summary: "ERP integration is failing"
          description: "All ERP API calls are failing for {{ $labels.integration }}"

  - name: procur_system_alerts
    interval: 30s
    rules:
      - alert: HighAPILatency
        expr: |
          histogram_quantile(0.95, 
            rate(procur_http_request_duration_seconds_bucket[5m])
          ) > 2
        for: 5m
        labels:
          severity: warning
          component: api
        annotations:
          summary: "High API latency"
          description: "P95 latency is {{ $value }}s for {{ $labels.endpoint }}"
      
      - alert: HighAPIErrorRate
        expr: |
          rate(procur_http_requests_total{status=~"5.."}[5m]) 
          / rate(procur_http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
          component: api
        annotations:
          summary: "High API error rate"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"
      
      - alert: EventProcessingBacklog
        expr: |
          rate(procur_events_published_total[5m]) 
          - rate(procur_events_processed_total[5m]) > 10
        for: 10m
        labels:
          severity: warning
          component: events
        annotations:
          summary: "Event processing backlog"
          description: "{{ $value }} events/s backlog for {{ $labels.event_type }}"
      
      - alert: HighEventFailureRate
        expr: |
          rate(procur_events_processed_total{status="failed"}[5m]) 
          / rate(procur_events_processed_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
          component: events
        annotations:
          summary: "High event processing failure rate"
          description: "Failure rate is {{ $value | humanizePercentage }} for {{ $labels.event_type }}"
      
      - alert: DatabaseConnectionPoolExhausted
        expr: procur_database_connections > 90
        for: 5m
        labels:
          severity: critical
          component: database
        annotations:
          summary: "Database connection pool near exhaustion"
          description: "{{ $value }} connections in use (threshold: 90)"

  - name: procur_security_alerts
    interval: 30s
    rules:
      - alert: UnauthorizedAccessAttempts
        expr: |
          rate(procur_http_requests_total{status="401"}[5m]) > 1
        for: 5m
        labels:
          severity: warning
          component: security
        annotations:
          summary: "High rate of unauthorized access attempts"
          description: "{{ $value }} unauthorized requests/s"
      
      - alert: SuspiciousActivityDetected
        expr: |
          rate(procur_http_requests_total{status="403"}[5m]) > 0.5
        for: 5m
        labels:
          severity: warning
          component: security
        annotations:
          summary: "Suspicious activity detected"
          description: "{{ $value }} forbidden requests/s"
      
      - alert: MultipleFailedLogins
        expr: |
          increase(procur_http_requests_total{endpoint="/auth/login",status=~"4.."}[5m]) > 10
        for: 5m
        labels:
          severity: warning
          component: security
        annotations:
          summary: "Multiple failed login attempts"
          description: "{{ $value }} failed login attempts in 5 minutes"
"""


def export_alerting_rules():
    """Export alerting rules to file."""
    from pathlib import Path
    
    alerts_dir = Path(__file__).parent.parent.parent.parent / "monitoring"
    alerts_dir.mkdir(exist_ok=True)
    
    file_path = alerts_dir / "alerting_rules.yml"
    with open(file_path, "w") as f:
        f.write(ALERTING_RULES)
    
    print(f"Exported alerting rules to {file_path}")
    return file_path
