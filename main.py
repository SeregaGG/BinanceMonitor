import time
import websockets
import asyncio
import json
from asyncio.events import AbstractEventLoop
from queue import Queue

# all_info = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
# kline_info = 'https://fapi.binance.com/fapi/v1/klines?symbol=btcusdt&interval=1h&startTime=1676190523114'
# wss_url = 'wss://fstream.binance.com/stream?streams=xrpusdt@aggTrade/bnbusdt@aggTrade'
# symbol: str = 'xrpusdt'
# interval: str = '1h'
# start_time: int = round(time.time() * 1000) - 3_600_000
#
# current_kline = json.loads(requests.get(f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&startTime={start_time}').content)


class PriceQueue(Queue):
    def __init__(self, interval: int = 3_600_000):
        self.interval = interval
        super().__init__()

    def put(self, item: tuple[int, float], block: bool = ..., timeout: float | None = ...) -> None:
        if len(self.queue) and item[1] - self.queue[0][0] >= self.interval:
            super().put(item)
            super().get()
        else:
            super().put(item)

    def get_max_price(self):
        return max([item[1] for item in self.queue])


async def main():
    symbol = 'xrpusdt'
    wss_url: str = f'wss://fstream.binance.com/stream?streams={symbol}@aggTrade'
    async with websockets.connect(wss_url) as ws:
        prices = PriceQueue()
        while True:
            current_price: float = float(json.loads(await ws.recv())['data']['p'])
            prices.put((round(time.time() * 1000), current_price))
            max_price = prices.get_max_price()

            if ((max_price / current_price) - 1) * 100 >= 1:
                print('Alert')
                prices.queue.clear()


if __name__ == '__main__':
    loop: AbstractEventLoop = asyncio.get_event_loop()
    loop.run_until_complete(main())
