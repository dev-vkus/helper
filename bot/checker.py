from .auth import get_units, pyrus_api, get_public_api
from database.psql import Database
import json
from iso3166 import countries
from timezonefinder import TimezoneFinder
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors


class JSONObject:
    def __init__(self, unit):
        self.__dict__ = json.loads(unit)


async def check_rest(data):
    db = Database()
    dict_catalog = {}
    result_rest = []
    rests = data['stationary'].replace(', ', ',').split(',')
    catalogs = await pyrus_api('https://api.pyrus.com/v4/catalogs/56873')
    for catalog in catalogs['items']:
        dict_catalog[catalog['values'][0]] = catalog['item_id']
    access = db.get_token(str(data['user_id']))
    access_rests = await get_units(access=access[0])
    tf = TimezoneFinder()
    rest_auth, catalog_list, uuid_list = [], [], []
    country, tz_name = 'ru', 'Europe/Moscow'
    for rest in rests:
        rest_auth.append(rest)
    for unit in access_rests:
        if unit['name'] in rest_auth:
            rest_tuple = db.get_stationary(unit['id'])
            result_rest.append(unit['name'])
            if not rest_tuple:
                value = dict_catalog.get(unit['id'].upper())
                if value:
                    catalog_list.append(value)
                    country = countries.get(unit['countryCode']).alpha2.lower()
                    link = f'https://publicapi.dodois.io/{country}' \
                           f'/api/v1/unitinfo/pizzeria/{unit["id"].upper()}'
                    unit_info = await get_public_api(link)
                    latitude = unit_info['CoordinateY']
                    longitude = unit_info['CoordinateX']
                    unit['rest_id'] = unit_info['Id']
                    tz_name = tf.timezone_at(lng=longitude, lat=latitude)
                    uuid_list.append(unit['id'])
                    db.add_stationary(unit['name'], unit['id'], unit_info['Id'],
                                      value, country, tz_name)
            else:
                country, tz_name = rest_tuple[5], rest_tuple[6]
                catalog_list.append(rest_tuple[4])
                uuid_list.append(rest_tuple[2])
    try:
        if data['post'] != 'tickets':
            catalog_list = []
        if uuid_list:
            in_rest = db.get_order(data['post'], access[1], country, tz_name, str(data['chat_id']))
            if in_rest:
                for i in uuid_list:
                    if i not in in_rest[1]:
                        in_rest[1].append(i)
                for j in catalog_list:
                    if j not in in_rest[2]:
                        in_rest[2].append(j)
                db.update_order(in_rest[0], in_rest[1], in_rest[2])
            else:
                db.add_order(data['post'], uuid_list, catalog_list, access[1],
                             country, tz_name, str(data['chat_id']))
            return result_rest
        else:
            return []
    except errors.lookup(UNIQUE_VIOLATION):
        return []
