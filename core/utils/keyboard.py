from aiogram.types import (
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_inline_keyboard(
    buttons: list[dict[str, str]], row_width: int = 1
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for button in buttons:
        if "url" in button:
            builder.button(text=button["text"], url=button["url"])
        else:
            builder.button(text=button["text"], callback_data=button["callback_data"])

    builder.adjust(row_width)
    return builder.as_markup()

def create_edit_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        {"text": "✏️ Имя", "callback_data": "edit_name"},
        {"text": "✏️ Деятельность", "callback_data": "edit_about"},
        {"text": "✏️ Цель", "callback_data": "edit_target"},
        {"text": "✏️ Хобби", "callback_data": "edit_hobby"},
        {"text": "🔄 Перегенерировать", "callback_data": "regenerate"},
        {"text": "🔄 Заполнить заново", "callback_data": "restart_full"},
        {"text": "✅ Готово", "callback_data": "finish_editing"},
    ]
    return create_inline_keyboard(buttons, row_width=2)

def create_skip_button() -> InlineKeyboardMarkup:
    buttons = [{"text": "Пропустить", "callback_data": "skip_hobby"}]
    return create_inline_keyboard(buttons, row_width=1)