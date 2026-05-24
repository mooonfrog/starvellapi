from __future__ import annotations

from typing import Optional

from .enums import MessageType, OfferType, OrderStatus
from .types import (
    Chat,
    ChatMessage,
    Offer,
    Order,
    OrderDetails,
    Profile,
    Review,
    ReviewResponse,
    SubCategory,
    TicketReply,
    User,
)


def parse_user(d: dict) -> Optional[User]:
    """
    Разбирает словарь в объект :class:`starvellapi.types.User`.

    :param d: Словарь с данными пользователя из API.
    :type d: :obj:`dict`

    :return: Объект пользователя или :obj:`None`, если словарь пуст.
    :rtype: :class:`starvellapi.types.User` or :obj:`None`
    """
    if not d:
        return None
    return User(
        id=d["id"],
        username=d.get("username", ""),
        avatar=d.get("avatar"),
        is_online=d.get("isOnline", False),
        is_banned=d.get("isBanned", False),
        rating=d.get("rating"),
        reviews_count=d.get("reviewsCount", 0),
        kyc_status=d.get("kycStatus"),
        roles=d.get("roles", []),
    )


def parse_profile(d: dict) -> Profile:
    """
    Разбирает словарь в объект :class:`starvellapi.types.Profile`.

    :param d: Словарь с данными профиля из эндпоинта ``/profiles/me``.
    :type d: :obj:`dict`

    :return: Объект профиля текущего пользователя.
    :rtype: :class:`starvellapi.types.Profile`
    """
    u = d.get("user", {})
    user = parse_user(u)
    if user is None:
        raise ValueError("В ответе /profiles/me отсутствует поле user")
    return Profile(
        user=user,
        email=u.get("email", ""),
        balance=_to_rub(d.get("balance", {}).get("rubBalance", 0)),
        held=_to_rub(d.get("holdedAmount", 0)),
        purchase_orders=d.get("orderCountsByType", {}).get("purchaseOrdersCount", 0),
        sales_orders=d.get("orderCountsByType", {}).get("salesOrdersCount", 0),
        unread_chat_ids=d.get("unreadChatIds", []),
        unread_ticket_ids=d.get("unreadTicketIds", []),
        description=u.get("description", ""),
        banner=u.get("banner"),
        is_selling_enabled=u.get("isSellingEnabled", False),
        is_phone_linked=u.get("isPhoneLinked", False),
        is_telegram_linked=u.get("isTelegramLinked", False),
        has_password=u.get("hasPassword", False),
    )


def parse_sub_category(d: dict) -> Optional[SubCategory]:
    """
    Разбирает словарь в объект :class:`starvellapi.types.SubCategory`.

    :param d: Словарь с данными подкатегории из API.
    :type d: :obj:`dict`

    :return: Объект подкатегории или :obj:`None`, если словарь пуст.
    :rtype: :class:`starvellapi.types.SubCategory` or :obj:`None`
    """
    if not d:
        return None
    return SubCategory(
        id=d["id"],
        name=d.get("name", ""),
        filters=d.get("filters", []),
    )


def parse_offer(d: dict) -> Offer:
    """
    Разбирает словарь в объект :class:`starvellapi.types.Offer`.

    :param d: Словарь с данными оффера из API.
    :type d: :obj:`dict`

    :return: Объект оффера.
    :rtype: :class:`starvellapi.types.Offer`
    """
    u = d.get("user", {})
    sc = d.get("subCategory") or {}
    raw_type = d.get("type", "LOT")
    offer_type = OfferType.__members__.get(raw_type, OfferType.LOT)

    game_id = d.get("gameId")
    category_id = d.get("categoryId")
    if game_id is None and isinstance(sc, dict):
        game_id = sc.get("gameId") or (sc.get("game") or {}).get("id")
    if category_id is None and isinstance(sc, dict):
        category_id = sc.get("categoryId") or (sc.get("category") or {}).get("id")

    return Offer(
        id=d["id"],
        type=offer_type,
        price=d["price"],
        availability=d.get("availability", 0),
        user=parse_user(u),
        sub_category=parse_sub_category(sc) if sc else None,
        attributes=d.get("attributes", []),
        availability_unit=d.get("availabilityUnit", "UNITS"),
        descriptions=d.get("descriptions", {}),
        instant_delivery=d.get("instantDelivery", False),
        auto_delivery=d.get("autoDelivery", False),
        min_order_currency_amount=d.get("minOrderCurrencyAmount"),
        badges=d.get("badges", []),
        completion_rate=d.get("completionRate"),
        game_id=game_id,
        category_id=category_id,
        is_active=d.get("isActive", True),
    )


