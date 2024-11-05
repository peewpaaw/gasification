from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order, OrderStatusHistory


@receiver(post_save, sender=Order)
def create_initial_order_status(sender, instance, created, **kwargs):
    # if created:
    #     OrderStatusHistory.objects.create(
    #         order=instance,
    #         status='created',
    #         created_by=instance.created_by
    #
    #     )
    pass
