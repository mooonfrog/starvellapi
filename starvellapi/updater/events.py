from __future__ import annotations

from ..enums import EventType
from ..types import Chat, ChatMessage, Order, Review


class BaseEvent:
    """
    Базовый класс для всех событий StarvellAPI.

    :param event_type: Тип события.
    :type event_type: :class:`starvellapi.enums.EventType`
    """

    def __init__(self, event_type: EventType) -> None:
        self.event_type: EventType = event_type
        """Тип события."""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} event_type={self.event_type}>"


class NewMessageEvent(BaseEvent):
    """
    Событие нового сообщения в чате.

    :param message: Новое сообщение.
    :type message: :class:`starvellapi.types.ChatMessage`

    :param chat: Чат, в котором появилось сообщение.
    :type chat: :class:`starvellapi.types.Chat`
    """

    def __init__(self, message: ChatMessage, chat: Chat) -> None:
        super().__init__(EventType.NEW_MESSAGE)

        self.message: ChatMessage = message
        """Новое сообщение."""

        self.chat: Chat = chat
        """Чат, в котором появилось сообщение."""

    def __repr__(self) -> str:
        return (
            f"<NewMessageEvent chat_id={self.chat.id!r} "
            f"author_id={self.message.author_id}>"
        )


class NewOrderEvent(BaseEvent):
    """
    Событие нового заказа.

    :param order: Новый заказ.
    :type order: :class:`starvellapi.types.Order`
    """

    def __init__(self, order: Order) -> None:
        super().__init__(EventType.NEW_ORDER)

        self.order: Order = order
        """Новый заказ."""

    def __repr__(self) -> str:
        return f"<NewOrderEvent order_id={self.order.id!r}>"


class OrderStatusChangedEvent(BaseEvent):
    """
    Событие изменения статуса заказа.

    :param order: Заказ с обновлённым статусом.
    :type order: :class:`starvellapi.types.Order`
    """

    def __init__(self, order: Order) -> None:
        super().__init__(EventType.ORDER_STATUS_CHANGED)

        self.order: Order = order
        """Заказ с обновлённым статусом."""

    def __repr__(self) -> str:
        return (
            f"<OrderStatusChangedEvent order_id={self.order.id!r} "
            f"status={self.order.status}>"
        )


class NewReviewEvent(BaseEvent):
    def __init__(self, review: Review) -> None:
        super().__init__(EventType.NEW_REVIEW)
        self.review: Review = review

    def __repr__(self) -> str:
        return f"<NewReviewEvent review_id={self.review.id!r} rating={self.review.rating}>"


class CommandInvokedEvent(BaseEvent):
    def __init__(
        self,
        command: str,
        message: ChatMessage,
        chat: Chat,
        author_username: str,
        response: str,
    ) -> None:
        super().__init__(EventType.COMMAND_INVOKED)
        self.command: str = command
        self.message: ChatMessage = message
        self.chat: Chat = chat
        self.author_username: str = author_username
        self.response: str = response

    def __repr__(self) -> str:
        return (
            f"<CommandInvokedEvent command={self.command!r} "
            f"chat_id={self.chat.id!r} author={self.author_username!r}>"
        )
