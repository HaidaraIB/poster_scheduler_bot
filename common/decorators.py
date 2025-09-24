from telegram import Update
from telegram.ext import ContextTypes
from common.force_join import check_if_user_member
import functools
import models


def check_if_user_banned_dec(func):
    @functools.wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        with models.session_scope() as s:
            user = s.get(models.User, update.effective_user.id)
            if user.is_banned:
                return
        return await func(update, context, *args, **kwargs)

    return wrapper


def add_new_user_dec(func):
    @functools.wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        with models.session_scope() as s:
            user = s.get(models.User, update.effective_user.id)
            if not user:
                tg_user = update.effective_user
                user = models.User(
                    user_id=tg_user.id,
                    username=tg_user.username if tg_user.username else "",
                    name=tg_user.full_name,
                )
                s.add(user)
        return await func(update, context, *args, **kwargs)

    return wrapper


def check_if_user_member_decorator(func):
    @functools.wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        is_user_member = await check_if_user_member(update=update, context=context)
        if not is_user_member:
            return
        return await func(update, context, *args, **kwargs)

    return wrapper
