import aiohttp
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_async_session
from config import get_settings
import json

class OpenRouterClient:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://openrouter.ai/api/v1"
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def check_daily_limit(self, user_id: int, db: AsyncSession) -> tuple[bool, int]:
        """Проверяет дневной лимит AI-запросов пользователя"""
        from models.user import User
        
        user = await db.get(User, user_id)
        if not user:
            return False, 0
        
        today = date.today()
        if user.last_ai_request_date != today:
            user.daily_ai_requests = 0
            user.last_ai_request_date = today
        
        daily_limit = 5  # Бесплатный лимит
        requests_used = user.daily_ai_requests
        
        return requests_used < daily_limit, daily_limit - requests_used

    async def increment_usage(self, user_id: int, db: AsyncSession):
        """Увеличивает счетчик использованных AI-запросов"""
        from models.user import User
        
        user = await db.get(User, user_id)
        if user:
            user.daily_ai_requests += 1
            user.total_ai_requests += 1
            await db.commit()

    async def chat_completion(
        self, 
        messages: list[dict], 
        user_id: int,
        db: AsyncSession,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Отправляет запрос к OpenRouter API"""
        
        # Проверяем лимит
        can_request, remaining = await self.check_daily_limit(user_id, db)
        
        if not can_request:
            return {
                "error": "limit_exceeded",
                "message": f"Вы исчерпали бесплатный лимит ({remaining} запросов осталось на сегодня)",
                "remaining": remaining
            }

        headers = {
            "Authorization": f"Bearer {self.settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yourusername/milana-ai",
            "X-Title": "Milana AI Bot"
        }

        payload = {
            "model": model or self.settings.OPENROUTER_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1000
        }

        try:
            session = await self._get_session()
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    # Увеличиваем счетчик использования
                    await self.increment_usage(user_id, db)
                    return result
                else:
                    error_text = await response.text()
                    return {
                        "error": "api_error",
                        "message": f"OpenRouter API error: {response.status}",
                        "details": error_text
                    }
                    
        except asyncio.TimeoutError:
            return {
                "error": "timeout",
                "message": "Запрос превысил время ожидания. Попробуйте позже."
            }
        except Exception as e:
            return {
                "error": "unknown_error",
                "message": f"Неизвестная ошибка: {str(e)}"
            }

    async def generate_horoscope(self, zodiac_sign: str, user_id: int, db: AsyncSession) -> str:
        """Генерирует гороскоп для знака зодиака"""
        
        prompt = f"""Напиши смешной, но мотивирующий гороскоп для знака {zodiac_sign} на сегодня. 
        Гороскоп должен быть коротким (2-3 предложения), позитивным и немного юмористическим.
        Используй эмодзи для настроения."""
        
        messages = [
            {"role": "system", "content": "Ты астролог с отличным чувством юмора."},
            {"role": "user", "content": prompt}
        ]
        
        result = await self.chat_completion(messages, user_id, db)
        
        if "error" in result:
            return f"⚠️ {result['message']}"
        
        try:
            content = result["choices"][0]["message"]["content"]
            return content.strip()
        except (KeyError, IndexError):
            return "⚠️ Не удалось сгенерировать гороскоп. Попробуйте позже."

    async def summarize_news(self, news_text: str, user_id: int, db: AsyncSession) -> str:
        """Создает краткую выжимку из новостей"""
        
        prompt = f"""Сделай краткую выжимку из этих новостей (2-3 основных пункта):
        
        {news_text}
        
        Выдели только самую важную информацию."""
        
        messages = [
            {"role": "system", "content": "Ты новостной аналитик, который умеет выделять главное."},
            {"role": "user", "content": prompt}
        ]
        
        result = await self.chat_completion(messages, user_id, db)
        
        if "error" in result:
            return f"⚠️ {result['message']}"
        
        try:
            content = result["choices"][0]["message"]["content"]
            return content.strip()
        except (KeyError, IndexError):
            return "⚠️ Не удалось обработать новости. Попробуйте позже."

# Глобальный экземпляр клиента
llm_client = OpenRouterClient()