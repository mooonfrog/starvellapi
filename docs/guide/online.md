# Онлайн-статус

`OnlineKeeper` поддерживает websocket-соединение, чтобы Starvell показывал тебя как «онлайн».

## Запуск

```python
import asyncio
from starvellapi import Account, OnlineKeeper

async def main():
    async with Account(session_cookie="...") as acc:
        keeper = OnlineKeeper(acc)
        await keeper.start()
        try:
            await asyncio.sleep(3600)
        finally:
            await keeper.stop()

asyncio.run(main())
```

Или через context manager:

```python
async with Account(session_cookie="...") as acc:
    async with OnlineKeeper(acc):
        await asyncio.sleep(3600)
```

## Параметры

- `reconnect_delay` (`float`, по умолчанию 5.0) — задержка перед переподключением после обрыва.

## Поведение

- Соединение к `wss://starvell.com/socket.io/?EIO=4&transport=websocket`.
- Auth — через cookie `session` (берётся из `Account`).
- Ping/pong: socket.io шлёт `2`, мы отвечаем `3`. Интервал и таймаут читаются из handshake-payload.
- При падении соединения, ошибке таймаута или другой сетевой проблеме keeper переподключится сам.

## Жизненный цикл

| Метод | Что делает |
|-------|-----------|
| `start()` | Запускает фоновую таску. Идемпотентно — повторный вызов ничего не делает. |
| `stop()` | Отменяет таску и ждёт её завершения. |
| `is_running` | Проверка состояния. |

## Совмещение с Runner

`OnlineKeeper` и `Runner` независимы и могут работать одновременно:

```python
async with Account(session_cookie="...") as acc:
    async with OnlineKeeper(acc):
        runner = Runner(acc)
        async for event in runner.listen():
            handle(event)
```
