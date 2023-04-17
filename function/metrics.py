from database.psql import Database
from .api import post_api, set_date, set_date_productivity
from config.conf import Config
from bot.auth import get_public_api
from datetime import timedelta
from logger.logger import Logger


async def change_revenue(today, week):
    try:
        perc = round((today * 100 / week) - 100)
    except ZeroDivisionError:
        perc = 0
    if perc >= 0:
        perc = f'+{perc}'
        message = f'{int(today)} <b>{perc}%</b> \U0001F7E2'
    else:
        message = f'{int(today)} <b>{perc}%</b> \U0001F534'
    return message


async def change_time(tm):
    hour = tm.seconds // 3600
    minute = tm.seconds % 3600 // 60
    second = tm.seconds % 3600 % 60
    if minute < 10:
        minute = f'0{minute}'
    if second < 10:
        second = f'0{second}'
    return f'{hour}:{minute}:{second}'


async def send_metrics():
    db = Database()
    cfg = Config()
    logger = Logger('metrics')
    orders = db.select_orders('metrics')
    for order in orders:
        logger.info(f'START metrics {order[1]}')
        uuids = ','.join(order[1])
        dt_start, dt_end, created_after = await set_date(order[4], minutes=0)
        start_prod, end_prod, seconds_now = await set_date_productivity(order[4])
        delivery_stat = await post_api(f'https://api.dodois.io/dodopizza/{order[3]}/delivery/statistics/',
                                       order[0], units=uuids, _from=dt_start, to=dt_end)
        product = await post_api(f'https://api.dodois.io/dodopizza/{order[3]}/production/productivity',
                                 order[0], units=uuids, _from=start_prod, to=end_prod)
        handover = await post_api(f'https://api.dodois.io/dodopizza/{order[3]}/production/orders-handover-statistics',
                                  order[0], units=uuids, _from=dt_start, to=dt_end, salesChannels='DineIn')
        for unit in order[1]:
            speed, shf, tm = timedelta(0), timedelta(0), timedelta(0)
            productivity, prod_hour, orders_hour, cert = 0, 0, 0, 0
            rest_id = db.get_stationary(unit)
            link = f'https://publicapi.dodois.io/{order[3]}/api/v1/' \
                   f'OperationalStatisticsForTodayAndWeekBefore/{rest_id[3]}'
            revenue = await get_public_api(link)
            today = revenue['today']
            week = revenue['weekBeforeToThisTime']
            revenue_today = today['revenue']
            revenue_week = week['revenue']
            try:
                for delivery in delivery_stat['unitsStatistics']:
                    if delivery['unitId'] == unit:
                        avg_delivery = timedelta(seconds=delivery['avgDeliveryOrderFulfillmentTime'])
                        shelf = timedelta(seconds=delivery['avgHeatedShelfTime'])
                        cert = delivery['lateOrdersCount']
                        speed = await change_time(avg_delivery)
                        shf = await change_time(shelf)
            except KeyError:
                logger.error(f'ERROR delivery in metrics')
            try:
                for prod in product['productivityStatistics']:
                    if prod['unitId'] == unit:
                        productivity = prod['salesPerLaborHour']
                        prod_hour = prod['productsPerLaborHour']
                        orders_hour = prod['ordersPerCourierLabourHour']
            except KeyError:
                logger.error(f'ERROR productivity in metrics')
            try:
                for hand in handover['ordersHandoverStatistics']:
                    if hand['unitId'] == unit:
                        time_rest = timedelta(seconds=(hand['avgTrackingPendingTime'] + hand['avgCookingTime']))
                        tm = await change_time(time_rest)
            except KeyError:
                logger.error(f'ERROR handover in metrics')
            rev = await change_revenue(revenue_today, revenue_week)
            if seconds_now >= 39500:
                message = f'<b>{rest_id[1]}</b>\n' \
                          f'<b>Выручка:</b> {rev}\n' \
                          f'<b>Производительность:</b> {int(productivity)}\n' \
                          f'<b>Продуктов на чел/час:</b> {str(prod_hour).replace(".", ",")}\n' \
                          f'<b>Скорость доставки:</b> {speed}\n' \
                          f'<b>Время на полке:</b> {shf}\n' \
                          f'<b>Заказов на курьера/час:</b> {str(orders_hour).replace(".", ",")}\n' \
                          f'<b>Сертификаты:</b> {cert}\n' \
                          f'<b>Время приготовления в ресторан:</b> {tm}\n'
                await cfg.bot.send_message(order[5], message)
        logger.info(f'OK metrics')
