from __future__ import annotations


class StarvellAPIError(Exception):
    """Базовое исключение библиотеки StarvellAPI."""


class AuthExpiredError(StarvellAPIError):
    """
    Сессия истекла или недействительна.

    Выбрасывается при получении HTTP 401 или 403.
    """


class TransientError(StarvellAPIError):
    """
    Временная сетевая ошибка или ошибка сервера (5xx).

    Выбрасывается после исчерпания попыток повтора запроса.
    """


class BotCheckDetectedException(StarvellAPIError):
    """
    Обнаружена проверка на бота (DDoS-Guard).

    Выбрасывается, когда DDoS-Guard блокирует запрос.
    """


class RequestFailedError(StarvellAPIError):
    """
    Запрос завершился с неожиданным HTTP-статусом.

    :param status_code: HTTP-статус ответа.
    :type status_code: :obj:`int`

    :param url: URL запроса.
    :type url: :obj:`str`

    :param message: Сообщение об ошибке.
    :type message: :obj:`str`
    """

    def __init__(self, status_code: int, url: str, message: str = "") -> None:
        self.status_code: int = status_code
        """HTTP-статус ответа."""

        self.url: str = url
        """URL запроса."""

        super().__init__(f"HTTP {status_code} на {url}: {message}")


class MessageNotDeliveredError(StarvellAPIError):
    """
    Сообщение не было доставлено.

    :param chat_id: Идентификатор чата.
    :type chat_id: :obj:`str`
    """

    def __init__(self, chat_id: str) -> None:
        self.chat_id: str = chat_id
        """Идентификатор чата."""

        super().__init__(f"Сообщение не доставлено в чат {chat_id}")
