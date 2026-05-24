# starvellapi

Асинхронный Python-клиент для [starvell.com](https://starvell.com) на `httpx` и `websockets`.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docs](https://img.shields.io/badge/docs-readthedocs-8CA1AF.svg)](https://starvell.readthedocs.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Покрывает профиль, офферы, заказы, чаты, отзывы, тикеты поддержки. Плюс long-polling апдейтер событий и keepalive онлайн-статуса через websocket.

## Установка

```bash
pip install git+https://github.com/mooonfrog/starvellapi.git
```

Зависимости: `httpx>=0.27`, `certifi`, `websockets>=12`.

## Быстрый старт

```python
import asyncio
from starvellapi import Account

async def main():
    async with Account(session_cookie="...") as acc:
        me = await acc.get_profile()
        print(me.user.username, "balance:", me.balance, "₽")

        chats = await acc.get_chats(limit=10)
        if chats:
            await acc.send_message(chats[0].id, "привет")

asyncio.run(main())
```

### Слушать события

```python
import asyncio
from starvellapi import Account, Runner
from starvellapi import NewMessageEvent, NewOrderEvent, NewReviewEvent

async def main():
    async with Account(session_cookie="...") as acc:
        runner = Runner(acc, poll_interval=3.0)
        async for event in runner.listen():
            if isinstance(event, NewMessageEvent):
                print("msg:", event.chat.id, event.message.content)
            elif isinstance(event, NewOrderEvent):
                print("order:", event.order.id, event.order.status)
            elif isinstance(event, NewReviewEvent):
                print("review:", event.review.rating, event.review.content)

asyncio.run(main())
```

### Онлайн-статус

```python
from starvellapi import Account, OnlineKeeper

async with Account(session_cookie="...") as acc:
    async with OnlineKeeper(acc):
        await asyncio.sleep(3600)
```

## Что доступно

- **`Account`** — async HTTP-клиент с авто-ретраями на 5xx и сетевые ошибки, обработкой 401/403 как `AuthExpiredError`. Методы: `get_profile`, `get_offers_by_category`, `update_offer`, `get_orders`, `refund_order`, `mark_order_completed`, `get_chats`, `get_chat_messages`, `send_typing`, `read_chat`, `send_message`, `get_reviews`, `create_review_response`, `update_review_response`, `delete_review_response`, `reply_ticket`, `close_ticket`, `update_description`.
- **`Runner`** — поллинг событий: новые сообщения, заказы, смена статусов, отзывы. Поддерживает persistence через `state_store`.
- **`OnlineKeeper`** — websocket keepalive статуса «онлайн» с авто-переподключением.
- **Типы**: `User`, `Profile`, `Offer`, `Order`, `OrderDetails`, `Chat`, `ChatMessage`, `Review`, `ReviewResponse`, `TicketReply`, `SubCategory`.
- **Енумы**: `OrderStatus`, `OrderUserType`, `OfferType`, `OfferSortBy`, `SortDirection`, `MessageType`, `EventType`.
- **Исключения**: `StarvellAPIError`, `AuthExpiredError`, `TransientError`, `RequestFailedError`, `MessageNotDeliveredError`.

## Документация

Полная документация: <https://starvell.readthedocs.io>

## Получить session cookie

Залогинься на [starvell.com](https://starvell.com), открой DevTools → **Application → Cookies → starvell.com**. Скопируй значение cookie с именем `session`.

## Сборка документации локально

```bash
pip install -r docs/requirements.txt
mkdocs serve
```

## Лицензия

[MIT](LICENSE)

## Кредиты

- Автор: [@yusxe](https://t.me/yusxe)
- Исходно — часть проекта [starvellbot](https://github.com/mooonfrog/starvellbot)
