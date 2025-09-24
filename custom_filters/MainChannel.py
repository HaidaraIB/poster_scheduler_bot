from telegram import Update
from telegram.ext.filters import UpdateFilter
import models


class MainChannel(UpdateFilter):
    def filter(self, update: Update):
        with models.session_scope() as s:
            postchat = s.get(models.PostChat, update.effective_chat.id)
            if not postchat:
                return False
            return postchat.is_main
