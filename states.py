from aiogram.fsm.state import State, StatesGroup


class MainSG(StatesGroup):
    passw = State()
    main = State()
    common_info = State()

class ArchiveSG(StatesGroup):
    start = State()
    pump_choice = State()
    date_choice = State()
    plot = State()
