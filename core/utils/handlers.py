from aiogram import F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    URLInputFile,
)
from .helpers import generate_presentation, validate_channel_membership
from .keyboard import create_inline_keyboard, create_edit_keyboard
from src.queries.orm import AsyncOrm
from config import (
    logger,
    ch_username,
    welcome_pic,
    UserState,
    dp,
    name,
    about,
    target,
    hobby,
)


@dp.message(Command(commands=["start", "help", "restart"]))
async def handle_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    user_id = message.from_user.id

    if user := await AsyncOrm.get_user_by_id(user_id):
        markup = create_inline_keyboard(
            [
                {"text": "Да, обновить", "callback_data": "restart_flow"},
                {"text": "Нет, оставить", "callback_data": "cancel"},
            ],
            row_width=2,
        )

        await message.answer(
            f"👋 'Мы уже знакомы!'\n\n"
            f"Ваша текущая самопрезентация:\n\n{user.presentation}\n\n"
            "Хотите обновить данные?",
            reply_markup=markup,
        )
        return

    welcome_image = URLInputFile(welcome_pic)
    markup = create_inline_keyboard(
        [{"text": "Да, начнем!", "callback_data": "start_flow"}]
    )

    await message.answer_photo(
        photo=welcome_image,
        caption=(
            "👋 Здравствуйте!\n\n"
            "Я бот Коллаборатора, помогу вам составить текст "
            "самопрезентации для нетворкинга.\n\n"
            "Мне нужно получить несколько ответов на вопросы, "
            "чтобы предложить вам оптимальный текст. Начнем?"
        ),
        reply_markup=markup,
    )


@dp.callback_query(F.data == "start_flow")
async def start_questionnaire(callback: CallbackQuery, state: FSMContext):
    """Начало опроса или его перезапуск"""
    await callback.message.edit_reply_markup()

    subscribe_markup = create_inline_keyboard(
        [
            {"text": "Перейти в канал", "url": f"https://t.me/{ch_username[1:]}"},
            {"text": "Я подписался", "callback_data": "check_channel"},
        ],
        row_width=1,
    )

    await callback.message.answer(
        "🔒 Прежде чем мы начнём, мне необходимо убедиться, "
        f"что вы подписаны на наш канал {ch_username}.\n\n"
        "Пожалуйста, подпишитесь по ссылке ниже и нажмите кнопку подтверждения:",
        reply_markup=subscribe_markup,
        disable_web_page_preview=True,
    )
    await state.set_state(UserState.awaiting_channel_join)


@dp.message(UserState.collecting_name)
async def collect_name(message: Message, state: FSMContext):
    """Collect user's name"""
    if len(message.text) > 150:
        await message.answer(
            "⚠️ Слишком длинное представление. " "Пожалуйста, уложитесь в 150 символов."
        )
        return

    await state.update_data(name=message.text)

    await message.answer(
        about,
    )
    await state.set_state(UserState.collecting_about)


@dp.message(UserState.collecting_about)
async def collect_about(message: Message, state: FSMContext):
    """Collect about info"""
    if len(message.text) > 200:
        await message.answer(
            "⚠️ Слишком длинное описание. " "Пожалуйста, уложитесь в 200 символов."
        )
        return

    await state.update_data(about=message.text)

    await message.answer(
        target,
    )
    await state.set_state(UserState.collecting_target)


@dp.message(UserState.collecting_target)
async def collect_target(message: Message, state: FSMContext):
    """Collect networking target"""
    if message.text.lower() == "пропустить":
        await state.update_data(target=None)
    else:
        await state.update_data(target=message.text)

    markup = create_inline_keyboard(
        [{"text": "Пропустить", "callback_data": "skip_hobby"}],
        row_width=1,
    )

    await message.answer(
        hobby,
        reply_markup=markup,
    )
    await state.set_state(UserState.collecting_hobby)


@dp.callback_query(F.data == "skip_hobby", UserState.collecting_hobby)
async def skip_hobby(callback: CallbackQuery, state: FSMContext):
    """Skip hobby step"""
    await callback.message.edit_reply_markup()  # Удаляем кнопку пропустить
    await finalize_presentation(callback.message, state)


@dp.message(UserState.collecting_hobby)
async def collect_hobby_and_finalize(message: Message, state: FSMContext):
    """Final step - collect hobby and generate presentation"""
    if message.text.lower() == "пропустить":
        await state.update_data(hobby=None)
    else:
        await state.update_data(hobby=message.text)

    await finalize_presentation(message, state)


async def finalize_presentation(message: Message, state: FSMContext):
    """Common finalization logic"""
    user_id = message.from_user.id
    user_data = await state.get_data()

    try:
        if user := await AsyncOrm.get_user_by_id(user_id):
            await AsyncOrm.update_user_item(
                user_id=user_id,
                name=user_data["name"],
                about=user_data["about"],
                target=user_data.get("target"),
                hobby=user_data.get("hobby"),
            )
        else:
            user = await AsyncOrm.insert_user(
                id=user_id,
                name=user_data["name"],
                about=user_data["about"],
                target=user_data.get("target"),
                hobby=user_data.get("hobby"),
            )

        presentation = await generate_presentation(user_data)
        await AsyncOrm.update_user_presentation(user_id, presentation)

        await message.answer(
            "🎉 Ваша самопрезентация готова!\n\n"
            f"{presentation}\n\n"
            "Вы можете в любой момент обновить данные, отправив /start",
        )

    except Exception as e:
        logger.error(f"Error saving user data: {e}")
        await message.answer(
            "⚠️ Произошла ошибка при сохранении данных. "
            "Попробуйте позже или свяжитесь с поддержкой."
        )

    await state.clear()


