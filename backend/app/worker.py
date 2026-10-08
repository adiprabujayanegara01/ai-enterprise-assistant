"""Celery worker untuk OCR/parsing/embedding di luar request utama.  Jalankan: celery -A app.worker.celery_app worker"""
from celery import Celery
from app.core.config import settings

celery_app = Celery("ai_worker", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(task_track_started=True, task_acks_late=True, worker_prefetch_multiplier=1)


@celery_app.task(name="ingest_document", bind=True, max_retries=2, default_retry_delay=10)
def ingest_task(self, doc_id: int):
    from app.services.document_service import ingest_document
    ingest_document(doc_id)
    return doc_id
