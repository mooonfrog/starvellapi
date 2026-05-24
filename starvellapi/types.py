from __future__ import annotations

from typing import Optional

from .enums import (
    MessageType,
    OfferType,
    OrderStatus,
)


class User:
    """
    Описывает пользователя Starvell.

    :param id: Уникальный идентификатор пользователя.
    :type id: :obj:`int`

    :param username: Никнейм пользователя.
    :type username: :obj:`str`

    :param avatar: Ссылка на аватар пользователя, *опционально*.
    :type avatar: :obj:`str` or :obj:`None`

    :param is_online: Онлайн ли пользователь в данный момент.
    :type is_online: :obj:`bool`

    :param is_banned: Заблокирован ли пользователь.
    :type is_banned: :obj:`bool`

    :param rating: Рейтинг пользователя, *опционально*.
    :type rating: :obj:`float` or :obj:`None`

    :param reviews_count: Количество отзывов у пользователя.
    :type reviews_count: :obj:`int`

    :param kyc_status: Статус верификации KYC, *опционально*.
    :type kyc_status: :obj:`str` or :obj:`None`

    :param roles: Список ролей пользователя.
    :type roles: :obj:`list[str]`
    """

    def __init__(
        self,
        id: int,
        username: str,
        avatar: Optional[str] = None,
        is_online: bool = False,
        is_banned: bool = False,
        rating: Optional[float] = None,
        reviews_count: int = 0,
        kyc_status: Optional[str] = None,
        roles: Optional[list[str]] = None,
    ) -> None:
        self.id: int = id
        """Уникальный идентификатор пользователя."""

        self.username: str = username
        """Никнейм пользователя."""

        self.avatar: str | None = avatar
        """Ссылка на аватар пользователя."""

        self.is_online: bool = is_online
        """Онлайн ли пользователь в данный момент."""

        self.is_banned: bool = is_banned
        """Заблокирован ли пользователь."""

        self.rating: float | None = rating
        """Рейтинг пользователя."""

        self.reviews_count: int = reviews_count
        """Количество отзывов у пользователя."""

        self.kyc_status: str | None = kyc_status
        """Статус верификации KYC."""

        self.roles: list[str] = roles or []
        """Список ролей пользователя."""

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"


class Profile:
    """
    Описывает профиль текущего авторизованного пользователя.

    :param user: Основная информация о пользователе.
    :type user: :class:`starvellapi.types.User`

    :param email: Электронная почта аккаунта.
    :type email: :obj:`str`

    :param balance: Доступный баланс в рублях.
    :type balance: :obj:`float`

    :param held: Сумма на удержании в рублях.
    :type held: :obj:`float`

    :param purchase_orders: Количество заказов в роли покупателя.
    :type purchase_orders: :obj:`int`

    :param sales_orders: Количество заказов в роли продавца.
    :type sales_orders: :obj:`int`

    :param unread_chat_ids: Список ID непрочитанных чатов.
    :type unread_chat_ids: :obj:`list[str]`

    :param unread_ticket_ids: Список ID непрочитанных тикетов поддержки.
    :type unread_ticket_ids: :obj:`list[int]`

    :param description: Описание профиля.
    :type description: :obj:`str`

    :param banner: Ссылка на баннер профиля, *опционально*.
    :type banner: :obj:`str` or :obj:`None`

    :param is_selling_enabled: Включена ли продажа на аккаунте.
    :type is_selling_enabled: :obj:`bool`

    :param is_phone_linked: Привязан ли номер телефона.
    :type is_phone_linked: :obj:`bool`

    :param is_telegram_linked: Привязан ли Telegram.
    :type is_telegram_linked: :obj:`bool`

    :param has_password: Установлен ли пароль на аккаунте.
    :type has_password: :obj:`bool`
    """

    def __init__(
        self,
        user: User,
        email: str,
        balance: float,
        held: float,
        purchase_orders: int,
        sales_orders: int,
        unread_chat_ids: Optional[list[str]] = None,
        unread_ticket_ids: Optional[list[int]] = None,
        description: str = "",
        banner: Optional[str] = None,
        is_selling_enabled: bool = False,
        is_phone_linked: bool = False,
        is_telegram_linked: bool = False,
        has_password: bool = False,
    ) -> None:
        self.user: User = user
        """Основная информация о пользователе."""

        self.email: str = email
        """Электронная почта аккаунта."""

        self.balance: float = balance
        """Доступный баланс в рублях."""

        self.held: float = held
        """Сумма на удержании в рублях."""

        self.purchase_orders: int = purchase_orders
        """Количество заказов в роли покупателя."""

        self.sales_orders: int = sales_orders
        """Количество заказов в роли продавца."""

        self.unread_chat_ids: list[str] = unread_chat_ids or []
        """Список ID непрочитанных чатов."""

        self.unread_ticket_ids: list[int] = unread_ticket_ids or []
        """Список ID непрочитанных тикетов поддержки."""

        self.description: str = description
        """Описание профиля."""

        self.banner: str | None = banner
        """Ссылка на баннер профиля."""

        self.is_selling_enabled: bool = is_selling_enabled
        """Включена ли продажа на аккаунте."""

        self.is_phone_linked: bool = is_phone_linked
        """Привязан ли номер телефона."""

        self.is_telegram_linked: bool = is_telegram_linked
        """Привязан ли Telegram."""

        self.has_password: bool = has_password
        """Установлен ли пароль на аккаунте."""

    def __repr__(self) -> str:
        return f"<Profile user={self.user!r} balance={self.balance}>"


