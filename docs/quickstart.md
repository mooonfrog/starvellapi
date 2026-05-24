# Быстрый старт

## Получить session cookie

Залогинься на [starvell.com](https://starvell.com), открой DevTools, вкладку **Application → Cookies → starvell.com**. Скопируй значение cookie с именем `session`.

## Подключение

```python
import asyncio
from starvellapi import Account

async def main():
    async with Account(session_cookie="...") as acc:
        me = await acc.get_profile()
        print(me.user.username, "balance:", me.balance, "₽")

asyncio.run(main())
```

`Account` — это async context manager. Он сам поднимает HTTP-клиент, забирает профиль и кладёт `user_id` в `acc.user_id`. Закрывается автоматически.

## Прокси и user-agent

```python
async with Account(
    session_cookie="...",
    proxy="http://user:pass@host:8080",
    user_agent="Mozilla/5.0 ...",
) as acc:
    ...
```

## Базовые операции

### Чаты

```python
chats = await acc.get_chats(limit=20)
for chat in chats:
    print(chat.id, chat.unread_count, chat.last_message and chat.last_message.content)

messages = await acc.get_chat_messages(
    chat_id=chats[0].id,
    interlocutor_id=chats[0].participants[0].id,
    limit=50,
)

await acc.send_message(chats[0].id, "Привет!")
await acc.read_chat(chats[0].id)
```

### Офферы

```python
from starvellapi import OfferSortBy, SortDirection

offers = await acc.get_offers_by_category(
    category_id=42,
    limit=100,
    sort_by=OfferSortBy.PRICE,
    sort_dir=SortDirection.ASC,
)
mine = [o for o in offers if o.user.id == acc.user_id]
for offer in mine:
    await acc.update_offer(offer.id, price="99.99", availability=10)
```

### Заказы

```python
from starvellapi import OrderUserType

orders = await acc.get_orders(user_type=OrderUserType.SELLER, limit=20)
for order in orders:
    print(order.id, order.status, order.total_price)

await acc.mark_order_completed(orders[0].id)
```

### Отзывы

```python
reviews = await acc.get_reviews(recipient_id=acc.user_id, limit=10)
for review in reviews:
    print(review.rating, review.author_username, review.content)

await acc.create_review_response(reviews[0].id, "Спасибо!")
```

## Дальше

- [Слушаем события](guide/events.md)
- [Онлайн-статус](guide/online.md)
- [Полный API](api/account.md)
