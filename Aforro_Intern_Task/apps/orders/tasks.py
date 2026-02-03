from celery import shared_task
import time

@shared_task
def send_order_confirmation(order_id):
    """
    Simulates sending an email asynchronously.
    """
    print(f"📧 Sending confirmation email for Order #{order_id}...")
    time.sleep(5)  # Simulate network delay (SMTP server)
    print(f"✅ Email sent successfully for Order #{order_id}!")
    return f"Order {order_id} processed."