class SubCategory:
    """
    Описывает подкатегорию игры.

    :param id: Уникальный идентификатор подкатегории.
    :type id: :obj:`int`

    :param name: Название подкатегории.
    :type name: :obj:`str`

    :param filters: Список доступных фильтров подкатегории.
    :type filters: :obj:`list[dict]`
    """

    def __init__(
        self,
        id: int,
        name: str,
        filters: Optional[list[dict]] = None,
    ) -> None:
        self.id: int = id
        """Уникальный идентификатор подкатегории."""

        self.name: str = name
        """Название подкатегории."""

        self.filters: list[dict] = filters or []
        """Список доступных фильтров подкатегории."""

    def __repr__(self) -> str:
        return f"<SubCategory id={self.id} name={self.name!r}>"


class Offer:
    """
    Описывает оффер (объявление о продаже) на бирже Starvell.

    :param id: Уникальный идентификатор оффера.
    :type id: :obj:`int`

    :param type: Тип оффера.
    :type type: :class:`starvellapi.enums.OfferType`

    :param price: Цена оффера в виде строки.
    :type price: :obj:`str`

    :param availability: Доступное количество единиц.
    :type availability: :obj:`int`

    :param user: Продавец оффера.
    :type user: :class:`starvellapi.types.User`

    :param sub_category: Подкатегория оффера, *опционально*.
    :type sub_category: :class:`starvellapi.types.SubCategory` or :obj:`None`

    :param attributes: Список атрибутов оффера.
    :type attributes: :obj:`list[dict]`

    :param availability_unit: Единица измерения доступности.
    :type availability_unit: :obj:`str`

    :param descriptions: Описания оффера по языкам.
    :type descriptions: :obj:`dict`

    :param instant_delivery: Доступна ли мгновенная доставка.
    :type instant_delivery: :obj:`bool`

    :param auto_delivery: Доступна ли автоматическая доставка.
    :type auto_delivery: :obj:`bool`

    :param min_order_currency_amount: Минимальная сумма заказа, *опционально*.
    :type min_order_currency_amount: :obj:`float` or :obj:`None`

    :param badges: Список значков оффера.
    :type badges: :obj:`list[dict]`

    :param completion_rate: Процент успешного выполнения заказов, *опционально*.
    :type completion_rate: :obj:`float` or :obj:`None`
    """

    def __init__(
        self,
        id: int,
        type: OfferType,
        price: str,
        availability: int,
        user: User,
        sub_category: Optional[SubCategory] = None,
        attributes: Optional[list[dict]] = None,
        availability_unit: str = "UNITS",
        descriptions: Optional[dict] = None,
        instant_delivery: bool = False,
        auto_delivery: bool = False,
        min_order_currency_amount: Optional[float] = None,
        badges: Optional[list[dict]] = None,
        completion_rate: Optional[float] = None,
        game_id: Optional[int] = None,
        category_id: Optional[int] = None,
        is_active: bool = True,
    ) -> None:
        self.id: int = id
        """Уникальный идентификатор оффера."""

        self.type: OfferType = type
        """Тип оффера."""

        self.price: str = price
        """Цена оффера в виде строки."""

        self.availability: int = availability
        """Доступное количество единиц."""

        self.user: User = user
        """Продавец оффера."""

        self.sub_category: SubCategory | None = sub_category
        """Подкатегория оффера."""

        self.attributes: list[dict] = attributes or []
        """Список атрибутов оффера."""

        self.availability_unit: str = availability_unit
        """Единица измерения доступности."""

        self.descriptions: dict = descriptions or {}
        """Описания оффера по языкам."""

        self.instant_delivery: bool = instant_delivery
        """Доступна ли мгновенная доставка."""

        self.auto_delivery: bool = auto_delivery
        """Доступна ли автоматическая доставка."""

        self.min_order_currency_amount: float | None = min_order_currency_amount
        """Минимальная сумма заказа."""

        self.badges: list[dict] = badges or []
        """Список значков оффера."""

        self.completion_rate: float | None = completion_rate
        """Процент успешного выполнения заказов."""

        self.game_id: int | None = game_id
        """Идентификатор игры оффера."""

        self.category_id: int | None = category_id
        """Идентификатор родительской категории оффера."""

        self.is_active: bool = is_active
        """Активен ли оффер."""

    def __repr__(self) -> str:
        return f"<Offer id={self.id} price={self.price!r} user={self.user!r}>"


