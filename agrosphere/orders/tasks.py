from celery import shared_task

@shared_task
def send_order_confirmation_email(order_id):
    # code to send email
    pass
