from database.psql import Database
from .api import post_api, set_date
from datetime import datetime
from config.conf import Config
from logger.logger import Logger


async def stop_channel():
    db = Database()
    logger = Logger('stops')
    cfg = Config()
    ch_type = {
        'Takeaway': 'Самовывоз', 'Delivery': 'Доставка', 'Dine-in': 'Ресторан'
    }
    orders = db.select_orders('stops')
    for order in orders:
        logger.info(f'START stops {order[1]}')
        uuids = ','.join(order[1])
        dt_start, dt_end, created_after = await set_date(order[4], minutes=5)
        channel = await post_api(f'https://api.dodois.io/dodopizza/{order[3]}/production/stop-sales-channels',
                                 order[0], units=uuids, _from=dt_start, to=dt_end)
        try:
            for ch in channel['stopSalesBySalesChannels']:
                start_date = ch['startedAt']
                start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
                if start_date > created_after:
                    tm = ch['startedAt'].replace('T', ' ')
                    rest = ch['unitName']
                    reason = ch['reason']
                    cnl = ch['salesChannelName']
                    message = f'<b>{rest}</b>\n' \
                              f'<b>Время стопа: {tm}</b>\n' \
                              f'<b>Остановили: {ch_type[cnl]}</b>\n' \
                              f'<b>Причина:</b> {reason}\n'
                    await cfg.bot.send_message(order[5], message)
            logger.info(f'OK stops')
        except TypeError:
            logger.error(f'ERROR stops')
        except KeyError:
            logger.error(f'ERROR stops')


async def stop_ingredients():
    ings = [
        "Тесто 25", "Тесто 30", "Тесто 35",
        "Сыр моцарелла", "Пицца-соус", 'Соус Альфредо',
        "Бекон(слайс)", "Ветчина", "Говядина", "Картофель соломкой",
        "Кофе зерно", "Лук красный", "Мороженое", "Молоко",
        "Салат свежий", "Салями Пепперони", "Салями Чоризо",
        "Перец свежий", "Соус МаксТейсти(Бургер)", "Соус Барбекю",
        "Соус Чесночный ранч", "Томаты свежие", "Цыпленок филе",
        "Чеснок сухой", "Шампиньоны свежие", "Тортилья пшеничная 25см",
        "Добрый Кола 0,33", "Добрый Кола 0,5", "Маффин Три шоколада",
        "Соус Сырный порционный", "Чизкейк", "Коробка 25", "Коробка 30",
        "Коробка 35", "Стакан для кофе 250мл", "Стакан для кофе 300мл",
        "Стакан для кофе 400мл"
    ]
    db = Database()
    cfg = Config()
    logger = Logger('ings')
    orders = db.select_orders('ings')
    for order in orders:
        uuids = ','.join(order[1])
        logger.info(f'START ings {order[1]}')
        dt_start, dt_end, created_after = await set_date(order[4], minutes=5)
        ingredient = await post_api(f'https://api.dodois.io/dodopizza/{order[3]}/production/stop-sales-ingredients',
                                    order[0], units=uuids, _from=dt_start, to=dt_end)
        try:
            for ing in ingredient['stopSalesByIngredients']:
                start_date = ing['startedAt']
                start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
                if start_date > created_after:
                    tm = ing['startedAt'].replace('T', ' ')
                    reason = ing['reason']
                    rest = ing['unitName']
                    stop_ing = ing['ingredientName']
                    if stop_ing in ings:
                        message = f'<b>{rest}</b>\n' \
                                  f'<b>Время стопа: {tm}</b>\n' \
                                  f'<b>Остановили: {stop_ing}</b>\n' \
                                  f'<b>Причина:</b> {reason}\n'
                        await cfg.bot.send_message(order[5], message)
            logger.info(f'OK ings')
        except TypeError:
            logger.error(f'ERROR ings')
        except KeyError:
            logger.error(f'ERROR ings')