class OrderDetails:
    """
    Детали оффера, привязанного к заказу.

    :param game: Информация об игре.
    :type game: :obj:`dict`

    :param category: Информация о категории.
    :type category: :obj:`dict`

    :param sub_category: Информация о подкатегории.
    :type sub_category: :obj:`dict`
    """

    def __init__(self, game: dict, category: dict, sub_category: dict) -> None:
        self.game: dict = game
        """Информация об игре."""

        self.category: dict = category
        """Информация о категории."""

        self.sub_category: dict = sub_category
        """Информация о подкатегории."""


class Order:
    """
    Описывает заказ на бирже Starvell.

    :param id: Уникальный идентификатор заказа.
    :type id: :obj:`str`

    :param status: Текущий статус заказа.
    :type status: :class:`starvellapi.enums.OrderStatus`

    :param quantity: Количество единиц в заказе.
    :type quantity: :obj:`int`

    :param base_price: Базовая цена заказа в рублях.
    :type base_price: :obj:`float`

    :param total_price: Итоговая цена заказа в рублях.
    :type total_price: :obj:`float`

    :param seller_id: Идентификатор продавца.
    :type seller_id: :obj:`int`

    :param buyer_id: Идентификатор покупателя.
    :type buyer_id: :obj:`int`

    :param created_at: Дата и время создания заказа (ISO 8601).
    :type created_at: :obj:`str`

    :param offer_details: Детали оффера, *опционально*.
    :type offer_details: :class:`starvellapi.types.OrderDetails` or :obj:`None`

    :param order_args: Аргументы заказа (данные покупателя).
    :type order_args: :obj:`list[dict]`

    :param buyer: Покупатель заказа, *опционально*.
    :type buyer: :class:`starvellapi.types.User` or :obj:`None`
    """

    def __init__(
        self,
        id: str,
        status: OrderStatus,
        quantity: int,
        base_price: float,
        total_price: float,
        seller_id: int,
        buyer_id: int,
        created_at: str,
        offer_details: Optional[OrderDetails] = None,
        order_args: Optional[list[dict]] = None,
        buyer: Optional[User] = None,
    ) -> None:
        self.id: str = id
        """Уникальный идентификатор заказа."""

        self.status: OrderStatus = status
        """Текущий статус заказа."""

        self.quantity: int = quantity
        """Количество единиц в заказе."""

        self.base_price: float = base_price
        """Базовая цена заказа в рублях."""

        self.total_price: float = total_price
        """Итоговая цена заказа в рублях."""

        self.seller_id: int = seller_id
        """Идентификатор продавца."""

        self.buyer_id: int = buyer_id
        """Идентификатор покупателя."""

        self.created_at: str = created_at
        """Дата и время создания заказа (ISO 8601)."""

        self.offer_details: OrderDetails | None = offer_details
        """Детали оффера."""

        self.order_args: list[dict] = order_args or []
        """Аргументы заказа (данные покупателя)."""

        self.buyer: User | None = buyer
        """Покупатель заказа."""

    def __repr__(self) -> str:
        return f"<Order id={self.id!r} status={self.status}>"


