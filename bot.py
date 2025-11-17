import asyncio
import logging
import os
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Настройка логирования (нужно до загрузки env, чтобы логировать)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения ПЕРЕД импортом handlers
# Определяем путь к файлам относительно текущей директории скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')
env_example_path = os.path.join(script_dir, 'env.example')

# Логирование путей только для отладки (можно убрать после проверки)
# logger.info(f"Текущая рабочая директория: {os.getcwd()}")
# logger.info(f"Директория скрипта: {script_dir}")
# logger.info(f"Путь к .env: {env_path}")
# logger.info(f"Файл .env существует: {os.path.exists(env_path)}")

# Сначала пытаемся загрузить .env, если его нет - загружаем env.example
if os.path.exists(env_path):
    # Пробуем загрузить файл
    try:
        # Читаем файл вручную для отладки
        with open(env_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
            logger.info(f"Содержимое .env файла (первые 200 символов): {repr(file_content[:200])}")
            logger.info(f"Длина файла: {len(file_content)} символов")
            logger.info(f"Количество строк: {len(file_content.splitlines())}")
        
        # Загружаем через dotenv
        result = load_dotenv(env_path, override=True)
        logger.info(f"Результат load_dotenv: {result}")
        
        # Проверяем что загрузилось
        test_token = getenv("BOT_TOKEN")
        logger.info(f"BOT_TOKEN после загрузки: {'найден' if test_token else 'НЕ найден'}")
        if test_token:
            logger.info(f"Длина токена: {len(test_token)} символов, начало: {test_token[:20]}...")
        else:
            # Пробуем загрузить вручную
            logger.warning("Пробую загрузить переменные вручную...")
            for line in file_content.split('\n'):
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
                    logger.info(f"Установлена переменная: {key.strip()}")
            test_token = getenv("BOT_TOKEN")
            logger.info(f"BOT_TOKEN после ручной загрузки: {'найден' if test_token else 'НЕ найден'}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке .env: {e}")
        result = False
elif os.path.exists(env_example_path):
    load_dotenv(env_example_path)
    logger.info("Используется env.example (файл .env не найден)")
elif os.path.exists('.env'):
    load_dotenv('.env')
    logger.info("Загружен файл .env (относительный путь)")
else:
    load_dotenv()
    logger.warning("Файлы .env и env.example не найдены, используются системные переменные окружения")

# Импортируем handlers ПОСЛЕ загрузки переменных окружения
from handlers import start, content, consult

# Получаем токен бота
BOT_TOKEN = getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN не найден в переменных окружения!")
    logger.error("Создайте файл .env и добавьте туда ваш токен бота!")
    sys.exit(1)

# Проверяем, что токен не является плейсхолдером
if BOT_TOKEN in ["your_bot_token_here", "your_bot_token", ""]:
    logger.error("BOT_TOKEN содержит плейсхолдер, а не реальный токен!")
    logger.error("Создайте файл .env на основе env.example и замените 'your_bot_token_here' на ваш реальный токен!")
    logger.error("Получите токен у @BotFather в Telegram")
    sys.exit(1)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())


async def main():
    """Основная функция запуска бота"""
    # Регистрируем роутеры
    dp.include_router(start.router)
    dp.include_router(content.router)
    dp.include_router(consult.router)
    
    logger.info("Бот запущен и готов к работе!")
    
    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")

