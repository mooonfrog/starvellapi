# Слушаем события

API Starvell не отдаёт push-события для аккаунта, поэтому `Runner` периодически опрашивает чаты, заказы и отзывы и сравнивает их с известным состоянием.

## Простой случай

```python
import asyncio
from starvellapi import Account, Runner
from starvellapi import (
    NewMessageEvent,
    NewOrderEvent,
    OrderStatusChangedEvent,
    NewReviewEvent,
)

async def main():
    async with Account(session_cookie="...") as acc:
        runner = Runner(acc, poll_interval=3.0)
        try:
            async for event in runner.listen():
                if isinstance(event, NewMessageEvent):
                    print("msg:", event.chat.id, event.message.content)
                elif isinstance(event, NewOrderEvent):
                    print("order:", event.order.id, event.order.status)
                elif isinstance(event, OrderStatusChangedEvent):
                    print("status:", event.order.id, event.order.status)
                elif isinstance(event, NewReviewEvent):
                    print("review:", event.review.rating)
        finally:
            await runner.stop()

asyncio.run(main())
```

## Persistence через `state_store`

Без state store `Runner` пропустит первые события (он сначала запоминает текущее состояние, чтобы не выдать всю историю заказов как новые события). Чтобы пережить рестарт без потери, передай объект с методами `get(key, default)` и `set(key, value)`. Простой JSON-стор:

```python
import json
from pathlib import Path

class JsonStateStore:
    def __init__(self, path):
        self.path = Path(path)
        self._data = json.loads(self.path.read_text()) if self.path.exists() else {}

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.path.write_text(json.dumps(self._data, ensure_ascii=False))

state = JsonStateStore("./state.json")
runner = Runner(acc, poll_interval=3.0, state_store=state)
```

После каждого тика `Runner` сохранит:

- `chat_msg_ids` — последний `id` сообщения по каждому чату
- `order_ids`, `order_statuses` — известные заказы и их статусы
- `review_ids` — id отзывов
- `reviews_initialized` — флаг первой инициализации отзывов

## Остановка

`Runner.listen()` — async-генератор. Чтобы корректно остановить, либо выходи из цикла (он сам завершится при `CancelledError`), либо явно вызови `await runner.stop()`. После `stop()` `Runner` сохранит состояние в `state_store`, если он передан.

## Ошибки

- `AuthExpiredError` пробрасывается из `listen()` — сессия мертва, цикл нужно остановить и обновить cookie.
- Прочие исключения логируются как `WARNING` и не прерывают цикл.