@dp.callback_query(F.data == "restart_flow")
async def handle_restart(callback: CallbackQuery, state: FSMContext):
    """Обработчик перезапуска с выбором поля для редактирования"""
    await callback.message.edit_reply_markup()
    user = await AsyncOrm.get_user_by_id(callback.from_user.id)
    markup = create_edit_keyboard()

    await callback.message.answer(
        f"Выберите, что хотите обновить:\n\n"
        f"Текущая самопрезентация:\n{user.presentation}",
        reply_markup=markup,
    )


@dp.callback_query(F.data.startswith("edit_"))
async def edit_field(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора поля для редактирования"""
    field = callback.data.split("_")[1]
    prompts = {"name": name, "about": about, "target": target, "hobby": hobby}

    await callback.message.edit_text(prompts[field])
    await state.set_state(getattr(UserState, f"editing_{field}"))
    await state.update_data(editing_field=field)


@dp.message(F.text, UserState.editing_name)
@dp.message(F.text, UserState.editing_about)
@dp.message(F.text, UserState.editing_target)
@dp.message(F.text, UserState.editing_hobby)
async def save_edited_field(message: Message, state: FSMContext):
    """Сохранение отредактированного поля"""
    user_data = await state.get_data()
    field = user_data["editing_field"]
    text = message.text

    if field == "name" and len(text) > 150:
        await message.answer(
            "⚠️ Слишком длинное имя. Пожалуйста, уложитесь в 150 символов."
        )
        return
    if field == "about" and len(text) > 200:
        await message.answer(
            "⚠️ Слишком длинное описание. Пожалуйста, уложитесь в 200 символов."
        )
        return

    await AsyncOrm.update_user_item(message.from_user.id, **{field: text})
    user = await AsyncOrm.get_user_by_id(message.from_user.id)

    markup = create_edit_keyboard()
    await message.answer(
        f"✅ Поле '{field}' успешно обновлено!\n\n"
        f"Текущая самопрезентация:\n\n{user.presentation}\n\n"
        "Выберите следующее действие:",
        reply_markup=markup,
    )
    await state.set_state(None)


@dp.callback_query(F.data == "regenerate")
async def regenerate_presentation(callback: CallbackQuery):
    """Перегенерация презентации"""
    user = await AsyncOrm.get_user_by_id(callback.from_user.id)
    if not user:
        await callback.answer("Пользователь не найден!", show_alert=True)
        return

    user_data = {
        "name": user.name,
        "about": user.about,
        "target": user.target,
        "hobby": user.hobby,
    }

    try:
        presentation = await generate_presentation(user_data)
        await AsyncOrm.update_user_presentation(callback.from_user.id, presentation)

        markup = create_edit_keyboard()
        await callback.message.edit_text(
            f"🎉 Презентация перегенерирована!\n\n{presentation}\n\n"
            "Выберите следующее действие:",
            reply_markup=markup,
        )
    except Exception as e:
        logger.error(f"Error regenerating presentation: {e}")
        await callback.answer(
            "⚠️ Ошибка при генерации презентации. Попробуйте позже.", show_alert=True
        )


@dp.callback_query(F.data == "restart_full")
async def restart_full_questionnaire(callback: CallbackQuery, state: FSMContext):
    """Полный перезапуск анкеты"""
    await callback.message.edit_reply_markup()  # Удаляем старые кнопки

    subscribe_markup = create_inline_keyboard(
        [
            {"text": "Перейти в канал", "url": f"https://t.me/{ch_username[1:]}"},
            {"text": "Я подписался", "callback_data": "check_channel"},
        ],
        row_width=1,
    )

    await callback.message.answer(
        "🔒 Начинаем заполнение анкеты заново. Прежде чем продолжить, "
        f"убедитесь, что вы подписаны на наш канал {ch_username}.\n\n"
        "Пожалуйста, подпишитесь по ссылке ниже и нажмите кнопку подтверждения:",
        reply_markup=subscribe_markup,
        disable_web_page_preview=True,
    )
    await state.set_state(UserState.awaiting_channel_join)


@dp.callback_query(F.data == "finish_editing")
async def finish_editing(callback: CallbackQuery, state: FSMContext):
    """Завершение редактирования"""
    await callback.message.edit_text(
        "Редактирование завершено. Для новых изменений используйте /start"
    )
    await state.clear()


@dp.message()
async def handle_unrecognized(message: Message):
    """Handle any unrecognized messages"""
    await message.answer(
        "Я не понимаю эту команду. Пожалуйста, используйте /start для начала работы."
    )


@dp.callback_query(F.data == "check_channel", UserState.awaiting_channel_join)
async def check_channel_subscription(callback: CallbackQuery, state: FSMContext):
    """Verify channel subscription"""
    if not await validate_channel_membership(callback.from_user.id):
        await callback.answer(
            "Вы ещё не подписались на канал!",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        name,
    )
    await state.set_state(UserState.collecting_name)


@dp.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Cancel current action"""
    await callback.message.edit_text("Действие отменено.")
    await state.clear()


@dp.errors()
async def error_handler(event: Exception, bot: Bot):
    """Global error handler"""
    logger.error(f"Error occurred: {event}", exc_info=True)
