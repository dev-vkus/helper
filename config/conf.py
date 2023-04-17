import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher


class Config:
    load_dotenv()
    dbase = os.getenv('DATA_BASE')
    user = os.getenv('USER_NAME')
    password = os.getenv('PASSWORD')
    host = os.getenv('IP')
    token = os.getenv('TOKEN')
    bot = Bot(token, parse_mode='HTML')
    pyrus = os.getenv('PYRUS')
    key = os.getenv('KEY')
    scope = 'staffmembers:read stopsales deliverystatistics staffshifts:read productionefficiency ' \
            'accounting user.role:read offline_access'
    redirect = os.getenv('REDIRECT')
    verifier = os.getenv('VERIFIER')
    client = os.getenv('CLIENT')
    secret = os.getenv('SECRET')
    dp = Dispatcher(bot, storage=MemoryStorage())
    scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})
