from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.llm_service import LLMService
from utils.keyboards import (
    get_consultation_keyboard,
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


class Consultation(StatesGroup):
    """Состояния для консультаций"""
    waiting_for_type = State()
    waiting_for_question = State()


@router.message(Command("consult"))
@router.message(F.text == "💼 Консультация")
async def cmd_consult(message: Message, state: FSMContext):
    """Начало консультации"""
    await state.set_state(Consultation.waiting_for_type)
    await message.answer(
        "💼 <b>Консультация по вопросам бизнеса</b>\n\n"
        "Выберите тип консультации:",
        reply_markup=get_consultation_keyboard()
    )


@router.callback_query(F.data.startswith("consult_"))
async def process_consult_type(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа консультации"""
    consult_type = callback.data.replace("consult_", "")
    type_names = {
        "legal": "Юридические вопросы",
        "marketing": "Маркетинг",
        "finance": "Финансы",
        "other": "Другие вопросы"
    }
    type_name = type_names.get(consult_type, "Общие вопросы")
    
    await state.update_data(consult_type=consult_type)
    await state.set_state(Consultation.waiting_for_question)
    
    examples = {
        "legal": "Например: какие документы нужны для регистрации ИП?",
        "marketing": "Например: как продвигать бизнес в Instagram?",
        "finance": "Например: как вести учет доходов и расходов?",
        "other": "Например: как выбрать нишу для бизнеса?"
    }
    
    await callback.message.edit_text(
        f"💼 <b>{type_name}</b>\n\n"
        f"Опишите ваш вопрос подробно:\n"
        f"{examples.get(consult_type, '')}\n\n"
        f"Чем больше деталей вы укажете, тем точнее будет ответ.",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()


@router.message(Consultation.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    """Обработка вопроса и генерация ответа"""
    data = await state.get_data()
    consult_type = data.get("consult_type", "other")
    
    type_contexts = {
        "legal": "юридическим вопросам для малого бизнеса в России",
        "marketing": "маркетингу и продвижению малого бизнеса",
        "finance": "финансовым вопросам и учету для малого бизнеса",
        "other": "общим вопросам ведения малого бизнеса"
    }
    
    context = type_contexts.get(consult_type, "общим вопросам бизнеса")
    
    await message.answer("⏳ Анализирую ваш вопрос и готовлю ответ...")
    
    prompt = (
        f"Ты - эксперт по {context}. "
        f"Ответь на вопрос владельца малого бизнеса:\n\n"
        f"{message.text}\n\n"
        f"Требования к ответу:\n"
        f"- Будь конкретным и практичным\n"
        f"- Приведи примеры, если возможно\n"
        f"- Структурируй ответ (используй списки, если уместно)\n"
        f"- Укажи на важные нюансы и подводные камни\n"
        f"- Если вопрос требует юридической консультации, укажи, что лучше обратиться к юристу\n"
        f"- Длина: 200-400 слов"
    )
    
    try:
        answer = await get_llm_service().generate_text(prompt)
        await message.answer(
            f"💡 <b>Ответ на ваш вопрос:</b>\n\n"
            f"{answer}\n\n"
            f"⚠️ <i>Важно: Это общие рекомендации. "
            f"Для сложных вопросов рекомендуется консультация со специалистом.</i>",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка: {str(e)}\n"
            f"Попробуйте переформулировать вопрос или обратитесь в поддержку.",
            reply_markup=get_main_keyboard()
        )
    
    await state.clear()


@router.callback_query(F.data == "back")
async def back_to_main_consult(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню из консультаций"""
    await state.clear()
    try:
        await callback.message.edit_text(
            "👋 <b>Главное меню</b>\n\nВыберите, что вам нужно:",
            reply_markup=None
        )
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=get_main_keyboard()
        )
    except Exception:
        await callback.message.answer(
            "👋 <b>Главное меню</b>\n\nВыберите, что вам нужно:",
            reply_markup=get_main_keyboard()
        )
    await callback.answer()

