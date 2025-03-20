from aiogram.fsm.state import State, StatesGroup


class MainSG(StatesGroup):
    passw = State()
    main = State()
    common_info = State()
