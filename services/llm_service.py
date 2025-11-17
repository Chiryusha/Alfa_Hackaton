import os
from typing import Optional
import aiohttp



class LLMService:
    """Сервис для работы с LLM через различные провайдеры"""
    
    def __init__(self):
        # Определяем провайдера из переменных окружения (по умолчанию groq - бесплатный)
        self.provider = os.getenv("LLM_PROVIDER", "groq").lower()
        
        if self.provider == "groq":
            # Groq AI - БЕСПЛАТНЫЙ, быстрый, рекомендую!
            self.api_key = os.getenv("GROQ_API_KEY", "")
            self.base_url = "https://api.groq.com/openai/v1"
            self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        elif self.provider == "gemini":
            # Google Gemini - БЕСПЛАТНЫЙ через AI Studio
            self.api_key = os.getenv("GEMINI_API_KEY", "")
            self.base_url = "https://generativelanguage.googleapis.com/v1beta"
            self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        elif self.provider == "deepseek":
            self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
            self.base_url = "https://api.deepseek.com/v1"
            self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        elif self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY не найден в переменных окружения!")
            self.base_url = "https://api.openai.com/v1"
            self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        elif self.provider == "yandex":
            self.api_key = os.getenv("YANDEX_API_KEY")
            if not self.api_key:
                raise ValueError("YANDEX_API_KEY не найден в переменных окружения!")
            self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            self.model = os.getenv("YANDEX_MODEL", "yandexgpt")
        else:
            raise ValueError(f"Неподдерживаемый провайдер: {self.provider}. Доступны: groq, gemini, deepseek, openai, yandex")
        
        self.session = None
    
    async def _get_session(self):
        """Получает или создает aiohttp сессию"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _close_session(self):
        """Закрывает aiohttp сессию"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """
        Генерирует текст на основе промпта
        
        Args:
            prompt: Текст промпта
            max_tokens: Максимальное количество токенов в ответе
            temperature: Температура генерации (0.0-1.0)
        
        Returns:
            Сгенерированный текст
        """
        system_message = (
            "Ты - профессиональный помощник для владельцев малого бизнеса. "
            "Твоя задача - создавать качественный коммерческий контент и "
            "давать практические советы. Будь конкретным, полезным и дружелюбным. "
            "Отвечай на русском языке."
        )
        
        if self.provider == "groq":
            return await self._generate_groq(system_message, prompt, max_tokens, temperature)
        elif self.provider == "gemini":
            return await self._generate_gemini(system_message, prompt, max_tokens, temperature)
        elif self.provider == "deepseek":
            return await self._generate_deepseek(system_message, prompt, max_tokens, temperature)
        elif self.provider == "openai":
            return await self._generate_openai(system_message, prompt, max_tokens, temperature)
        elif self.provider == "yandex":
            return await self._generate_yandex(system_message, prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Неподдерживаемый провайдер: {self.provider}")
    
    async def _generate_groq(
        self,
        system_message: str,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Генерация через Groq AI API (БЕСПЛАТНЫЙ!)"""
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY не найден! Получите бесплатный ключ на "
                "https://console.groq.com/ и добавьте его в .env файл"
            )
        
        session = await self._get_session()
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Groq API ошибка {response.status}: {error_text}")
                
                data = await response.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise Exception(f"Ошибка при генерации текста через Groq: {str(e)}")
    
    async def _generate_gemini(
        self,
        system_message: str,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Генерация через Google Gemini API (БЕСПЛАТНЫЙ!)"""
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY не найден! Получите бесплатный ключ на "
                "https://aistudio.google.com/app/apikey и добавьте его в .env файл"
            )
        
        session = await self._get_session()
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Gemini использует другую структуру запроса
        full_prompt = f"{system_message}\n\n{prompt}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Gemini API ошибка {response.status}: {error_text}")
                
                data = await response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            raise Exception(f"Ошибка при генерации текста через Gemini: {str(e)}")
    
    async def _generate_deepseek(
        self,
        system_message: str,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Генерация через DeepSeek API"""
        if not self.api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY не найден! Получите бесплатный ключ на "
                "https://platform.deepseek.com/ и добавьте его в .env файл"
            )
        
        session = await self._get_session()
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"DeepSeek API ошибка {response.status}: {error_text}")
                
                data = await response.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise Exception(f"Ошибка при генерации текста через DeepSeek: {str(e)}")
    
    async def _generate_openai(
        self,
        system_message: str,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Генерация через OpenAI API"""
        session = await self._get_session()
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API ошибка {response.status}: {error_text}")
                
                data = await response.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise Exception(f"Ошибка при генерации текста через OpenAI: {str(e)}")
    
    async def _generate_yandex(
        self,
        system_message: str,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Генерация через YandexGPT API"""
        session = await self._get_session()
        url = self.base_url
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.api_key}"
        }
        
        full_prompt = f"{system_message}\n\n{prompt}"
        
        payload = {
            "modelUri": f"gpt://{self.model}/yandexgpt/latest",
            "completionOptions": {
                "stream": False,
                "temperature": temperature,
                "maxTokens": str(max_tokens)
            },
            "messages": [
                {
                    "role": "system",
                    "text": system_message
                },
                {
                    "role": "user",
                    "text": prompt
                }
            ]
        }
        
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"YandexGPT API ошибка {response.status}: {error_text}")
                
                data = await response.json()
                return data["result"]["alternatives"][0]["message"]["text"].strip()
        except Exception as e:
            raise Exception(f"Ошибка при генерации текста через YandexGPT: {str(e)}")
    
    async def generate_with_context(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: int = 1000
    ) -> str:
        """
        Генерирует текст с дополнительным контекстом
        
        Args:
            prompt: Основной промпт
            context: Дополнительный контекст
            max_tokens: Максимальное количество токенов
        
        Returns:
            Сгенерированный текст
        """
        full_prompt = prompt
        if context:
            full_prompt = f"Контекст: {context}\n\n{prompt}"
        
        return await self.generate_text(full_prompt, max_tokens)

