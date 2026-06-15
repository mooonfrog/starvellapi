from __future__ import annotations
import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Optional, Protocol
import websockets
from ..account import Account
from ..exceptions import AuthExpiredError
from ..updater.events import BaseEvent, NewMessageEvent, NewOrderEvent, NewReviewEvent, OrderStatusChangedEvent
from .. import parser
from ..types import Chat
log = logging.getLogger('starvellapi.runner')
_WS_URL = 'wss://starvell.com/socket.io/?EIO=4&transport=websocket'
_SEEN_IDS_MAXLEN = 1000

class _StateStore(Protocol):

    def get(self, key: str, default: Any=None) -> Any:
        ...

    def set(self, key: str, value: Any) -> None:
        ...

class Runner:

    def __init__(self, account: Account, state_store: Optional[_StateStore]=None) -> None:
        self._account: Account = account
        self._running: bool = False
        self._state = state_store
        self._seen_message_ids: dict[str, None] = {}
        self._known_order_ids: set[str] = set()
        self._known_order_statuses: dict[str, str] = {}
        self._known_review_ids: set[str] = set()
        self._reviews_initialized: bool = False
        self._queue: asyncio.Queue[BaseEvent] = asyncio.Queue()
        self._ws_task: Optional[asyncio.Task] = None
        if self._state is not None:
            self._known_order_ids = set(self._state.get('order_ids', []) or [])
            self._known_order_statuses = dict(self._state.get('order_statuses', {}) or {})
            self._known_review_ids = set(self._state.get('review_ids', []) or [])
            self._reviews_initialized = bool(self._state.get('reviews_initialized', False))

    def _persist(self) -> None:
        if self._state is None:
            return
        self._state.set('order_ids', list(self._known_order_ids))
        self._state.set('order_statuses', self._known_order_statuses)
        self._state.set('review_ids', list(self._known_review_ids))
        self._state.set('reviews_initialized', self._reviews_initialized)

    def _mark_seen(self, message_id: str) -> None:
        self._seen_message_ids[message_id] = None
        while len(self._seen_message_ids) > _SEEN_IDS_MAXLEN:
            self._seen_message_ids.pop(next(iter(self._seen_message_ids)))

    async def listen(self) -> AsyncGenerator[BaseEvent, None]:
        self._running = True
        await self._init_known_state()
        self._ws_task = asyncio.create_task(self._ws_loop())
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                yield event
            except asyncio.TimeoutError:
                pass
            except asyncio.CancelledError:
                break
        await self.stop()

    async def stop(self) -> None:
        self._running = False
        if self._ws_task:
            self._ws_task.cancel()
        self._persist()

    async def _ws_loop(self) -> None:
        while self._running:
            try:
                connect = await self._account.connect_websocket(_WS_URL)
                async with connect as ws:
                    await ws.send('40/chats,')
                    while self._running:
                        try:
                            raw = await asyncio.wait_for(ws.recv(), timeout=25.0)
                        except asyncio.TimeoutError:
                            await ws.send('2')
                            continue
                        if not isinstance(raw, str):
                            continue
                        if raw == '2':
                            await ws.send('3')
                            continue
                        if raw.startswith('42/chats,'):
                            data = raw[9:]
                            try:
                                payload = json.loads(data)
                                if isinstance(payload, list) and len(payload) == 2 and (payload[0] == 'message_created'):
                                    msg_data = payload[1]
                                    msg = parser.parse_message(msg_data)
                                    if msg.type.value == 'NOTIFICATION' and msg.metadata:
                                        ntype = msg.metadata.get('notificationType')
                                        if ntype in ('ORDER_PAYMENT', 'ORDER_COMPLETED'):
                                            order_data = msg_data.get('order')
                                            if order_data:
                                                order = parser.parse_order(order_data)
                                                if order.id not in self._known_order_ids:
                                                    self._known_order_ids.add(order.id)
                                                    self._known_order_statuses[order.id] = order.status.value
                                                    await self._queue.put(NewOrderEvent(order=order))
                                                    self._persist()
                                                else:
                                                    prev_status = self._known_order_statuses.get(order.id)
                                                    if prev_status != order.status.value:
                                                        self._known_order_statuses[order.id] = order.status.value
                                                        await self._queue.put(OrderStatusChangedEvent(order=order))
                                                        self._persist()
                                        elif ntype == 'REVIEW_CREATED':
                                            review_events = await self._sync_reviews()
                                            for rev_event in review_events:
                                                await self._queue.put(rev_event)
                                            if review_events:
                                                self._persist()
                                    author_data = msg_data.get('author', {})
                                    author = parser.parse_user(author_data) if author_data else None
                                    participants = [author] if author else []
                                    chat = Chat(id=msg_data['chatId'], participants=participants, last_message=msg)
                                    if msg.id not in self._seen_message_ids:
                                        self._mark_seen(msg.id)
                                        await self._queue.put(NewMessageEvent(message=msg, chat=chat))
                            except Exception as e:
                                log.warning('WS Parse Error: %s', e)
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.debug('WS Reconnect: %s', e)
                await asyncio.sleep(5.0)


    async def _sync_reviews(self) -> list[BaseEvent]:
        events: list[BaseEvent] = []
        try:
            reviews = await self._account.get_reviews(recipient_id=self._account.user_id, limit=20)
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
            log.warning('Reviews Sync Error: %s', e)
        return events

    async def _init_known_state(self) -> None:
        try:
            chats = await self._account.get_chats(limit=100)
            for chat in chats:
                if chat.last_message:
                    self._mark_seen(chat.last_message.id)
        except AuthExpiredError:
            raise
        except Exception as e:
            log.warning('Init Chats Error: %s', e)
        try:
            orders = await self._account.get_orders(limit=50)
            for order in orders:
                self._known_order_ids.add(order.id)
                self._known_order_statuses[order.id] = order.status.value
        except AuthExpiredError:
            raise
        except Exception as e:
            log.warning('Init Orders Error: %s', e)