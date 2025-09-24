from telegram.ext import ContextTypes

async def reforward_job(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    from_chat_id = job_data["from_chat_id"]
    message_id = job_data["message_id"]
    has_video = job_data["has_video"]
    support_videos = job_data["support_videos"]

    if has_video and not support_videos:
        return
    
    try:
        await context.bot.forward_message(
            chat_id=context.job.chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
        )
    except Exception as e:
        print(e)
