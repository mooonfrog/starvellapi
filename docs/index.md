# starvellapi

Асинхронная библиотека для [starvell.com](https://starvell.com) на `httpx` и `websockets`.

## Что внутри

- [`Account`](api/account.md) — async HTTP-клиент Starvell. Профиль, офферы, заказы, чаты, отзывы, тикеты.
- [`Runner`](api/runner.md) — long-polling апдейтер: новые сообщения, заказы, смена статусов, новые отзывы.
- [`OnlineKeeper`](api/online.md) — websocket keepalive статуса «онлайн».
- [Типы](api/types.md) и [енумы](api/enums.md) под все ответы API.
- [Иерархия исключений](api/exceptions.md) с явным разделением временных и фатальных ошибок.

## Установка

```bash
pip install git+https://github.com/mooonfrog/starvellapi.git
```

## Минимальный пример

```python
import asyncio
from starvellapi import Account

async def main():
    async with Account(session_cookie="...") as acc:
        me = await acc.get_profile()
        print(me.user.username, me.balance)

asyncio.run(main())
```

Дальше — [быстрый старт](quickstart.md).
