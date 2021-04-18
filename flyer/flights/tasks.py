import time

from celery import shared_task


@shared_task
def sample_task(sleep_secs):
    time.sleep(int(sleep_secs))
    print(f"Why, I've slept for {sleep_secs} seconds!")
    return True
