from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


class KeyboardAuth:
    def __init__(self, url):
        self.auth = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'Dodo IS',
                    url=url
                )]
        ])

class Keyboard:
    set_callback = CallbackData('s', 'func_id')
    post = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f'\U0001F6A7 Стопы',
                callback_data='stops&ings'
            )],
        [
            InlineKeyboardButton(
                text=f'\U0001F4D8 Тикеты',
                callback_data=set_callback.new(func_id='tickets')
            )],
        [
            InlineKeyboardButton(
                text=f'\U0001F534 Выход',
                callback_data='exit'
            )]
    ])
    stops = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f'\U0001F9C0 Стопы ингредиентов',
                callback_data=set_callback.new(func_id='ings')
            )],
        [
            InlineKeyboardButton(
                text=f'\U0001F3E2 Стопы по каналам продаж',
                callback_data=set_callback.new(func_id='stops')
            )],
        [
            InlineKeyboardButton(
                text=f'\U0001F519 Назад',
                callback_data='back'
            )],
        [
            InlineKeyboardButton(
                text=f'\U0001F534 Выход',
                callback_data='exit'
            )]
    ])
    out = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f'\U0001F519 Назад',
                callback_data='back'
            )],
        [
            InlineKeyboardButton(
                text=f'\U0001F534 Выход',
                callback_data='exit'
            )]
    ])
