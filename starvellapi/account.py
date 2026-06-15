from __future__ import annotations
import asyncio
import ssl
from typing import Any, Optional
import certifi
import httpx
from .exceptions import AuthExpiredError, BotCheckDetectedException, TransientError
from .enums import OfferSortBy, OrderUserType, SortDirection
from .types import Chat, ChatMessage, Offer, Order, Profile, Review, TicketReply
from . import parser
_BASE_URL = 'https://starvell.com/api'
_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'

class Account:
    """
    Основной класс для взаимодействия с API Starvell.

    Используется как асинхронный контекстный менеджер::

        async with Account(session_cookie="...") as account:
            profile = await account.get_profile()

    :param session_cookie: Значение cookie ``session`` авторизованного пользователя.
    :type session_cookie: :obj:`str`

    :param proxy: Прокси-сервер в формате ``http://user:pass@host:port``, *опционально*.
    :type proxy: :obj:`str` or :obj:`None`

    :param ddg5: Cookie для обхода защиты DDoS-Guard (полное название: `__ddg5_`).
        **Примечание:** эта Cookie "умирает" каждый раз, когда:
        - меняется IP
        - меняется User-Agent / TLS fingerprint
        - сервер обновил ключи/алгоритм
        Чтобы API работал, эта Cookie должна быть взята из Cookie-данных аккаунта, токен которого вы указали, и запросы должны идти с того же IP-адреса, под которым Вы авторизовывались на starvell.com.
        Если она недействительна, при запросах будет вызываться исключение `BotCheckDetectedException`.
    :type ddg5: :obj:`str` or :obj:`None`
    """

    def __init__(self, session_cookie: str, proxy: Optional[str]=None, user_agent: Optional[str]=None, ddg5: Optional[str]=None) -> None:
        self._session_cookie: str = session_cookie
        self._proxy: str | None = proxy
        self._user_agent: str = user_agent or _USER_AGENT
        self._ddg5: Optional[str] = ddg5
        self._http: Optional[httpx.AsyncClient] = None
        self._user_id: Optional[int] = None

    async def __aenter__(self) -> Account:
        await self._open()
        profile = await self.get_profile()
        self._user_id = profile.user.id
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self._close()

    async def _open(self) -> None:
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        ssl_ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        cookies = {'session': self._session_cookie, 'starvell.theme': 'dark', 'starvell.time_zone': 'Europe/Moscow'}
        if self._ddg5:
            cookies['__ddg5_'] = self._ddg5
        
        headers = {
            'User-Agent': self._user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Origin': 'https://starvell.com',
            'Referer': 'https://starvell.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        
        kw: dict[str, Any] = dict(
            base_url=_BASE_URL, 
            headers=headers, 
            cookies=cookies, 
            timeout=httpx.Timeout(25.0, connect=10.0, read=25.0), 
            verify=ssl_ctx, 
            follow_redirects=True,
            http2=True
        )
        if self._proxy:
            kw['proxy'] = self._proxy
        self._http = httpx.AsyncClient(**kw)

    async def _close(self) -> None:
        if self._http:
            await self._http.aclose()
            self._http = None

    @property
    def http(self) -> httpx.AsyncClient:
        """
        Возвращает активный HTTP-клиент.

        :raises RuntimeError: Если клиент не был инициализирован.
        :rtype: :class:`httpx.AsyncClient`
        """
        if self._http is None:
            raise RuntimeError('Клиент не открыт. Используйте async with Account(...) as account.')
        return self._http

    @property
    def user_id(self) -> int:
        """
        Возвращает идентификатор текущего пользователя.

        :raises RuntimeError: Если профиль ещё не загружен.
        :rtype: :obj:`int`
        """
        if self._user_id is None:
            raise RuntimeError('user_id не загружен. Дождитесь завершения __aenter__.')
        return self._user_id

    async def connect_websocket(self, url: str) -> Any:
        """
        Устанавливает WebSocket-соединение с учётом прокси и DDoS-Guard.
        """
        import websockets
        from urllib.parse import urlparse
        
        cookie_str = f'session={self._session_cookie}; starvell.theme=dark; starvell.time_zone=Europe/Moscow'
        if self._ddg5:
            cookie_str += f'; __ddg5_={self._ddg5}'
            
        headers = {
            'User-Agent': self._user_agent,
            'Origin': 'https://starvell.com',
            'Cookie': cookie_str,
            'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        }
        
        kw: dict[str, Any] = {}
        try:
            kw['additional_headers'] = headers
        except TypeError:
            kw['extra_headers'] = headers

        if self._proxy:
            from python_socks.asyncio.proxy import Proxy
            p = urlparse(self._proxy)
            proxy_type = p.scheme
            if proxy_type == 'http':
                from python_socks import ProxyType
                proxy_type = ProxyType.HTTP
            elif proxy_type == 'socks5':
                from python_socks import ProxyType
                proxy_type = ProxyType.SOCKS5
            elif proxy_type == 'socks4':
                from python_socks import ProxyType
                proxy_type = ProxyType.SOCKS4
            
            proxy = Proxy.create(
                proxy_type=proxy_type,
                host=p.hostname,
                port=p.port,
                username=p.username,
                password=p.password,
                rdns=True
            )
            sock = await proxy.connect(dest_host=urlparse(url).hostname, dest_port=443)
            return websockets.connect(url, sock=sock, server_hostname=urlparse(url).hostname, **kw)
        
        return websockets.connect(url, **kw)

    async def _request(self, method: str, url: str, **kw: Any) -> httpx.Response:
        """
        Выполняет HTTP-запрос с автоматическим повтором при временных ошибках.

        :param method: HTTP-метод (``GET``, ``POST`` и т.д.).
        :type method: :obj:`str`

        :param url: Относительный или абсолютный URL.
        :type url: :obj:`str`

        :return: Объект HTTP-ответа.
        :rtype: :class:`httpx.Response`

        :raises AuthExpiredError: При HTTP 401 или 403.
        :raises TransientError: При сетевой ошибке или HTTP 5xx после повторов.
        """
        attempts = 0
        last_exc: Exception | None = None
        while attempts < 3:
            attempts += 1
            try:
                resp = await self.http.request(method, url, **kw)
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.RemoteProtocolError, httpx.ReadError, httpx.WriteError) as e:
                last_exc = e
                if attempts >= 3:
                    raise TransientError(f'{type(e).__name__}: {e}') from e
                await asyncio.sleep(1.5 * attempts)
                continue
            except httpx.HTTPError as e:
                raise TransientError(f'{type(e).__name__}: {e}') from e
            if resp.status_code == 403:
                if 'ddos-guard' in resp.headers.get('server', '').lower():
                    raise BotCheckDetectedException(
                        f'DDoS-Guard check detected on {url}. '
                        'Возможные причины: \n'
                        '1. Вы получили куку на другом IP (например, дома), а бот запущен на сервере без прокси.\n'
                        '2. User-Agent в конфиге бота не совпадает с тем, в котором вы брали куку.\n'
                        '3. Кука __ddg5_ протухла.'
                    )
                raise AuthExpiredError(f'HTTP {resp.status_code} на {url}')
            if resp.status_code == 401:
                raise AuthExpiredError(f'HTTP {resp.status_code} на {url}')
            if 500 <= resp.status_code < 600:

                last_exc = Exception(f'HTTP {resp.status_code}')
                if attempts >= 3:
                    raise TransientError(f'HTTP {resp.status_code} на {url}')
                await asyncio.sleep(1.5 * attempts)
                continue
            resp.raise_for_status()
            return resp
        raise TransientError(str(last_exc))

    async def _get(self, url: str, **kw: Any) -> httpx.Response:
        return await self._request('GET', url, **kw)

    async def _post(self, url: str, **kw: Any) -> httpx.Response:
        return await self._request('POST', url, **kw)

    async def get_profile(self) -> Profile:
        """
        Возвращает профиль текущего авторизованного пользователя.

        :return: Профиль пользователя.
        :rtype: :class:`starvellapi.types.Profile`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        resp = await self._get('/profiles/me')
        return parser.parse_profile(resp.json())

    async def update_description(self, description: str) -> None:
        """
        Обновляет описание профиля текущего пользователя.

        :param description: Новый текст описания профиля.
        :type description: :obj:`str`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        await self._post('/users/update', json={'userId': self.user_id, 'description': description})

    async def get_offers_by_category(self, category_id: int, *, limit: int=100, offset: int=0, online_only: bool=False, attributes: Optional[list[dict]]=None, sort_by: OfferSortBy=OfferSortBy.PRICE, sort_dir: SortDirection=SortDirection.DESC, with_completion_rates: bool=True) -> list[Offer]:
        """
        Возвращает список офферов в указанной категории.

        :param category_id: Идентификатор категории.
        :type category_id: :obj:`int`

        :param limit: Максимальное количество офферов за запрос.
        :type limit: :obj:`int`

        :param offset: Смещение для пагинации.
        :type offset: :obj:`int`

        :param online_only: Показывать только офферы онлайн-продавцов.
        :type online_only: :obj:`bool`

        :param attributes: Список атрибутов для фильтрации, *опционально*.
        :type attributes: :obj:`list[dict]` or :obj:`None`

        :param sort_by: Поле для сортировки.
        :type sort_by: :class:`starvellapi.enums.OfferSortBy`

        :param sort_dir: Направление сортировки.
        :type sort_dir: :class:`starvellapi.enums.SortDirection`

        :param with_completion_rates: Включать процент выполнения в ответ.
        :type with_completion_rates: :obj:`bool`

        :return: Список офферов.
        :rtype: :obj:`list[:class:`starvellapi.types.Offer`]`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        resp = await self._post('/offers/list-by-category', json={'limit': limit, 'offset': offset, 'categoryId': category_id, 'onlyOnlineUsers': online_only, 'attributes': attributes or [], 'sortBy': sort_by.value, 'sortDir': sort_dir.value, 'withCompletionRates': with_completion_rates})
        return [parser.parse_offer(o) for o in resp.json()]

    async def update_offer(self, offer_id: int, *, availability: Optional[int]=None, price: Optional[str]=None, min_order: Optional[float]=None, active: Optional[bool]=None) -> None:
        """
        Частично обновляет параметры оффера.

        :param offer_id: Идентификатор оффера.
        :type offer_id: :obj:`int`

        :param availability: Новое доступное количество единиц, *опционально*.
        :type availability: :obj:`int` or :obj:`None`

        :param price: Новая цена оффера, *опционально*.
        :type price: :obj:`str` or :obj:`None`

        :param min_order: Новая минимальная сумма заказа, *опционально*.
        :type min_order: :obj:`float` or :obj:`None`

        :param active: Активен ли оффер, *опционально*.
        :type active: :obj:`bool` or :obj:`None`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        body: dict[str, Any] = {}
        if availability is not None:
            body['availability'] = availability
        if price is not None:
            body['price'] = price
        if min_order is not None:
            body['minOrderCurrencyAmount'] = min_order
        if active is not None:
            body['isActive'] = active
        await self._post(f'/offers/{offer_id}/partial-update', json=body)

    async def get_orders(self, *, user_type: OrderUserType=OrderUserType.SELLER, status: Optional[str]=None, with_buyer: bool=True, limit: int=20, offset: int=0) -> list[Order]:
        """
        Возвращает список заказов аккаунта.

        :param user_type: Роль пользователя в заказе (продавец или покупатель).
        :type user_type: :class:`starvellapi.enums.OrderUserType`

        :param status: Фильтр по статусу заказа, *опционально*.
        :type status: :obj:`str` or :obj:`None`

        :param with_buyer: Включать информацию о покупателе в ответ.
        :type with_buyer: :obj:`bool`

        :param limit: Максимальное количество заказов за запрос.
        :type limit: :obj:`int`

        :param offset: Смещение для пагинации.
        :type offset: :obj:`int`

        :return: Список заказов.
        :rtype: :obj:`list[:class:`starvellapi.types.Order`]`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        resp = await self._post('/orders/list', json={'filter': {'status': status, 'userType': user_type.value}, 'with': {'buyer': with_buyer}, 'limit': limit, 'offset': offset})
        return [parser.parse_order(o) for o in resp.json()]

    async def refund_order(self, order_id: str) -> None:
        """
        Оформляет возврат по заказу.

        :param order_id: Идентификатор заказа.
        :type order_id: :obj:`str`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        await self._post('/orders/refund', json={'orderId': order_id})

    async def mark_order_completed(self, order_id: str) -> None:
        """
        Отмечает заказ как выполненный со стороны продавца.

        :param order_id: Идентификатор заказа.
        :type order_id: :obj:`str`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        await self._post(f'/orders/{order_id}/mark-seller-completed', json={'id': order_id})

    async def get_chats(self, limit: int=50, offset: int=0) -> list[Chat]:
        """
        Возвращает список чатов аккаунта.

        :param limit: Максимальное количество чатов за запрос.
        :type limit: :obj:`int`

        :param offset: Смещение для пагинации.
        :type offset: :obj:`int`

        :return: Список чатов.
        :rtype: :obj:`list[:class:`starvellapi.types.Chat`]`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        resp = await self._post('/chats/list', params={'offset': offset, 'limit': limit})
        return [parser.parse_chat(c) for c in resp.json()]

    async def get_chat_messages(self, chat_id: str, interlocutor_id: int, limit: int=50) -> list[ChatMessage]:
        """
        Возвращает историю сообщений в чате.

        :param chat_id: Идентификатор чата.
        :type chat_id: :obj:`str`

        :param interlocutor_id: Идентификатор собеседника.
        :type interlocutor_id: :obj:`int`

        :param limit: Максимальное количество сообщений за запрос.
        :type limit: :obj:`int`

        :return: Список сообщений.
        :rtype: :obj:`list[:class:`starvellapi.types.ChatMessage`]`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        resp = await self._post('/bff/chat-page', json={'interlocutorId': interlocutor_id, 'messagesListDto': {'chatId': chat_id, 'limit': limit}})
        items = resp.json().get('messagesListResult', {}).get('items', [])
        return [parser.parse_message(m) for m in items]

    async def send_typing(self, chat_id: str, is_typing: bool=True) -> None:
        """
        Отправляет статус печатания в чат.

        :param chat_id: Идентификатор чата.
        :type chat_id: :obj:`str`

        :param is_typing: Печатает ли пользователь в данный момент.
        :type is_typing: :obj:`bool`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        await self._post('/chats/send-typing', json={'chatId': chat_id, 'isTyping': is_typing})

    async def read_chat(self, chat_id: str) -> None:
        """
        Отмечает чат как прочитанный.

        :param chat_id: Идентификатор чата.
        :type chat_id: :obj:`str`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        await self._post('/chats/read', json={'chatId': chat_id})

    async def send_message(self, chat_id: str, content: str, socket_id: Optional[str]=None) -> ChatMessage:
        """
        Отправляет текстовое сообщение в чат.

        :param chat_id: Идентификатор чата.
        :type chat_id: :obj:`str`

        :param content: Текст сообщения.
        :type content: :obj:`str`

        :param socket_id: Идентификатор WebSocket-соединения для дедупликации, *опционально*.
        :type socket_id: :obj:`str` or :obj:`None`

        :return: Отправленное сообщение.
        :rtype: :class:`starvellapi.types.ChatMessage`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        body: dict[str, Any] = {'chatId': chat_id, 'content': content}
        if socket_id is not None:
            body['clientSocketId'] = socket_id
        resp = await self._post('/messages/send', json=body)
        return parser.parse_message(resp.json().get('message', {}))

    async def send_image(self, chat_id: str, image_bytes: bytes, socket_id: Optional[str]=None) -> Message:
        """
        Отправляет изображение в чат.

        :param chat_id: Идентификатор чата.
        :type chat_id: :obj:`str`

        :param image_bytes: Содержимое изображения в виде байтов.
        :type image_bytes: :obj:`bytes`

        :param socket_id: Идентификатор WebSocket-соединения для дедупликации, *опционально*.
        :type socket_id: :obj:`str` or :obj:`None`

        :return: Отправленное сообщение с изображением.
        :rtype: :class:`starvellapi.types.ChatMessage`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        params = {'chatId': chat_id}
        if socket_id:
            params['clientSocketId'] = socket_id
        files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
        resp = await self._post('/messages/send-with-image', params=params, files=files)
        return parser.parse_message(resp.json().get('message', {}))

    async def get_reviews(self, recipient_id: int, limit: int=20, offset: int=0) -> list[Review]:
        """
        Возвращает список отзывов на пользователя.

        :param recipient_id: Идентификатор пользователя, отзывы которого нужно получить.
        :type recipient_id: :obj:`int`

        :param limit: Максимальное количество отзывов за запрос.
        :type limit: :obj:`int`

        :param offset: Смещение для пагинации.
        :type offset: :obj:`int`

        :return: Список отзывов.
        :rtype: :obj:`list[:class:`starvellapi.types.Review`]`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        resp = await self._post('/reviews/list', json={'filter': {'recipientId': recipient_id}, 'pagination': {'offset': offset, 'limit': limit}})
        return [parser.parse_review(r) for r in resp.json()]

    async def create_review_response(self, review_id: str, content: str) -> dict:
        """
        Создаёт ответ продавца на отзыв.

        :param review_id: Идентификатор отзыва.
        :type review_id: :obj:`str`

        :param content: Текст ответа на отзыв.
        :type content: :obj:`str`

        :return: Словарь с данными созданного ответа.
        :rtype: :obj:`dict`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        resp = await self._post('/review-responses/create', json={'content': content, 'reviewId': review_id})
        return resp.json()

    async def update_review_response(self, response_id: str, review_id: str, content: str) -> dict:
        """
        Обновляет ответ продавца на отзыв.

        :param response_id: Идентификатор ответа на отзыв.
        :type response_id: :obj:`str`

        :param review_id: Идентификатор отзыва.
        :type review_id: :obj:`str`

        :param content: Новый текст ответа.
        :type content: :obj:`str`

        :return: Словарь с данными обновлённого ответа.
        :rtype: :obj:`dict`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        resp = await self._post(f'/review-responses/{response_id}/update', json={'content': content, 'reviewId': review_id})
        return resp.json()

    async def delete_review_response(self, response_id: str) -> None:
        """
        Удаляет ответ продавца на отзыв.

        :param response_id: Идентификатор ответа на отзыв.
        :type response_id: :obj:`str`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        await self._post(f'/review-responses/{response_id}/delete')

    async def reply_ticket(self, ticket_id: int, body: str) -> TicketReply:
        """
        Отвечает на тикет в службу поддержки.

        :param ticket_id: Идентификатор тикета.
        :type ticket_id: :obj:`int`

        :param body: Текст ответа.
        :type body: :obj:`str`

        :return: Объект ответа на тикет.
        :rtype: :class:`starvellapi.types.TicketReply`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        resp = await self._post('/support/reply', data={'ticketId': str(ticket_id), 'body': body})
        return parser.parse_ticket_reply(resp.json())

    async def close_ticket(self, ticket_id: int) -> None:
        """
        Закрывает тикет поддержки.

        :param ticket_id: Идентификатор тикета.
        :type ticket_id: :obj:`int`

        :raises AuthExpiredError: Если сессия истекла.
        :raises TransientError: При временной ошибке сети или сервера.
        """
        await self._post('/support/close', json={'ticketId': ticket_id})
