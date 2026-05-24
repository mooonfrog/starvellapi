from __future__ import annotations

import asyncio
import logging
from typing import Any, AsyncGenerator, Optional, Protocol

from ..account import Account
from ..exceptions import AuthExpiredError
from ..updater.events import (
    BaseEvent,
    NewMessageEvent,
    NewOrderEvent,
    NewReviewEvent,
    OrderStatusChangedEvent,
)
from .. import parser

log = logging.getLogger("starvellapi.runner")


class _StateStore(Protocol):
    def get(self, key: str, default: Any = None) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...


class Runner:
    def __init__(
        self,
        account: Account,
        poll_interval: float = 3.0,
        state_store: Optional[_StateStore] = None,
    ) -> None:
        self._account: Account = account
        self._poll_interval: float = poll_interval
        self._running: bool = False
        self._state = state_store

        self._known_chat_message_ids: dict[str, str] = {}
        self._known_order_ids: set[str] = set()
        self._known_order_statuses: dict[str, str] = {}
        self._known_review_ids: set[str] = set()
        self._reviews_initialized: bool = False
        self._loaded_from_state: bool = False

        if self._state is not None:
            self._known_chat_message_ids = dict(self._state.get("chat_msg_ids", {}) or {})
            self._known_order_ids = set(self._state.get("order_ids", []) or [])
            self._known_order_statuses = dict(self._state.get("order_statuses", {}) or {})
            self._known_review_ids = set(self._state.get("review_ids", []) or [])
            self._reviews_initialized = bool(self._state.get("reviews_initialized", False))
            self._loaded_from_state = bool(
                self._known_chat_message_ids or self._known_order_ids or self._known_review_ids
            )

    def _persist(self) -> None:
        if self._state is None:
            return
        self._state.set("chat_msg_ids", self._known_chat_message_ids)
        self._state.set("order_ids", list(self._known_order_ids))
        self._state.set("order_statuses", self._known_order_statuses)
        self._state.set("review_ids", list(self._known_review_ids))
        self._state.set("reviews_initialized", self._reviews_initialized)

    async def listen(self) -> AsyncGenerator[BaseEvent, None]:
        self._running = True
        if not self._loaded_from_state:
            await self._init_known_state()

        while self._running:
            try:
                events = await self._poll()
                for event in events:
                    yield event
                if events:
                    self._persist()
            except asyncio.CancelledError:
                break
            except AuthExpiredError:
                raise
            except Exception as e:
                log.warning("Ошибка при опросе API: %s", e)

            await asyncio.sleep(self._poll_interval)

    async def stop(self) -> None:
        self._running = False
        self._persist()

    async def _poll(self) -> list[BaseEvent]:
        events: list[BaseEvent] = []

        try:
            chats = await self._account.get_chats(limit=50)
            for chat in chats:
                if chat.last_message is None:
                    continue
                last_id = self._known_chat_message_ids.get(chat.id)
                if last_id is None:
                    self._known_chat_message_ids[chat.id] = chat.last_message.id
                    continue
                if chat.last_message.id != last_id:
                    self._known_chat_message_ids[chat.id] = chat.last_message.id
                    events.append(NewMessageEvent(message=chat.last_message, chat=chat))
        except AuthExpiredError:
            raise
        except Exception as e:
            log.warning("Ошибка при опросе чатов: %s", e)

        try:
            orders = await self._account.get_orders(limit=50)
            for order in orders:
                if order.id not in self._known_order_ids:
                    self._known_order_ids.add(order.id)
                    self._known_order_statuses[order.id] = order.status.value
                    events.append(NewOrderEvent(order=order))
                else:
                    prev_status = self._known_order_statuses.get(order.id)
                    if prev_status and prev_status != order.status.value:
                        self._known_order_statuses[order.id] = order.status.value
                        events.append(OrderStatusChangedEvent(order=order))
        except AuthExpiredError:
            raise
        except Exception as e:
            log.warning("Ошибка при опросе заказов: %s", e)

        try:
            reviews = await self._account.get_reviews(
                recipient_id=self._account.user_id,
                limit=20,
            )
            if not self._reviews_initialized:
                for r in reviews:
                    self._known_review_ids.add(r.id)
                self._reviews_initialized = True
            else:
                for r in reviews:
                    if r.id not in self._known_review_ids:
                        self._known_review_ids.add(r.id)
                        events.append(NewReviewEvent(review=r))
        except AuthExpiredError:
            raise
        except Exception as e:
            log.warning("Ошибка при опросе отзывов: %s", e)

        return events

    async def _init_known_state(self) -> None:
        try:
            chats = await self._account.get_chats(limit=100)
            for chat in chats:
                if chat.last_message:
                    self._known_chat_message_ids[chat.id] = chat.last_message.id
        except AuthExpiredError:
            raise
        except Exception as e:
            log.warning("Не удалось загрузить чаты при инициализации: %s", e)

        try:
            orders = await self._account.get_orders(limit=50)
            for order in orders:
                self._known_order_ids.add(order.id)
                self._known_order_statuses[order.id] = order.status.value
        except AuthExpiredError:
            raise
        except Exception as e:
            log.warning("Не удалось загрузить заказы при инициализации: %s", e)
