import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoDataUpdater:
    """Класс для обновления крипто-данных в реальном времени"""
    
    def __init__(self, update_interval: int = 60):
        self.cache = {}
        self.last_update = None
        self.update_interval = update_interval
        self.update_task = None
        self._running = False
        
        # Список криптовалют для отслеживания
        self.symbols = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT", 
            "SOL": "SOLUSDT",
            "BNB": "BNBUSDT",
            "XRP": "XRPUSDT"
        }
    
    async def fetch_binance(self, session, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """Получение цены с Binance"""
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            async with session.get(url, timeout=5) as response:
                data = await response.json()
                return {
                    "price": float(data['price']),
                    "source": "Binance",
                    "symbol": symbol
                }
        except Exception as e:
            logger.error(f"Binance error for {symbol}: {e}")
            return None
    
    async def fetch_coingecko(self, session) -> Optional[Dict]:
        """Получение цен с CoinGecko для нескольких монет"""
        try:
            # Запрашиваем все нужные монеты одним запросом
            coins = ",".join(self.symbols.keys())
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coins}&vs_currencies=usd"
            async with session.get(url, timeout=5) as response:
                data = await response.json()
                result = {}
                for coin_id in self.symbols.keys():
                    if coin_id.lower() in data:
                        result[coin_id] = {
                            "price": data[coin_id.lower()]['usd'],
                            "source": "CoinGecko"
                        }
                return result if result else None
        except Exception as e:
            logger.error(f"CoinGecko error: {e}")
            return None
    
    async def fetch_bybit(self, session, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """Получение цены с Bybit"""
        try:
            url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}"
            async with session.get(url, timeout=5) as response:
                data = await response.json()
                if data['retCode'] == 0:
                    return {
                        "price": float(data['result']['list'][0]['lastPrice']),
                        "source": "Bybit",
                        "symbol": symbol
                    }
        except Exception as e:
            logger.error(f"Bybit error for {symbol}: {e}")
            return None
    
    async def update_all_crypto(self):
        """Обновление всех криптовалют"""
        prices = {}
        
        async with aiohttp.ClientSession() as session:
            # Получаем цены из разных источников для каждой монеты
            for coin_name, symbol in self.symbols.items():
                binance_price = await self.fetch_binance(session, symbol)
                bybit_price = await self.fetch_bybit(session, symbol)
                
                # Собираем все доступные цены для монеты
                available_prices = []
                
                if binance_price:
                    available_prices.append(binance_price['price'])
                if bybit_price:
                    available_prices.append(bybit_price['price'])
                
                # Также пробуем CoinGecko для всех монет разом
                coingecko_prices = await self.fetch_coingecko(session)
                if coingecko_prices and coin_name in coingecko_prices:
                    available_prices.append(coingecko_prices[coin_name]['price'])
                
                # Вычисляем среднюю цену
                if available_prices:
                    avg_price = sum(available_prices) / len(available_prices)
                    prices[coin_name] = round(avg_price, 2)
                else:
                    prices[coin_name] = None
                    logger.warning(f"No price available for {coin_name}")
        
        if any(prices.values()):
            now = datetime.now()
            self.cache = {
                "crypto": prices,
                "last_update": now.isoformat(),
                "date": now.strftime("%d.%m.%Y"),
                "time": now.strftime("%H:%M:%S"),
                "timestamp": now.timestamp()
            }
            self.last_update = now
            
            # Логируем успешное обновление
            available_coins = {k: v for k, v in prices.items() if v}
            logger.info(f"✅ Crypto updated: {available_coins}")
            return self.cache
        
        logger.error("❌ Failed to get any crypto data")
        return None
    
    async def start_background_updater(self):
        """Запуск фонового обновления"""
        self._running = True
        logger.info(f"🚀 Starting background crypto updater (every {self.update_interval}s)")
        
        # Первое обновление сразу
        await self.update_all_crypto()
        
        # Цикл обновлений
        while self._running:
            await asyncio.sleep(self.update_interval)
            await self.update_all_crypto()
    
    def stop_updater(self):
        """Остановка обновлений"""
        self._running = False
        logger.info("🛑 Stopped background updater")
    
    def get_current_data(self) -> Dict:
        """Получение текущих данных из кэша"""
        if not self.cache:
            return {
                "available": False,
                "error": "No data available yet"
            }
        
        age_seconds = 0
        if self.last_update:
            age_seconds = (datetime.now() - self.last_update).total_seconds()
        
        return {
            "available": True,
            "crypto": self.cache.get("crypto", {}),
            "date": self.cache.get("date", ""),
            "time": self.cache.get("time", ""),
            "age_seconds": int(age_seconds),
            "is_fresh": age_seconds < 120
        }

# Глобальный экземпляр
crypto_updater = CryptoDataUpdater(update_interval=60)