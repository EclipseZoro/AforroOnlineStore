import time
from celery import shared_task


@shared_task
def send_order_confirmation(order_id):
    time.sleep(2)

    print(f"[CELERY] Order confirmation sent for order {order_id}")