def parse_order(d: dict) -> Order:
    """
    Разбирает словарь в объект :class:`starvellapi.types.Order`.

    :param d: Словарь с данными заказа из API.
    :type d: :obj:`dict`

    :return: Объект заказа.
    :rtype: :class:`starvellapi.types.Order`
    """
    od = d.get("offerDetails")
    bu = d.get("user")
    raw_status = d.get("status", "")
    status = OrderStatus.__members__.get(raw_status, OrderStatus.PENDING)
    return Order(
        id=d["id"],
        status=status,
        quantity=d.get("quantity", 1),
        base_price=_to_rub(d.get("basePrice", 0)),
        total_price=_to_rub(d.get("totalPrice", 0)),
        seller_id=d["sellerId"],
        buyer_id=d["buyerId"],
        created_at=d["createdAt"],
        offer_details=OrderDetails(
            game=od["game"],
            category=od["category"],
            sub_category=od["subCategory"],
        ) if od else None,
        order_args=d.get("orderArgs", []),
        buyer=parse_user(bu) if bu else None,
    )


def parse_message(d: dict) -> ChatMessage:
    """
    Разбирает словарь в объект :class:`starvellapi.types.ChatMessage`.

    :param d: Словарь с данными сообщения из API.
    :type d: :obj:`dict`

    :return: Объект сообщения.
    :rtype: :class:`starvellapi.types.ChatMessage`
    """
    raw_type = d.get("type", "DEFAULT")
    msg_type = MessageType.__members__.get(raw_type, MessageType.DEFAULT)
    return ChatMessage(
        id=d["id"],
        content=d.get("content", ""),
        type=msg_type,
        author_id=d.get("authorId", 0),
        chat_id=d.get("chatId", ""),
        created_at=d.get("createdAt", ""),
        author=d.get("author"),
        metadata=d.get("metadata"),
        is_hidden=d.get("isHidden", False),
        images=d.get("images", []),
    )


def parse_chat(d: dict) -> Chat:
    """
    Разбирает словарь в объект :class:`starvellapi.types.Chat`.

    :param d: Словарь с данными чата из API.
    :type d: :obj:`dict`

    :return: Объект чата.
    :rtype: :class:`starvellapi.types.Chat`
    """
    participants = [
        parse_user(p) for p in d.get("participants", []) if p
    ]
    lm = d.get("lastMessage")
    return Chat(
        id=d["id"],
        participants=participants,
        unread_count=d.get("unreadMessageCount", 0),
        last_message=parse_message({**lm, "chatId": d["id"]}) if lm else None,
    )


def parse_review(d: dict) -> Review:
    """
    Разбирает словарь в объект :class:`starvellapi.types.Review`.

    :param d: Словарь с данными отзыва из API.
    :type d: :obj:`dict`

    :return: Объект отзыва.
    :rtype: :class:`starvellapi.types.Review`
    """
    author = d.get("author", {})
    order = d.get("order", {})
    od = order.get("offerDetails", {})
    game = od.get("game", {})
    rr = d.get("reviewResponse")
    return Review(
        id=d["id"],
        content=d.get("content", ""),
        recipient_id=d.get("recipientId", 0),
        author_id=d.get("authorId", 0),
        rating=d.get("rating", 0),
        created_at=d.get("createdAt", ""),
        author_username=author.get("username", ""),
        author_avatar=author.get("avatar"),
        order_id=d.get("orderId"),
        game_name=game.get("name", ""),
        amount=order.get("amount", 0),
        is_hidden=d.get("isHidden", False),
        response=ReviewResponse(
            id=rr["id"],
            content=rr.get("content", ""),
        ) if rr else None,
    )


def parse_ticket_reply(d: dict) -> TicketReply:
    """
    Разбирает словарь в объект :class:`starvellapi.types.TicketReply`.

    :param d: Словарь с данными ответа тикета из API.
    :type d: :obj:`dict`

    :return: Объект ответа тикета.
    :rtype: :class:`starvellapi.types.TicketReply`
    """
    return TicketReply(
        id=d["id"],
        ticket_id=d.get("ticketId", d.get("ticket_id", 0)),
        body=d.get("body", ""),
        body_text=d.get("bodyText", d.get("body_text", "")),
        created_at=d.get("createdAt", d.get("created_at", "")),
        incoming=d.get("incoming", True),
        attachments=d.get("attachments", []),
    )


def _to_rub(kopecks: int | float) -> float:
    """
    Конвертирует копейки в рубли.

    :param kopecks: Сумма в копейках.
    :type kopecks: :obj:`int` or :obj:`float`

    :return: Сумма в рублях.
    :rtype: :obj:`float`
    """
    return kopecks / 100
