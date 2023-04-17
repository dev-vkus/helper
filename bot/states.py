from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    post = State()
    auth = State()
    stops = State()
    pizza = State()
    delete = State()
