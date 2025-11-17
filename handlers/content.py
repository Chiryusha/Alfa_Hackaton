from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.llm_service import LLMService
from utils.keyboards import (
    get_content_type_keyboard,
    get_platform_keyboard,
    get_main_keyboard,
    get_back_keyboard
)

router = Router()
llm_service = None  # Инициализируется при первом использовании


def get_llm_service():
    """Получает или создает экземпляр LLMService"""
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service


class ContentGeneration(StatesGroup):
    """Состояния для генерации контента"""
    waiting_for_type = State()
    waiting_for_params = State()
    waiting_for_platform = State()
    waiting_for_post_params = State()
    waiting_for_offer_params = State()
    waiting_for_product_params = State()


@router.message(Command("post"))
@router.message(F.text == "📱 Пост для соцсетей")
async def cmd_post(message: Message, state: FSMContext):
    """Начало создания поста для соцсетей"""
    await state.set_state(ContentGeneration.waiting_for_platform)
    await message.answer(
        "🎯 <b>Создание поста для социальных сетей</b>\n\n"
        "Выберите платформу:",
        reply_markup=get_platform_keyboard()
    )


@router.callback_query(F.data.startswith("platform_"))
async def process_platform(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора платформы"""
    platform = callback.data.replace("platform_", "")
    platform_names = {
        "instagram": "Instagram",
        "vk": "ВКонтакте",
        "telegram": "Telegram",
        "facebook": "Facebook",
        "ok": "Одноклассники"
    }
    platform_name = platform_names.get(platform, platform)
    
    await state.update_data(platform=platform, content_type="post")
    await state.set_state(ContentGeneration.waiting_for_post_params)
    
    await callback.message.edit_text(
        f"📱 <b>Создание поста для {platform_name}</b>\n\n"
        "Опишите, о чем должен быть пост:\n"
        "• Тема/повод\n"
        "• Ключевые моменты\n"
        "• Целевая аудитория\n"
        "• Желаемый тон (формальный/неформальный)\n\n"
        "💡 <b>Пример:</b> Анонс новой коллекции одежды для молодежи, "
        "неформальный тон, акцент на стиль и доступность",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()


@router.message(ContentGeneration.waiting_for_post_params)
async def generate_post(message: Message, state: FSMContext):
    """Генерация поста на основе параметров"""
    data = await state.get_data()
    platform = data.get("platform", "социальных сетей")
    
    await message.answer("⏳ Генерирую пост... Это займет несколько секунд.")
    
    prompt = (
        f"Создай пост для {platform} на основе следующего описания:\n\n"
        f"{message.text}\n\n"
        f"Требования:\n"
        f"- Адаптируй стиль под {platform}\n"
        f"- Используй эмодзи уместно\n"
        f"- Сделай текст привлекательным и вовлекающим\n"
        f"- Добавь призыв к действию\n"
        f"- Длина: 1-2 абзаца для {platform}"
    )
    
    try:
        generated_text = await get_llm_service().generate_text(prompt)
        await message.answer(
            f"✅ <b>Готовый пост для {platform}:</b>\n\n"
            f"{generated_text}\n\n"
            "📋 Скопируйте текст выше",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка при генерации: {str(e)}\n"
            "Попробуйте еще раз или обратитесь в поддержку.",
            reply_markup=get_main_keyboard()
        )
    
    await state.clear()


@router.message(Command("offer"))
@router.message(F.text == "📝 Коммерческое предложение")
async def cmd_offer(message: Message, state: FSMContext):
    """Начало создания коммерческого предложения"""
    await state.set_state(ContentGeneration.waiting_for_offer_params)
    await message.answer(
        "📝 <b>Создание коммерческого предложения</b>\n\n"
        "Опишите детали вашего предложения:\n"
        "• Название компании/продукта\n"
        "• Что вы предлагаете\n"
        "• Преимущества для клиента\n"
        "• Целевая аудитория\n"
        "• Контактная информация (опционально)\n\n"
        "💡 <b>Пример:</b> IT-компания предлагает разработку сайтов для малого бизнеса, "
        "быстрые сроки, доступные цены, поддержка после запуска",
        reply_markup=get_back_keyboard()
    )


@router.message(ContentGeneration.waiting_for_offer_params)
async def generate_offer(message: Message, state: FSMContext):
    """Генерация коммерческого предложения"""
    await message.answer("⏳ Составляю коммерческое предложение...")
    
    prompt = (
        f"Создай профессиональное коммерческое предложение на основе следующего описания:\n\n"
        f"{message.text}\n\n"
        f"Структура КП:\n"
        f"1. Приветствие и представление\n"
        f"2. Описание проблемы клиента\n"
        f"3. Предложение решения\n"
        f"4. Преимущества и выгоды\n"
        f"5. Призыв к действию\n"
        f"6. Контакты\n\n"
        f"Стиль: профессиональный, убедительный, но не навязчивый"
    )
    
    try:
        generated_text = await get_llm_service().generate_text(prompt)
        await message.answer(
            f"✅ <b>Готовое коммерческое предложение:</b>\n\n"
            f"{generated_text}\n\n"
            "📋 Скопируйте текст выше",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка: {str(e)}",
            reply_markup=get_main_keyboard()
        )
    
    await state.clear()


@router.message(Command("product"))
@router.message(F.text == "🛍️ Описание товара/услуги")
async def cmd_product(message: Message, state: FSMContext):
    """Начало создания описания товара/услуги"""
    await state.set_state(ContentGeneration.waiting_for_product_params)
    await message.answer(
        "🛍️ <b>Создание описания товара или услуги</b>\n\n"
        "Опишите ваш товар или услугу:\n"
        "• Название\n"
        "• Основные характеристики\n"
        "• Преимущества\n"
        "• Целевая аудитория\n"
        "• Уникальные особенности\n\n"
        "💡 <b>Пример:</b> Курс по маркетингу для начинающих предпринимателей, "
        "10 уроков, практические кейсы, поддержка в чате",
        reply_markup=get_back_keyboard()
    )


@router.message(ContentGeneration.waiting_for_product_params)
async def generate_product(message: Message, state: FSMContext):
    """Генерация описания товара/услуги"""
    await message.answer("⏳ Создаю описание...")
    
    prompt = (
        f"Создай привлекательное описание товара/услуги на основе следующего:\n\n"
        f"{message.text}\n\n"
        f"Требования:\n"
        f"- Заголовок, привлекающий внимание\n"
        f"- Структурированное описание с преимуществами\n"
        f"- Использование маркированных списков\n"
        f"- Призыв к действию\n"
        f"- SEO-оптимизация (если применимо)\n"
        f"- Длина: 150-300 слов"
    )
    
    try:
        generated_text = await get_llm_service().generate_text(prompt)
        await message.answer(
            f"✅ <b>Готовое описание:</b>\n\n"
            f"{generated_text}\n\n"
            "📋 Скопируйте текст выше",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка: {str(e)}",
            reply_markup=get_main_keyboard()
        )
    
    await state.clear()


@router.callback_query(F.data == "back")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    try:
        # Пытаемся отредактировать сообщение с inline-кнопками
        await callback.message.edit_text(
            "👋 <b>Главное меню</b>\n\nВыберите, что вам нужно:",
            reply_markup=None
        )
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=get_main_keyboard()
        )
    except Exception:
        # Если не удалось отредактировать, отправляем новое сообщение
        await callback.message.answer(
            "👋 <b>Главное меню</b>\n\nВыберите, что вам нужно:",
            reply_markup=get_main_keyboard()
        )
    await callback.answer()

