from typing import Optional
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
import json


with open('countries.json', encoding='UTF-8') as f:
    FLAGS = json.loads(f.read())


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    builder = InlineKeyboardBuilder()
    for i in items:
        builder.button(
            text=f'{i} {FLAGS[i]["flag"]}',
            callback_data=LanguageCallbackFactory(action="change", value=i)
        )
    builder.adjust(4)
    return builder.as_markup(resize_keyboard=True)


class LanguageCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    value: Optional[str] = None
