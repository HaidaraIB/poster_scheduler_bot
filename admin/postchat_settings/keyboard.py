from telegram import InlineKeyboardButton
import models


def build_postchat_settings_keyboard():
    return [
        [
            InlineKeyboardButton(
                text="إضافة ➕",
                callback_data="add_postchat",
            ),
        ],
        [
            InlineKeyboardButton(
                text="حذف ✖️",
                callback_data="delete_postchat",
            ),
        ],
        [
            InlineKeyboardButton(
                text="تعديل ♻️",
                callback_data="update_postchat",
            ),
        ],
    ]


def build_update_postchat_keyboard(chat: models.PostChat):
    return [
        [
            InlineKeyboardButton(
                text=f"القناة الرئيسية {'🟢' if chat.is_main else '🔴'}",
                callback_data=f"update_postchat_is_main_{chat.chat_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text=f"القناة تدعم الفيديوهات {'🟢' if chat.support_videos else '🔴'}",
                callback_data=f"update_postchat_support_videos_{chat.chat_id}",
            )
        ],
    ]
