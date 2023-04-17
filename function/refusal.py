from database.psql import Database
from .api import post_api, set_date
from config.conf import Config
from logger.logger import Logger


async def send_refusal():
    db = Database()
    cfg = Config()
    logger = Logger('refusal')
    orders = db.select_orders('refusal')
    for order in orders:
        logger.info(f'START refusal {order[1]}')
        uuids = ','.join(order[1])
        dt_start, dt_end, created_after = await set_date(order[4], minutes=60)
        refusal = await post_api(f'https://api.dodois.io/dodopizza/{order[3]}/accounting/cancelled-sales',
                                 order[0], units=uuids, _from=dt_start, to=dt_end, take=900)
        try:
            for ref in refusal['cancelledSales']:
                rest = ref['unitName']
                tm = ref['soldAt']
                prod = ref['productName']
                price = ref['price']
                message = f'<b>{rest}</b>\n' \
                          f'<b>Время заказа: {tm}</b>\n' \
                          f'<b>Отменили: {prod}</b>\n' \
                          f'<b>Цена:</b> {price}\n'
                await cfg.bot.send_message(order[5], message)
            logger.info(f'OK refusal')
        except TypeError:
            logger.error(f'ERROR refusal')
        except KeyError:
            logger.error(f'ERROR refusal')
