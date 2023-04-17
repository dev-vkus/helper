from config.conf import Config
import aiohttp
from aiogram import executor, types
from aiogram.dispatcher.filters import Command
from database.psql import Database
from bot.keyboard import KeyboardAuth, Keyboard
from bot.states import States
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BadRequest
from bot.checker import check_rest
from bot.auth import get_tokens
from aiogram.dispatcher.filters import CommandStart
from function.update_tokens import update_app
from function.tickets import send_tickets
from function.stops import stop_channel, stop_ingredients


'''
    Планировщик задач
# '''
Config.scheduler.add_job(update_app, 'interval', hours=4)
Config.scheduler.add_job(stop_ingredients, 'interval', minutes=2)
Config.scheduler.add_job(stop_channel, 'interval', minutes=5)
Config.scheduler.add_job(send_tickets, 'interval', minutes=5)


@Config.dp.message_handler(CommandStart())
async def start_func(message: types.Message):
    db = Database()
    code = message.get_args()
    if code:
        access, refresh, sub = await get_tokens(code)
        db.add_user(message.from_user.id, access, refresh, sub)
        await message.answer(f'Привет, <strong>{message.from_user.full_name}</strong>! \U0001F44B\n'
                             f'Подписывайся на нужные уведомления:\n', reply_markup=Keyboard.post)
        await States.post.set()
    else:
        account = db.check_auth(str(message.from_user.id))
        if account[0]:
            await message.answer(f'Привет, <strong>{message.from_user.full_name}</strong>! \U0001F44B\n'
                                 f'Подписывайся на нужные уведомления:\n', reply_markup=Keyboard.post)
            await States.post.set()
        else:
            await message.answer(f'Привет, <strong>{message.from_user.full_name}</strong>! \U0001F44B\n'
                                 f'Я отправляю уведомления, такие как:\n'
                                 f'\U0001F6A7 - <b>Стопы</b>\n'
                                 f'\U0001F4D8 - <b>Тикеты</b>\n'
                                 f'Но прежде чем приступить тебе необходимо авторизоваться на маркетплейсе')


@Config.dp.message_handler(Command(commands=["del"]), state=['*'])
async def orders_func(message: types.Message, state: FSMContext):
    db = Database()
    try:
        user = db.get_user(str(message.chat.id))
        my_orders = db.get_orders(str(message.chat.id), user[0])
    except TypeError:
        my_orders = []
    dict_orders = {}
    counter, text = 0, '<b>Выберите из списка номер уведомлений, которые хотите удалить.</b>\n' \
                       '<b>Список уведомлений:</b>\n'
    for order in my_orders:
        counter += 1
        dict_orders[counter] = order
    await state.update_data(orders=dict_orders)
    for key, value in dict_orders.items():
        text += f'<b>{str(key)}</b> - {value[1]} {value[2]} {value[3]}\n'
    await message.answer(text, reply_markup=Keyboard.out)
    await States.delete.set()


@Config.dp.message_handler(state=States.delete)
async def delete_func(message: types.Message, state: FSMContext):
    db = Database()
    orders = await state.get_data()
    try:
        choice = int(message.text)
        order = orders['orders'][choice]
        db.drop_order(order[0])
        await message.answer(f'Успешно!', reply_markup=Keyboard.out)
    except TypeError:
        await message.answer(f'Укажите корректный номер уведомлений', reply_markup=Keyboard.out)
    except KeyError:
        await message.answer(f'Укажите корректный номер уведомлений', reply_markup=Keyboard.out)


@Config.dp.callback_query_handler(text='stops&ings', state=States.post)
async def post_menu(call: types.CallbackQuery):
    await call.message.answer(f'Стопы', reply_markup=Keyboard.stops)
    await States.stops.set()


@Config.dp.callback_query_handler(Keyboard.set_callback.filter(),
                                  state=[States.stops, States.post])
async def stops_rest(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    post = callback_data.get('func_id')
    await call.message.answer(f'Укажите название ресторана как в dodo is\n'
                              f'(если их несколько, то укажите все через ",")', reply_markup=Keyboard.out)
    chat = call.message.chat.id
    await state.update_data(user_id=call.from_user.id, chat_id=chat, post=post)
    await States.pizza.set()


@Config.dp.message_handler(state=States.pizza)
async def stationary(message: types.Message, state: FSMContext):
    await state.update_data(stationary=message.text)
    await message.answer('Подождите, проверяем доступность введеных ресторанов...')
    rest_list = await check_rest(await state.get_data())
    if rest_list:
        await message.answer(f"\U00002705 Вы подписали на уведомления следующие рестораны: \n"
                             f"{', '.join(str(rest) for rest in rest_list)}")
        await state.finish()
    else:
        await message.answer('Данные рестораны не авторизованы или у вас нет к ним доступа.\n'
                             'Так же проверьте правильность введенного ресторана, и попробуйте ввести еще раз',
                             reply_markup=Keyboard.out)


@Config.dp.callback_query_handler(text='back', state=[States.stops, States.pizza, States.delete])
async def back_menu(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer(f'Привет, <strong>{call.message.from_user.full_name}</strong>! \U0001F44B\n'
                              f'Я собираю уведомления, такие как:\n'
                              f'\U0001F4D8 - <b>Стопы</b>\n', reply_markup=Keyboard.post)
    await States.post.set()


@Config.dp.callback_query_handler(text='exit', state=[States.post, States.stops, States.pizza, States.delete])
async def exit_work(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(f'Возвращайтесь снова \U0001F44B')
    await state.finish()


if __name__ == '__main__':
    Config.scheduler.start()
    executor.start_polling(Config.dp)
