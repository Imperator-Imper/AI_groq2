import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsUpdater:
    """Класс для получения актуальных новостей"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def get_news(self, query: str = "technology", max_articles: int = 5) -> List[Dict]:
        """Получить свежие новости по теме"""
        
        async with aiohttp.ClientSession() as session:
            try:
                # Ищем новости за последние 24 часа
                from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                
                url = f"https://newsapi.org/v2/everything?q={query}&from={from_date}&sortBy=publishedAt&language=ru&apiKey={self.api_key}&pageSize={max_articles}"
                
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data["status"] == "ok" and data["totalResults"] > 0:
                            articles = []
                            for article in data["articles"][:max_articles]:
                                articles.append({
                                    "title": article["title"],
                                    "description": article["description"][:200] if article["description"] else "",
                                    "source": article["source"]["name"],
                                    "url": article["url"],
                                    "published_at": article["publishedAt"][:10]
                                })
                            logger.info(f"Found {len(articles)} news for '{query}'")
                            return articles
                        else:
                            return []
                    else:
                        return []
            except Exception as e:
                logger.error(f"News API error: {e}")
                return []
    
    async def get_top_headlines(self, category: str = "general", max_articles: int = 5) -> List[Dict]:
        """Получить главные новости"""
        
        async with aiohttp.ClientSession() as session:
            try:
                url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={self.api_key}&pageSize={max_articles}"
                
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data["status"] == "ok" and data["totalResults"] > 0:
                            articles = []
                            for article in data["articles"][:max_articles]:
                                articles.append({
                                    "title": article["title"],
                                    "description": article["description"][:200] if article["description"] else "",
                                    "source": article["source"]["name"],
                                    "url": article["url"]
                                })
                            return articles
                    return []
            except Exception as e:
                logger.error(f"News API error: {e}")
                return []

# Глобальный экземпляр
news_updater = None