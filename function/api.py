import aiohttp
import asyncio
from aiohttp.client_exceptions import ContentTypeError
import pytz
from datetime import datetime, timedelta
from logger.logger import Logger


async def set_date(tz, minutes):
    time_zone = pytz.timezone(tz)
    created_before = datetime.now(tz=time_zone).replace(second=0, microsecond=0)
    if minutes == 0:
        created_after = (created_before.replace(hour=0, minute=0)).replace(tzinfo=None)
    else:
        created_after = (created_before - timedelta(minutes=minutes)).replace(tzinfo=None)
    dt_end = datetime.strftime(created_before, '%Y-%m-%dT%H:%M:%S')
    dt_start = datetime.strftime(created_after, '%Y-%m-%dT%H:%M:%S')

    return dt_start, dt_end, created_after


async def set_date_productivity(tz):
    time_zone = pytz.timezone(tz)
    created_before = datetime.now(tz=time_zone).replace(minute=0, second=0, microsecond=0)
    created_after = (created_before.replace(hour=0, minute=0)).replace(tzinfo=None)
    dt_end = datetime.strftime(created_before, '%Y-%m-%dT%H:%M:%S')
    dt_start = datetime.strftime(created_after, '%Y-%m-%dT%H:%M:%S')
    seconds_now = (created_before.replace(tzinfo=None) - created_after).seconds
    return dt_start, dt_end, seconds_now


async def post_api(url, access, **kwargs) -> dict:
    data = {}
    retry_limit = 5
    retry_delay = 30
    logger = Logger('post_api')
    for key, value in kwargs.items():
        if key == '_from':
            data['from'] = value
        else:
            data[key] = value
    headers = {
        "user-agent": 'DodoVkus',
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {access}"
    }
    async with aiohttp.ClientSession() as session:
        for i in range(retry_limit):
            async with session.get(url, headers=headers, params=data) as response:
                try:
                    if response.status == 200:
                        response = await response.json()
                        logger.info(f'OK post_api {url} {data}-{response}')
                        return response
                    elif response.status == 429 or response.status == 503:
                        logger.error(f'ERROR post_api {url} {data}-{response}')
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f'ERROR post_api {url} {data}-{response}')
                        break
                except ContentTypeError:
                    return {}
        return {}
