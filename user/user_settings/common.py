from telegram import InlineKeyboardButton
from common.lang_dicts import *


def build_settings_keyboard(lang: models.Language):
    keyboard = [
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["lang"],
                callback_data="change_lang",
            )
        ]
    ]
    return keyboard

