# Работа с Account

`Account` — основной класс для работы с API. Это async context manager, поэтому используется внутри `async with`:

```python
from starvellapi import Account

async with Account(session_cookie="...") as acc:
    profile = await acc.get_profile()
```

## Что происходит при входе в context manager

1. Создаётся `httpx.AsyncClient` с куками, заголовками и опциональным прокси.
2. Запрашивается `/profiles/me`, чтобы убедиться в валидности сессии.
3. `acc.user_id` заполняется идентификатором текущего пользователя.

Если сессия невалидна — поднимется {py:exc}`starvellapi.AuthExpiredError`.

## Доступ к raw httpx-клиенту

Если нужен эндпоинт, для которого нет высокоуровневого метода, можно использовать `acc.http`:

```python
resp = await acc.http.post("/some/endpoint", json={"foo": "bar"})
resp.raise_for_status()
data = resp.json()
```

## Ретраи

Все методы автоматически повторяют запрос до 3 раз с задержкой 1.5–4.5с при:

- `httpx.ReadTimeout`, `httpx.ConnectTimeout`
- `httpx.RemoteProtocolError`, `ReadError`, `WriteError`
- HTTP 5xx

После исчерпания попыток поднимется {py:exc}`starvellapi.TransientError`.

## Аутентификация

Если сервер вернул 401 или 403, методы поднимут {py:exc}`starvellapi.AuthExpiredError`. Это значит cookie протухла. Обработка обычно выглядит так:

```python
from starvellapi import Account, AuthExpiredError

while True:
    try:
        async with Account(session_cookie=current_cookie) as acc:
            await do_work(acc)
        break
    except AuthExpiredError:
        current_cookie = ask_user_for_new_cookie()
```

## Прокси

```python
async with Account(
    session_cookie="...",
    proxy="http://user:pass@host:8080",
) as acc:
    ...
```

`httpx` поддерживает HTTP, HTTPS и SOCKS5 (через `httpx-socks`).
