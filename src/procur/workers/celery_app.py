"""Celery application configuration."""

from celery import Celery
from celery.signals import task_failure, task_success, worker_ready

from ..events.config import get_event_bus_config

# Get configuration
config = get_event_bus_config()

# Create Celery app
celery_app = Celery(
    "procur",
    broker=config.celery_broker_url,
    backend=config.celery_result_backend,
    include=[
        "src.procur.workers.tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    
    # Task routing
    task_routes={
        "src.procur.workers.tasks.process_negotiation_round": {"queue": "negotiation"},
        "src.procur.workers.tasks.enrich_vendor_data": {"queue": "enrichment"},
        "src.procur.workers.tasks.generate_contract": {"queue": "contracts"},
        "src.procur.workers.tasks.send_notification": {"queue": "notifications"},
    },
    
    # Task priorities
    task_default_priority=5,
    
    # Result backend
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
    },
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Retry settings
    task_autoretry_for=(Exception,),
    task_retry_kwargs={"max_retries": 3},
    task_retry_backoff=True,
    task_retry_backoff_max=600,
    task_retry_jitter=True,
)


@worker_ready.connect
def on_worker_ready(**kwargs):
    """Called when worker is ready."""
    print("Celery worker is ready")


@task_success.connect
def on_task_success(sender=None, **kwargs):
    """Called when task succeeds."""
    print(f"Task {sender.name} succeeded")


@task_failure.connect
def on_task_failure(sender=None, exception=None, **kwargs):
    """Called when task fails."""
    print(f"Task {sender.name} failed: {exception}")
