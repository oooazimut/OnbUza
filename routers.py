from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio.session import AsyncSession

from db.models import User
from states import MainSG

start_router = Router()


@start_router.message(CommandStart())
async def start_nandler(msg: Message, dialog_manager: DialogManager):
    # session: AsyncSession = dialog_manager.middleware_data["session"]
    # start_state = MainSG.passw
    # query = select(User).filter_by(id=msg.from_user.id)
    # user = await session.scalar(query)
    # if user:
    #     start_state = MainSG.main
    start_state = MainSG.main
    await dialog_manager.start(state=start_state, mode=StartMode.RESET_STACK)
