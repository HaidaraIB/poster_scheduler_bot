from telegram import Update
from telegram.ext.filters import UpdateFilter
import models


class MainChannel(UpdateFilter):
    def filter(self, update: Update):
        with models.session_scope() as s:
            post_chat = s.get(models.PostChat, update.effective_chat.id)
            if not post_chat:
                return False
            return post_chat.is_main
