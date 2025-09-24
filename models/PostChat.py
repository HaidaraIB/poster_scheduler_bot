import sqlalchemy as sa
from models.DB import Base


class PostChat(Base):
    __tablename__ = "post_chats"

    chat_id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)
    is_main = sa.Column(sa.Boolean, default=False)
    support_videos = sa.Column(sa.Boolean, default=True)

    def __repr__(self) -> str:
        return (
            f"<PostChat(chat_id={self.chat_id}, "
            f"title={self.title}, "
            f"is_main={self.is_main}, "
            f"support_videos={self.support_videos})>"
        )

    def __str__(self) -> str:
        main_status = "Main" if self.is_main else "Secondary"
        video_support = "Supports Videos" if self.support_videos else "No Video Support"
        return f"PostChat {self.chat_id}: {self.title} {main_status}, {video_support}"
