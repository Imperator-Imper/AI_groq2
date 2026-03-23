import aiohttp
import asyncio
import base64
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageGenerator:
    """Класс для генерации изображений через AI"""
    
    def __init__(self, api_key: str = None):
        # Если нет своего API, используем бесплатные
        self.api_key = api_key
        self.fallback_mode = True  # Используем бесплатные API
    
    async def generate_image_free(self, prompt: str) -> Optional[str]:
        """Генерация через бесплатный API (Pollinations.ai)"""
        try:
            # Pollinations.ai - бесплатный генератор изображений
            url = f"https://image.pollinations.ai/prompt/{prompt}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        # Сохраняем изображение
                        image_data = await response.read()
                        return image_data
        except Exception as e:
            logger.error(f"Free image generation error: {e}")
            return None
    
    async def generate_image(self, prompt: str) -> Optional[bytes]:
        """Генерация изображения по промпту"""
        # Сначала пробуем бесплатный вариант
        result = await self.generate_image_free(prompt)
        if result:
            return result
        
        return None

# Глобальный экземпляр
image_gen = ImageGenerator()