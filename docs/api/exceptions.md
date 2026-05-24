# Исключения

## StarvellAPIError

::: starvellapi.StarvellAPIError
    options:
      show_bases: true

## AuthExpiredError

::: starvellapi.AuthExpiredError
    options:
      show_bases: true

## TransientError

::: starvellapi.TransientError
    options:
      show_bases: true

## RequestFailedError

::: starvellapi.RequestFailedError
    options:
      show_bases: true
      members_order: source

## MessageNotDeliveredError

::: starvellapi.MessageNotDeliveredError
    options:
      show_bases: true
      members_order: source

## Когда что ловить

- `AuthExpiredError` — сессия протухла. Обнови `session_cookie` и переоткрой `Account`.
- `TransientError` — сетевой таймаут или 5xx после трёх попыток. Обычно достаточно подождать и повторить вызов.
- `RequestFailedError` — неожиданный HTTP-статус с телом ответа.
- `MessageNotDeliveredError` — сообщение не доставлено в чат.
- `StarvellAPIError` — родительский класс, ловите его, если хотите перехватить любую ошибку библиотеки.
