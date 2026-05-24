# OnlineKeeper

::: starvellapi.OnlineKeeper
    options:
      show_bases: true
      members_order: source

## Как работает

`OnlineKeeper` подключается к `wss://starvell.com/socket.io/` через socket.io v4 EIO=4 transport, шлёт `40/online,` в namespace и отвечает `3` на каждый ping `2`. При обрыве переподключается с задержкой `reconnect_delay` секунд.

## Использование как context manager

```python
async with Account(session_cookie="...") as acc:
    async with OnlineKeeper(acc):
        await asyncio.sleep(3600)
```
