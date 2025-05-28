from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Next,
    Select,
    Start,
    SwitchTo,
    WebApp,
)
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from custom.babel_calendar import CustomCalendar
import handlers
from config import PUMPS, settings
from states import ArchiveSG, MainSG


main = Dialog(
    Window(
        Const("Введите пароль"),
        MessageInput(func=handlers.check_passwd, content_types=[ContentType.TEXT]),
        state=MainSG.passw,
    ),
    Window(
        Const("Меню:"),
        Button(
            Const("Общая информация"), id="common_info", on_click=handlers.on_common
        ),
        WebApp(Const("Тренды"), Const("https://kitvideovpn.ru:13701/webvisu.htm")),
        Start(Const("Архив"), id="start_archive", state=ArchiveSG.start),
        state=MainSG.main,
    ),
    Window(
        Const("Общая информация:"),
        StaticMedia(path=settings.common_img, type=ContentType.PHOTO),
        Back(Const("Назад")),
        state=MainSG.common_info,
    ),
)

archive = Dialog(
    Window(
        Const("Архив"),
        SwitchTo(
            Const("Газ.датчики"),
            id="to_gas_sensors",
            state=ArchiveSG.date_choice,
            on_click=handlers.select_gas_plot,
        ),
        Next(Const("Насосы")),
        Cancel(Const("Отмена")),
        state=ArchiveSG.start,
    ),
    Window(
        Const("Выбор насоса"),
        Select(
            Format("{item}"),
            id="pumps_selector",
            item_id_getter=lambda x: x,
            items=PUMPS,
            on_click=handlers.select_pump_plot,
        ),
        Back(Const("Назад")),
        Cancel(Const("Отмена")),
        state=ArchiveSG.pump_choice,
    ),
    Window(
        Const("Выбор даты"),
        CustomCalendar(id="calendar", on_click=handlers.on_date),
        Cancel(Const("Отмена")),
        state=ArchiveSG.date_choice,
    ),
    Window(
        Const("График"),
        StaticMedia(path=settings.archive_img, type=ContentType.PHOTO),
        Back(Const("Назад")),
        Cancel(Const("Отмена")),
        state=ArchiveSG.plot,
    ),
)
