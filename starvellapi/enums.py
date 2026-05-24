from __future__ import annotations

from enum import Enum


class OrderStatus(Enum):
    """Статусы заказа."""

    PENDING = "PENDING"
    """Заказ ожидает подтверждения."""

    PAID = "PAID"
    """Заказ оплачен."""

    IN_PROGRESS = "IN_PROGRESS"
    """Заказ в процессе выполнения."""

    COMPLETED = "COMPLETED"
    """Заказ завершён."""

    CANCELLED = "CANCELLED"
    """Заказ отменён."""

    REFUNDED = "REFUNDED"
    """Заказ возвращён."""

    DISPUTED = "DISPUTED"
    """По заказу открыт спор."""


class OrderUserType(Enum):
    """Роль пользователя в заказе."""

    SELLER = "seller"
    """Продавец."""

    BUYER = "buyer"
    """Покупатель."""


class OfferType(Enum):
    """Тип оффера."""

    LOT = "LOT"
    """Лот."""

    CURRENCY = "CURRENCY"
    """Валюта."""


class OfferSortBy(Enum):
    """Поле сортировки офферов."""

    PRICE = "price"
    """Сортировка по цене."""

    RATING = "rating"
    """Сортировка по рейтингу."""

    COMPLETION_RATE = "completionRate"
    """Сортировка по проценту выполнения."""


class SortDirection(Enum):
    """Направление сортировки."""

    ASC = "ASC"
    """По возрастанию."""

    DESC = "DESC"
    """По убыванию."""


class MessageType(Enum):
    """Тип сообщения в чате."""

    DEFAULT = "DEFAULT"
    """Обычное текстовое сообщение."""

    ORDER_CREATED = "ORDER_CREATED"
    """Системное сообщение о создании заказа."""

    ORDER_COMPLETED = "ORDER_COMPLETED"
    """Системное сообщение о завершении заказа."""

    ORDER_CANCELLED = "ORDER_CANCELLED"
    """Системное сообщение об отмене заказа."""

    ORDER_DISPUTED = "ORDER_DISPUTED"
    """Системное сообщение об открытии спора."""


class EventType(Enum):
    """Тип события от WebSocket."""

    NEW_MESSAGE = "new_message"
    """Новое сообщение в чате."""

    NEW_ORDER = "new_order"
    """Новый заказ."""

    ORDER_STATUS_CHANGED = "order_status_changed"
    """Статус заказа изменился."""

    NEW_REVIEW = "new_review"
    """Новый отзыв."""

    COMMAND_INVOKED = "command_invoked"
    """Пользователь вызвал кастомную команду в чате."""