class ChatMessage:
    """
    Описывает сообщение в чате Starvell.

    :param id: Уникальный идентификатор сообщения.
    :type id: :obj:`str`

    :param content: Текстовое содержимое сообщения.
    :type content: :obj:`str`

    :param type: Тип сообщения.
    :type type: :class:`starvellapi.enums.MessageType`

    :param author_id: Идентификатор автора сообщения.
    :type author_id: :obj:`int`

    :param chat_id: Идентификатор чата.
    :type chat_id: :obj:`str`

    :param created_at: Дата и время отправки сообщения (ISO 8601).
    :type created_at: :obj:`str`

    :param author: Краткая информация об авторе, *опционально*.
    :type author: :obj:`dict` or :obj:`None`

    :param metadata: Метаданные сообщения, *опционально*.
    :type metadata: :obj:`dict` or :obj:`None`

    :param is_hidden: Скрыто ли сообщение.
    :type is_hidden: :obj:`bool`

    :param images: Список прикреплённых изображений.
    :type images: :obj:`list[dict]`
    """

    def __init__(
        self,
        id: str,
        content: str,
        type: MessageType,
        author_id: int,
        chat_id: str,
        created_at: str,
        author: Optional[dict] = None,
        metadata: Optional[dict] = None,
        is_hidden: bool = False,
        images: Optional[list[dict]] = None,
    ) -> None:
        self.id: str = id
        """Уникальный идентификатор сообщения."""

        self.content: str = content
        """Текстовое содержимое сообщения."""

        self.type: MessageType = type
        """Тип сообщения."""

        self.author_id: int = author_id
        """Идентификатор автора сообщения."""

        self.chat_id: str = chat_id
        """Идентификатор чата."""

        self.created_at: str = created_at
        """Дата и время отправки сообщения (ISO 8601)."""

        self.author: dict | None = author
        """Краткая информация об авторе."""

        self.metadata: dict | None = metadata
        """Метаданные сообщения."""

        self.is_hidden: bool = is_hidden
        """Скрыто ли сообщение."""

        self.images: list[dict] = images or []
        """Список прикреплённых изображений."""

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id!r} author_id={self.author_id}>"


class Chat:
    """
    Описывает чат между пользователями Starvell.

    :param id: Уникальный идентификатор чата.
    :type id: :obj:`str`

    :param participants: Список участников чата.
    :type participants: :obj:`list[:class:`starvellapi.types.User`]`

    :param unread_count: Количество непрочитанных сообщений.
    :type unread_count: :obj:`int`

    :param last_message: Последнее сообщение в чате, *опционально*.
    :type last_message: :class:`starvellapi.types.ChatMessage` or :obj:`None`
    """

    def __init__(
        self,
        id: str,
        participants: list[User],
        unread_count: int = 0,
        last_message: Optional[ChatMessage] = None,
    ) -> None:
        self.id: str = id
        """Уникальный идентификатор чата."""

        self.participants: list[User] = participants
        """Список участников чата."""

        self.unread_count: int = unread_count
        """Количество непрочитанных сообщений."""

        self.last_message: ChatMessage | None = last_message
        """Последнее сообщение в чате."""

    def __repr__(self) -> str:
        return f"<Chat id={self.id!r} unread={self.unread_count}>"


class ReviewResponse:
    """
    Описывает ответ продавца на отзыв.

    :param id: Уникальный идентификатор ответа.
    :type id: :obj:`str`

    :param content: Текст ответа на отзыв.
    :type content: :obj:`str`
    """

    def __init__(self, id: str, content: str) -> None:
        self.id: str = id
        """Уникальный идентификатор ответа."""

        self.content: str = content
        """Текст ответа на отзыв."""

    def __repr__(self) -> str:
        return f"<ReviewResponse id={self.id!r}>"


