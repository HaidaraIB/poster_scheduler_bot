from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButtonRequestChat,
    Chat,
)
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from custom_filters import Admin
from common.keyboards import (
    build_back_button,
    build_back_to_home_page_button,
    build_admin_keyboard,
    build_keyboard,
)
from common.constants import HOME_PAGE_TEXT
from admin.postchat_settings.keyboard import (
    build_postchat_settings_keyboard,
    build_update_postchat_keyboard,
)
from common.back_to_home_page import back_to_admin_home_page_handler
from start import admin_command
import models


async def postchat_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_postchat_settings_keyboard()
        keyboard.append(build_back_to_home_page_button()[0])
        if update.message:
            await update.message.reply_text(
                text="تم الرجوع 👍🏻",
                reply_markup=ReplyKeyboardRemove(),
            )
            await update.message.reply_text(
                text="إعدادات القنوات/المجموعات",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await update.callback_query.edit_message_text(
                text="إعدادات القنوات/المجموعات",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return ConversationHandler.END


postchat_settings_handler = CallbackQueryHandler(
    postchat_settings, r"^postchat_settings|back_to_postchat_settings$"
)

CHAT_ID, IS_MAIN, SUPPORT_VIDEOS = range(3)


async def start_add_postchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=("اختر القناة/المجموعة التي تريد إضافتها 📌\n" "للرجوع اضغط /back"),
            reply_markup=ReplyKeyboardMarkup.from_row(
                button_row=[
                    KeyboardButton(
                        text="اختر قناة 📢",
                        request_chat=KeyboardButtonRequestChat(
                            request_id=6, chat_is_channel=True
                        ),
                    ),
                    KeyboardButton(
                        text="اختر مجموعة 👥",
                        request_chat=KeyboardButtonRequestChat(
                            request_id=7, chat_is_channel=False
                        ),
                    ),
                ],
                one_time_keyboard=True,
                resize_keyboard=True,
            ),
        )
        return CHAT_ID


back_to_start_add_postchat = postchat_settings


async def set_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):

        if update.message:
            if update.message.chat_shared:
                chat_id = update.message.chat_shared.chat_id
            else:
                chat_id = int(update.message.text)
            context.user_data["chat_id"] = chat_id
        else:
            chat_id = context.user_data["chat_id"]

        with models.session_scope() as s:
            postchat = s.get(models.PostChat, chat_id)
            if postchat:
                await update.message.reply_text(
                    text="هذه القناة/المجموعة مضافة بالفعل ⚠️"
                )
                return
        try:
            chat = await context.bot.get_chat(chat_id=chat_id)
            context.user_data["chat_title"] = chat.title
            context.user_data["chat_is_group"] = (
                chat.type == Chat.GROUP or chat.type == Chat.SUPERGROUP
            )
        except:
            await update.message.reply_text(
                text="تأكد من أن البوت مشترك في القناة/المجموعة ❗️"
            )
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    text="نعم 👍🏻",
                    callback_data="yes_is_main",
                ),
                InlineKeyboardButton(
                    text="لا 👎🏻",
                    callback_data="no_is_main",
                ),
            ],
            build_back_button("back_to_set_chat_id"),
            build_back_to_home_page_button()[0],
        ]
        if update.message:
            await update.message.reply_text(
                text="تم العثور على القناة/المجموعة ✅",
                reply_markup=ReplyKeyboardRemove(),
            )
            await update.message.reply_text(
                text=(
                    "هل تريد تعيين هذه القناة كقناة رئيسية؟\n"
                    "<b>سيتم إلغاء تعيين القناة الرئيسية الحالية</b>"
                ),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await update.callback_query.edit_message_text(
                text=(
                    "هل تريد تعيين هذه القناة كقناة رئيسية؟\n"
                    "<b>سيتم إلغاء تعيين القناة الرئيسية الحالية</b>"
                ),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        return IS_MAIN


back_to_set_chat_id = start_add_postchat


async def set_is_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            context.user_data["is_main"] = (
                update.callback_query.data.replace("_is_main", "") == "yes"
            )
        keyboard = [
            [
                InlineKeyboardButton(
                    text="نعم 👍🏻",
                    callback_data="yes_support_videos",
                ),
                InlineKeyboardButton(
                    text="لا 👎🏻",
                    callback_data="no_support_videos",
                ),
            ],
            build_back_button("back_to_set_is_main"),
            build_back_to_home_page_button()[0],
        ]
        await update.callback_query.edit_message_text(
            text="هل تدعم هذه القناة/المجموعة الفيديوهات؟",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return SUPPORT_VIDEOS


back_to_set_is_main = set_chat_id


async def set_support_videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        with models.session_scope() as s:
            if context.user_data["is_main"]:
                s.query(models.PostChat).update({models.PostChat.is_main: False})
                s.commit()
            new_chat = models.PostChat(
                chat_id=context.user_data["chat_id"],
                is_group=context.user_data["chat_is_group"],
                title=context.user_data["chat_title"],
                is_main=context.user_data["is_main"],
                support_videos=update.callback_query.data.replace("_support_videos", "")
                == "yes",
            )
            s.add(new_chat)
            s.commit()

        await update.callback_query.edit_message_text(
            text=f"تمت إضافة القناة/المجموعة بنجاح ✅",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


add_postchat_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            start_add_postchat,
            "add_postchat",
        )
    ],
    states={
        CHAT_ID: [
            MessageHandler(
                filters=filters.Regex(r"^-?[0-9]+$"),
                callback=set_chat_id,
            ),
            MessageHandler(
                filters=filters.StatusUpdate.CHAT_SHARED,
                callback=set_chat_id,
            ),
        ],
        IS_MAIN: [
            CallbackQueryHandler(
                set_is_main,
                r"^((yes)|(no))_is_main$",
            )
        ],
        SUPPORT_VIDEOS: [
            CallbackQueryHandler(
                set_support_videos,
                r"^((yes)|(no))_support_videos$",
            )
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        postchat_settings_handler,
        CallbackQueryHandler(back_to_set_chat_id, r"^back_to_set_chat_id$"),
        CallbackQueryHandler(back_to_set_is_main, r"^back_to_set_is_main$"),
        CommandHandler("back", back_to_start_add_postchat),
    ],
)


U_SELECT_CHAT, U_SELECT_FIELD = range(2)


async def start_update_postchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        with models.session_scope() as s:
            postchats = s.query(models.PostChat).all()
            if not postchats:
                await update.callback_query.answer(
                    text="ليس لدينا قنوات/مجموعات بعد ⚠️",
                    show_alert=True,
                )
                return ConversationHandler.END
            keyboard = build_keyboard(
                columns=1,
                texts=[p.title for p in postchats],
                buttons_data=[f"update_postchat_{p.chat_id}" for p in postchats],
            )
            keyboard.append(build_back_button("back_to_postchat_settings"))
            keyboard.append(build_back_to_home_page_button()[0])
            await update.callback_query.edit_message_text(
                text="اختر القنوات/المجموعات المتوفرة 📌",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return U_SELECT_CHAT


async def update_select_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        with models.session_scope() as s:
            chat_id = int(update.callback_query.data.replace("update_postchat_", ""))
            context.user_data["update_postchat_id"] = chat_id
            chat = s.get(models.PostChat, chat_id)
            keyboard = build_update_postchat_keyboard(chat)
            keyboard.append(build_back_button("back_to_update_select_chat"))
            keyboard.append(build_back_to_home_page_button()[0])
            await update.callback_query.edit_message_text(
                text="اختر الحقل الذي تريد تعديله:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return U_SELECT_FIELD


async def update_select_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        with models.session_scope() as s:
            field = update.callback_query.data.replace("update_postchat_", "")
            chat_id = int(update.callback_query.data.split("_")[-1])
            chat = s.get(models.PostChat, chat_id)
            if field.startswith("is_main"):
                s.query(models.PostChat).update({models.PostChat.is_main: False})
                s.commit()
                if not chat.is_main:
                    text = f"تم تعيين القناة/المجموعة {chat.title} لتصبح الرئيسية وإلغاء تعيين القناة الرئيسية الحالية ✅"
                else:
                    text = f"تم إلغاء تعيين القناة/المجموعة {chat.title} كرئيسية، لم يعد لديك أي قناة رئيسية الآن ✅"
                chat.is_main = not chat.is_main
            elif field.startswith("support_videos"):
                if chat.support_videos:
                    text = f"القناة/المجموعة {chat.title} لم تعد تدعم الفيديوهات ✅"
                else:
                    text = f"القناة/المجموعة {chat.title} أصبحت تدعم الفيديوهات ✅"
                chat.support_videos = not chat.support_videos
            await update.callback_query.answer(
                text=text,
                show_alert=True,
            )
            s.commit()
            keyboard = build_update_postchat_keyboard(chat)
            keyboard.append(build_back_button("back_to_update_select_chat"))
            keyboard.append(build_back_to_home_page_button()[0])
            await update.callback_query.edit_message_text(
                text="اختر الحقل الذي تريد تعديله:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return U_SELECT_FIELD


back_to_update_select_chat = start_update_postchat

update_postchat_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            start_update_postchat,
            r"^update_postchat$",
        )
    ],
    states={
        U_SELECT_CHAT: [
            CallbackQueryHandler(
                update_select_chat,
                r"^update_postchat_-?[0-9]+$",
            ),
        ],
        U_SELECT_FIELD: [
            CallbackQueryHandler(
                update_select_field,
                r"^update_postchat_((is_main)|(support_videos))_-?[0-9]+$",
            )
        ],
    },
    fallbacks=[
        postchat_settings_handler,
        back_to_admin_home_page_handler,
        admin_command,
        CallbackQueryHandler(
            back_to_update_select_chat, r"^back_to_update_select_chat$"
        ),
    ],
)


D_SELECT_CHAT, D_CONFIRM_DELETE = range(2)


async def start_delete_postchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        with models.session_scope() as s:
            postchats = s.query(models.PostChat).all()
            if not postchats:
                await update.callback_query.answer(
                    text="لا توجد قنوات/مجموعات للحذف ⚠️",
                    show_alert=True,
                )
                return ConversationHandler.END

            keyboard = [
                [
                    InlineKeyboardButton(
                        text=p.title, callback_data=f"delete_postchat_{p.chat_id}"
                    )
                ]
                for p in postchats
            ]
            keyboard.append(build_back_button("back_to_postchat_settings"))
            keyboard.append(build_back_to_home_page_button()[0])

            await update.callback_query.edit_message_text(
                text="اختر القناة/المجموعة التي تريد حذفها 📌",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return D_SELECT_CHAT


async def delete_select_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        with models.session_scope() as s:
            chat_id = int(update.callback_query.data.replace("delete_postchat_", ""))
            chat = s.get(models.PostChat, chat_id)
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="✅ نعم، احذف",
                        callback_data=f"confirm_delete_postchat_{chat_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ إلغاء",
                        callback_data=f"cancel_delete_postchat_{chat_id}",
                    )
                ],
                build_back_to_home_page_button()[0],
            ]
            await update.callback_query.edit_message_text(
                text=f"هل أنت متأكد أنك تريد حذف القناة/المجموعة <b>{chat.title}</b>؟",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return D_CONFIRM_DELETE


async def delete_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("confirm"):
            chat_id = int(update.callback_query.data.split("_")[-1])
            with models.session_scope() as s:
                chat = s.get(models.PostChat, chat_id)
                s.delete(chat)
            text = "تم حذف القناة/المجموعة بنجاح ✅"
        else:
            text = "تم إلغاء الحذف ❌"
        await update.callback_query.answer(
            text=text,
            show_alert=True,
        )
        await update.callback_query.edit_message_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


delete_postchat_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            start_delete_postchat,
            r"^delete_postchat$",
        )
    ],
    states={
        D_SELECT_CHAT: [
            CallbackQueryHandler(
                delete_select_chat,
                r"^delete_postchat_-?[0-9]+$",
            ),
        ],
        D_CONFIRM_DELETE: [
            CallbackQueryHandler(
                delete_confirmation,
                r"^((confirm)|(cancel))_delete_postchat_-?[0-9]+$",
            ),
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        postchat_settings_handler,
    ],
)
