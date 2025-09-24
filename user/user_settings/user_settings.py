from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from user.user_settings.common import build_settings_keyboard
from common.keyboards import (
    build_back_to_home_page_button,
    build_keyboard,
    build_back_button,
)
from common.lang_dicts import *


async def user_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        lang = get_lang(update.effective_user.id)
        keyboard = build_settings_keyboard(lang)
        keyboard.append(build_back_to_home_page_button(lang=lang, is_admin=False)[0])
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["settings"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


async def change_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        if update.callback_query.data in models.Language._member_names_:
            lang = models.Language[update.callback_query.data]
            with models.session_scope() as s:
                user = s.get(models.User, update.effective_user.id)
                user.lang = lang
            await update.callback_query.answer(
                text=TEXTS[lang]["change_lang_success"],
                show_alert=True,
            )

        else:
            lang = get_lang(update.effective_user.id)

        keyboard = build_keyboard(
            columns=2,
            texts=[l.value for l in models.Language],
            buttons_data=[l.name for l in models.Language],
        )
        keyboard.append(build_back_button(data="back_to_user_settings", lang=lang))
        keyboard.append(build_back_to_home_page_button(lang=lang, is_admin=False)[0])
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["change_lang"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


user_settings_handler = CallbackQueryHandler(
    user_settings,
    "^user_settings$|^back_to_user_settings$",
)
change_lang_handler = CallbackQueryHandler(
    change_lang,
    lambda x: x in [l.name for l in models.Language] + ["change_lang"],
)
