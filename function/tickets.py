from config.conf import Config
from database.psql import Database
from .api import set_date
from bot.auth import pyrus_api


async def send_tickets():
    db = Database()
    cfg = Config()
    orders = db.select_orders('tickets')
    dt_start, dt_end, created_after = await set_date('UTC', minutes=5)
    for order in orders:
        catalogs = ','.join(order[2])
        data = {
            "field_ids": [1, 60, 57, 198, 13, 222, 37, 202, 196, 204, 203, 2, 261, 262, 134],
            "include_archived": "y",
            "created_after": dt_start + 'Z',
            "created_before": dt_end + 'Z',
            "fld198": catalogs
        }
        pyrus = await pyrus_api('https://api.pyrus.com/v4/forms/522023/register', data)
        try:
            tasks = pyrus['tasks']
        except KeyError:
            tasks = []
        for task in tasks:
            problem = []
            checker, comment, name = '', '', ''
            type_order, number_order, grade = '', 0, 0
            dt, tm = '', ''
            id_task = task['id']
            tickets = await pyrus_api(f'https://api.pyrus.com/v4/tasks/{id_task}')
            try:
                ticket = tickets['task']
                fields = ticket['fields']
            except KeyError:
                fields = []
            for field in fields:
                if field['id'] == 198:
                    value = field['value']
                    try:
                        name = value['values'][1]
                    except IndexError:
                        name = ''
                elif field['id'] == 284:
                    try:
                        number_order = field['value']
                    except KeyError:
                        number_order = ''
                elif field['id'] == 285:
                    try:
                        dt = field['value']
                    except KeyError:
                        dt = ''
                elif field['id'] == 286:
                    try:
                        tm = field['value']
                    except KeyError:
                        tm = ''
                elif field['id'] == 280:
                    try:
                        value = field['value']
                        type_order = value['choice_names'][0]
                    except IndexError:
                        type_order = ''
                    except KeyError:
                        type_order = ''
                elif field['id'] == 13:
                    try:
                        value = field['value']['fields']
                    except KeyError:
                        value = []
                    for fld_value in value:
                        if fld_value['id'] == 142:
                            try:
                                grade = fld_value['value']
                            except KeyError:
                                grade = 0
                        elif fld_value['id'] == 143:
                            try:
                                comment = fld_value['value']
                            except KeyError:
                                comment = ''
                        elif fld_value['id'] == 144:
                            try:
                                checked = fld_value['value']['fields']
                            except KeyError:
                                checked = []
                            for check in checked:
                                if check['value'] == 'checked':
                                    checker = check['name']
                                else:
                                    checker = ''
                elif field['id'] == 202:
                    try:
                        values = field['value']
                    except KeyError:
                        values = []
                    for value in values:
                        cells = value['cells']
                        for cell in cells:
                            if cell['id'] == 203:
                                try:
                                    problem.append(cell['value']['values'][0])
                                except KeyError:
                                    pass
                                except IndexError:
                                    pass
            if checker or comment or problem:
                prb = ', '.join(problem)
                message = f'<b>{name}</b>\n' \
                          f'<b>Дата и время(UTC):</b> {dt + " " + tm}\n' \
                          f'<b>Тип заказа:</b> {type_order}\n' \
                          f'<b>Номер заказа:</b> {number_order}\n' \
                          f'<b>Оценка:</b> {grade}\n' \
                          f'<b>Отметка:</b> {checker}\n' \
                          f'<b>Комментарии:</b> {comment}\n' \
                          f'<b>Проблемы:</b> {prb}'
                await cfg.bot.send_message(order[5], message)
