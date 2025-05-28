from datetime import date
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.models import Gas_Sensor, Pump, User
from service.modbus import poll_registers
from service.plots import common_info, gas_plot, pump_plot
from states import ArchiveSG, MainSG


async def check_passwd(msg: Message, msg_inpt, manager: DialogManager):
    if msg.text == settings.passwd.get_secret_value():
        session: AsyncSession = manager.middleware_data["session"]
        session.add(User(id=msg.from_user.id, name=msg.from_user.full_name))
        await session.commit()
        await manager.next()
    else:
        await msg.answer("Неверно, попробуйте ещё раз")


async def on_common(clb: CallbackQuery, button, manager: DialogManager):
    data = await poll_registers()
    if not data:
        await clb.answer("Данных нет", show_alert=True)
        return

    for p in data["pumps"]:
        p.temperature = (
            "н/д" if p.temperature < -500 or p.temperature > 500 else p.temperature
        )
        p.pressure = "н/д" if p.pressure < -500 or p.pressure > 500 else p.pressure

    await common_info(data)
    await manager.switch_to(MainSG.common_info)


async def select_gas_plot(clb, button, manager: DialogManager):
    manager.dialog_data.update(plot="gas")


async def select_pump_plot(
    clb: CallbackQuery, select, manager: DialogManager, pump: str
):
    manager.dialog_data.update(plot=pump)
    await manager.switch_to(state=ArchiveSG.date_choice)


async def on_date(event, widget, manager: DialogManager, date: date):
    manager.dialog_data.update(date=date.isoformat())
    session: AsyncSession = manager.middleware_data["session"]

    match manager.dialog_data["plot"]:
        case "gas":
            data = await session.scalars(
                select(Gas_Sensor).where(func.date(Gas_Sensor.dttm) == date)
            )
            await gas_plot(data)
        case _:
            data = await session.scalars(
                select(Pump).where(
                    func.date(Pump.dttm) == date,
                    Pump.name == manager.dialog_data["plot"],
                )
            )
            await pump_plot(data)
