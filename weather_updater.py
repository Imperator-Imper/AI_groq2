import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherUpdater:
    """Класс для получения актуальной погоды"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.cache = {}  # город -> {данные, время_кэша}
        self.cache_ttl = 600  # 10 минут кэш
    
    async def get_weather(self, city: str = "Kyiv") -> Dict:
        """Получить погоду для города (с кэшированием)"""
        
        # Проверяем кэш
        city_lower = city.lower()
        now = datetime.now()
        
        if city_lower in self.cache:
            cached = self.cache[city_lower]
            if (now - cached["timestamp"]).seconds < self.cache_ttl:
                logger.info(f"Using cached weather for {city}")
                return cached["data"]
        
        # Запрашиваем новую погоду
        async with aiohttp.ClientSession() as session:
            try:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric&lang=ru"
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        weather_info = {
                            "city": data["name"],
                            "temperature": round(data["main"]["temp"]),
                            "feels_like": round(data["main"]["feels_like"]),
                            "description": data["weather"][0]["description"].capitalize(),
                            "humidity": data["main"]["humidity"],
                            "wind_speed": data["wind"]["speed"],
                            "icon": data["weather"][0]["icon"]
                        }
                        
                        # Сохраняем в кэш
                        self.cache[city_lower] = {
                            "data": weather_info,
                            "timestamp": now
                        }
                        
                        logger.info(f"Weather updated for {city}: {weather_info['temperature']}°C")
                        return weather_info
                    else:
                        return {"error": f"Город {city} не найден"}
            except Exception as e:
                logger.error(f"Weather error: {e}")
                return {"error": "Сервис погоды временно недоступен"}

# Глобальный экземпляр (инициализация в bot.py)
weather_updater = None