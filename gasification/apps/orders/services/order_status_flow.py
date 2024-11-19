from django.core.exceptions import ValidationError
from django.db import transaction

import logging

from apps.orders.models import Order, OrderStatusHistory, ORDER_STATUSES
from apps.orders.models import STATUS_CREATED, STATUS_ACCEPTED, \
    STATUS_CANCELLED, STATUS_ON_CONFIRM, \
    STATUS_REJECTED, STATUS_AGREED

ALLOWED_STATUS_TRANSITIONS = {
    STATUS_CREATED: [STATUS_ACCEPTED, STATUS_CANCELLED, STATUS_ON_CONFIRM],
    STATUS_ACCEPTED: [],
    STATUS_CANCELLED: [],
    STATUS_ON_CONFIRM: [STATUS_AGREED, STATUS_REJECTED],
    STATUS_AGREED: [],
    STATUS_REJECTED: [],
}

logger = logging.getLogger('order_status_transition')


def logger_send_message_init(order_id, status):
    logger.info(f"INIT status transition: -> {status} | ORDER: {order_id}")


class OrderStatusTransitionError:
    def get_invalid_status_transition(self, a, b):
        return f"Invalid status transition: {a} -> {b}"


def status_transition_check(order: Order, new_status) -> bool:
    """
    Checks if the status can be changed from current status to `new_status`
    """
    current_status = order.get_related_status().status
    try:
        if new_status not in ALLOWED_STATUS_TRANSITIONS[current_status]:
            raise ValidationError(f"INVALID status transition: {current_status} -> {new_status} | ORDER: {order}")
    except ValidationError as e:
        logger.error(e)
        return False
    return True


def order_accept(order: Order, user):
    logger_send_message_init(order.id, STATUS_ACCEPTED)
    if not status_transition_check(order, STATUS_ACCEPTED):
        return False
    _create_new_order_status(order=order, status=STATUS_ACCEPTED, on_date=order.selected_date, user=user)


def order_cancel(order: Order, user):
    logger_send_message_init(order.id, STATUS_CANCELLED)
    if not status_transition_check(order, STATUS_CANCELLED):
        print('return error message!')
        return None
    _create_new_order_status(order=order, status=STATUS_CANCELLED, user=user)


def order_on_confirm(order: Order, user, on_date):
    logger_send_message_init(order.id, STATUS_ON_CONFIRM)
    if not status_transition_check(order, STATUS_ON_CONFIRM):
        print('return error message!')
        return None
    _create_new_order_status(
        order=order,
        status=STATUS_ON_CONFIRM,
        user=user,
        on_date=on_date
    )


def order_agree(order: Order, user):
    logger_send_message_init(order.id, STATUS_AGREED)
    if not status_transition_check(order, STATUS_AGREED):
        print('return error message!')
        return None
    _create_new_order_status(
        order=order,
        status=STATUS_AGREED,
        user=user
    )


def order_reject(order: Order, user):
    logger_send_message_init(order.id, STATUS_REJECTED)
    if not status_transition_check(order, STATUS_REJECTED):
        print('return error message!')
        return None
    _create_new_order_status(
        order=order,
        status=STATUS_REJECTED,
        user=user
    )


def _create_new_order_status(order, status, user, on_date=None):
    with transaction.atomic():
        logger.info("order status history updating")
        OrderStatusHistory.objects.create(
            order=order,
            status=status,
            on_date=on_date,
            created_by=user
        )