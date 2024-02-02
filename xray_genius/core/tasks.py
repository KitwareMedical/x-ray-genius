from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def test_task() -> None:
    print('Test task')
    logger.info('Testing logger')
