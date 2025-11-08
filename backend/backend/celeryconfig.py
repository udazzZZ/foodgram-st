import os

broker_url = os.getenv('CELERY_BROKER_URL')
result_backend = 'rpc://'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Moscow'
enable_utc = True
task_acks_late = True
worker_concurrency = 2