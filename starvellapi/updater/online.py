from __future__ import annotations
import asyncio
import json
import logging
from typing import Optional
import websockets
from websockets.exceptions import ConnectionClosed, ConnectionClosedError, ConnectionClosedOK
from ..account import Account
log = logging.getLogger('starvellapi.online')
_WS_URL = 'wss://starvell.com/socket.io/?EIO=4&transport=websocket'
_DEFAULT_PING_INTERVAL_MS = 25000
_DEFAULT_PING_TIMEOUT_MS = 20000

class OnlineKeeper:

    def __init__(self, account: Account, reconnect_delay: float=5.0) -> None:
        self._account: Account = account
        self._reconnect_delay: float = reconnect_delay
        self._task: Optional[asyncio.Task] = None
        self._running: bool = False

    async def __aenter__(self) -> 'OnlineKeeper':
        await self.start()
        return self

    async def __aexit__(self, *exc) -> None:
        await self.stop()

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run())
        log.info('OnlineKeeper запущен')

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        log.info('OnlineKeeper остановлен')

    @property
    def is_running(self) -> bool:
        return self._running and self._task is not None and (not self._task.done())

    async def _run(self) -> None:
        while self._running:
            try:
                await self._connect_and_listen()
            except asyncio.CancelledError:
                break
            except (ConnectionClosedOK, ConnectionClosedError, ConnectionClosed) as e:
                log.debug('OnlineKeeper: соединение закрыто (%s). Переподключение через %.1fs', e, self._reconnect_delay)
            except Exception as e:
                log.warning('OnlineKeeper: ошибка %s. Переподключение через %.1fs', e, self._reconnect_delay)
            if not self._running:
                break
            try:
                await asyncio.sleep(self._reconnect_delay)
            except asyncio.CancelledError:
                break

    async def _connect_and_listen(self) -> None:
        connect = await self._account.connect_websocket(_WS_URL)
        async with connect as ws:
            ping_interval_ms, ping_timeout_ms = await self._read_open(ws)
            await ws.send('40/online,')
            log.debug('OnlineKeeper подключён, статус онлайн активен')
            read_timeout = (ping_interval_ms + ping_timeout_ms) / 1000.0
            while self._running:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=read_timeout)
                except asyncio.TimeoutError:
                    log.debug('OnlineKeeper: таймаут чтения, переподключаемся')
                    return
                if not isinstance(raw, str):
                    continue
                if raw == '2':
                    await ws.send('3')
                    continue

    async def _read_open(self, ws) -> tuple[int, int]:
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=10.0)
        except asyncio.TimeoutError:
            return (_DEFAULT_PING_INTERVAL_MS, _DEFAULT_PING_TIMEOUT_MS)
        if not isinstance(raw, str) or not raw.startswith('0'):
            return (_DEFAULT_PING_INTERVAL_MS, _DEFAULT_PING_TIMEOUT_MS)
        try:
            payload = json.loads(raw[1:])
        except (ValueError, json.JSONDecodeError):
            return (_DEFAULT_PING_INTERVAL_MS, _DEFAULT_PING_TIMEOUT_MS)
        return (int(payload.get('pingInterval', _DEFAULT_PING_INTERVAL_MS)), int(payload.get('pingTimeout', _DEFAULT_PING_TIMEOUT_MS)))