class Review:
    """
    Описывает отзыв на продавца Starvell.

    :param id: Уникальный идентификатор отзыва.
    :type id: :obj:`str`

    :param content: Текст отзыва.
    :type content: :obj:`str`

    :param recipient_id: Идентификатор получателя отзыва (продавца).
    :type recipient_id: :obj:`int`

    :param author_id: Идентификатор автора отзыва.
    :type author_id: :obj:`int`

    :param rating: Оценка от 1 до 5.
    :type rating: :obj:`int`

    :param created_at: Дата и время создания отзыва (ISO 8601).
    :type created_at: :obj:`str`

    :param author_username: Никнейм автора отзыва.
    :type author_username: :obj:`str`

    :param author_avatar: Ссылка на аватар автора, *опционально*.
    :type author_avatar: :obj:`str` or :obj:`None`

    :param order_id: Идентификатор связанного заказа, *опционально*.
    :type order_id: :obj:`str` or :obj:`None`

    :param game_name: Название игры заказа.
    :type game_name: :obj:`str`

    :param amount: Количество единиц в заказе.
    :type amount: :obj:`int`

    :param is_hidden: Скрыт ли отзыв.
    :type is_hidden: :obj:`bool`

    :param response: Ответ продавца на отзыв, *опционально*.
    :type response: :class:`starvellapi.types.ReviewResponse` or :obj:`None`
    """

    def __init__(
        self,
        id: str,
        content: str,
        recipient_id: int,
        author_id: int,
        rating: int,
        created_at: str,
        author_username: str = "",
        author_avatar: Optional[str] = None,
        order_id: Optional[str] = None,
        game_name: str = "",
        amount: int = 0,
        is_hidden: bool = False,
        response: Optional[ReviewResponse] = None,
    ) -> None:
        self.id: str = id
        """Уникальный идентификатор отзыва."""

        self.content: str = content
        """Текст отзыва."""

        self.recipient_id: int = recipient_id
        """Идентификатор получателя отзыва (продавца)."""

        self.author_id: int = author_id
        """Идентификатор автора отзыва."""

        self.rating: int = rating
        """Оценка от 1 до 5."""

        self.created_at: str = created_at
        """Дата и время создания отзыва (ISO 8601)."""

        self.author_username: str = author_username
        """Никнейм автора отзыва."""

        self.author_avatar: str | None = author_avatar
        """Ссылка на аватар автора."""

        self.order_id: str | None = order_id
        """Идентификатор связанного заказа."""

        self.game_name: str = game_name
        """Название игры заказа."""

        self.amount: int = amount
        """Количество единиц в заказе."""

        self.is_hidden: bool = is_hidden
        """Скрыт ли отзыв."""

        self.response: ReviewResponse | None = response
        """Ответ продавца на отзыв."""

    def __repr__(self) -> str:
        return f"<Review id={self.id!r} rating={self.rating} author={self.author_username!r}>"


class TicketReply:
    """
    Описывает ответ в тикете поддержки.

    :param id: Уникальный идентификатор ответа.
    :type id: :obj:`int`

    :param ticket_id: Идентификатор тикета.
    :type ticket_id: :obj:`int`

    :param body: HTML-тело ответа.
    :type body: :obj:`str`

    :param body_text: Текстовое тело ответа без HTML.
    :type body_text: :obj:`str`

    :param created_at: Дата и время создания ответа (ISO 8601).
    :type created_at: :obj:`str`

    :param incoming: Является ли ответ входящим (от поддержки).
    :type incoming: :obj:`bool`

    :param attachments: Список вложений.
    :type attachments: :obj:`list[dict]`
    """

    def __init__(
        self,
        id: int,
        ticket_id: int,
        body: str,
        body_text: str,
        created_at: str,
        incoming: bool = True,
        attachments: Optional[list[dict]] = None,
    ) -> None:
        self.id: int = id
        """Уникальный идентификатор ответа."""

        self.ticket_id: int = ticket_id
        """Идентификатор тикета."""

        self.body: str = body
        """HTML-тело ответа."""

        self.body_text: str = body_text
        """Текстовое тело ответа без HTML."""

        self.created_at: str = created_at
        """Дата и время создания ответа (ISO 8601)."""

        self.incoming: bool = incoming
        """Является ли ответ входящим (от поддержки)."""

        self.attachments: list[dict] = attachments or []
        """Список вложений."""

    def __repr__(self) -> str:
        return f"<TicketReply id={self.id} ticket_id={self.ticket_id}>"
