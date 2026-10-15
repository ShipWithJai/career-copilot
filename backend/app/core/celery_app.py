from celery import Celery 
from celery.schedules import crontab
from app.core.config import get_settings
REDIS_URL=str(get_settings().REDIS_URL)

celery_app=Celery(
    "career_copilot",
    include=["app.services.job_fetcher", "app.services.pdf_tasks"]
)
celery_app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    broker_connection_retry_on_startup=True,
    
    beat_schedule={
        'fetch-jobs-every-6-hours': {
            'task': 'app.services.job_fetcher.scheduled_job_fetch',
            'schedule': crontab(hour='*/6', minute='0'),
        },
    }
)

celery_app.autodiscover_tasks(['app.services'])