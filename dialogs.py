from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

import handlers
from states import MainSG


main = Dialog(
    Window(
        Const("Введите пароль"),
        MessageInput(func=handlers.check_passwd, content_types=[ContentType.TEXT]),
        state=MainSG.passw,
    ),
    Window(
        Const("Меню:"),
        Button(Const('Общая информация'), id='common_info', on_click=handlers.on_common),
        state=MainSG.main
    ),
)
