from telegram import Update
from telegram.ext import ContextTypes, MessageHandler
import models
from custom_filters import MainChannel
from jobs import reforward_job


async def relay_main_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with models.session_scope() as s:
        chats = (
            s.query(models.PostChat)
            .filter(models.PostChat.chat_id != update.effective_chat.id)
            .all()
        )
        has_video = bool(
            update.effective_message.video
            or update.effective_message.video_note
            or update.effective_message.animation
        )
        for chat in chats:
            if has_video and not chat.support_videos:
                continue
            await context.bot.forward_message(
                chat_id=chat.chat_id,
                from_chat_id=update.effective_chat.id,
                message_id=update.effective_message.message_id,
            )
            if chat.is_group:
                context.job_queue.run_repeating(
                    callback=reforward_job,
                    interval=600,
                    first=600,
                    last=14 * 600,
                    chat_id=chat.chat_id,
                    name=f"rebroadcast {update.effective_message.id} from {update.effective_chat.id} to {chat.chat_id}",
                    data={
                        "from_chat_id": update.effective_chat.id,
                        "message_id": update.effective_message.id,
                        "has_video": has_video,
                        "support_videos": chat.support_videos,
                    },
                    job_kwargs={
                        "id": f"rebroadcast {update.effective_message.id} from {update.effective_chat.id} to {chat.chat_id}",
                        "misfire_grace_time": None,
                        "replace_existing": True,
                    },
                )


relay_main_channel_post_handler = MessageHandler(
    filters=MainChannel(),
    callback=relay_main_channel_post,
)
