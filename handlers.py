from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from db.models import User


async def check_passwd(msg: Message, msg_inpt, manager: DialogManager):
    if msg.text == settings.passwd.get_secret_value():
        session: AsyncSession = manager.middleware_data["session"]
        session.add(User(id=msg.from_user.id, name=msg.from_user.full_name))
        await session.commit()
        await manager.next()
    else:
        await msg.answer("Неверно, попробуйте ещё раз")

async def on_common(clb: CallbackQuery, button, manager: DialogManager):
    pass
