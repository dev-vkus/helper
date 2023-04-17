from config.conf import Config
import psycopg2


class Database:
    @property
    def connection(self):
        cfg = Config()
        return psycopg2.connect(
            database=cfg.dbase,
            user=cfg.user,
            password=cfg.password,
            host=cfg.host,
            port='5432'
        )

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()
        return data

    def add_user(self, chat, access, refresh, sub):
        sql = '''
            INSERT INTO users (chat_id, access_token, refresh_token, sub)
            VALUES (%s, %s, %s, %s)
        '''
        params = (chat, access, refresh, sub)
        self.execute(sql, parameters=params, commit=True)

    def check_auth(self, chat):
        sql = '''
            SELECT EXISTS(SELECT id FROM users WHERE 
            chat_id = %s);
        '''
        params = (chat, )
        return self.execute(sql, parameters=params, fetchone=True)

    def get_token(self, chat):
        sql = '''
            SELECT access_token, id FROM users
            WHERE chat_id = %s;
        '''
        params = (chat,)
        return self.execute(sql, parameters=params, fetchone=True)

    def select_tokens(self):
        sql = '''
            SELECT id, access_token, refresh_token FROM users
        '''
        return self.execute(sql, fetchall=True)

    def update_tokens(self, user_id, access, refresh):
        sql = '''
            UPDATE users SET access_token = %s, refresh_token = %s
            WHERE id = %s
        '''
        parameters = (access, refresh, user_id)
        self.execute(sql, parameters=parameters, commit=True)

    def get_stationary(self, uuid):
        sql = '''
            SELECT * FROM stationary where rest_uuid = %s;
        '''
        params = (uuid, )
        return self.execute(sql, parameters=params, fetchone=True)

    def add_stationary(self, name, uuid, rest_id, catalog, country, tz):
        sql = '''
            INSERT INTO stationary (rest_name, rest_uuid, rest_id, catalog, country, time_zone)
            VALUES (%s, %s, %s, %s, %s, %s)
        '''
        params = (name, uuid, rest_id, catalog, country, tz)
        self.execute(sql, parameters=params, commit=True)

    def add_order(self, post, uuid, catalog, user, country, timezone, chat):
        sql = '''
            INSERT INTO orders (post, uuid, catalog, user_id, country, timezone, chat)
            VALUES (%s, %s, %s, %s, %s, %s, %s) 
        '''
        params = (post, uuid, catalog, user, country, timezone, chat)
        self.execute(sql, parameters=params, commit=True)

    def get_order(self, post, user, country, timezone, chat):
        sql = '''
            SELECT id, uuid, catalog FROM orders WHERE 
            post = %s and user_id = %s and country = %s and 
            timezone = %s and chat = %s
        '''
        params = (post, user, country, timezone, chat)
        return self.execute(sql, parameters=params, fetchone=True)

    def update_order(self, order_id, uuid, catalog):
        sql = '''
            UPDATE orders SET uuid = %s, catalog = %s WHERE id = %s
        '''
        params = (uuid, catalog, order_id)
        self.execute(sql, parameters=params, commit=True)

    def get_user(self, user):
        sql = '''
            SELECT id FROM users WHERE chat_id = %s
        '''
        params = (user, )
        return self.execute(sql, parameters=params, fetchone=True)

    def get_orders(self, chat, user):
        sql = '''
            SELECT id, post, country, timezone FROM orders
            WHERE chat = %s and user_id = %s
        '''
        params = (chat, user)
        return self.execute(sql, parameters=params, fetchall=True)

    def drop_order(self, order):
        sql = '''
            DELETE FROM orders WHERE id = %s
        '''
        params = (order,)
        self.execute(sql, parameters=params, commit=True)

    def select_orders(self, post):
        sql = '''
            SELECT users.access_token, orders.uuid, orders.catalog, 
            orders.country, orders.timezone, orders.chat
            FROM orders JOIN users ON users.id = orders.user_id
            WHERE orders.post = %s;
        '''
        params = (post, )
        return self.execute(sql, parameters=params, fetchall=True)

    def drop_user(self, user):
        sql = '''
            DELETE FROM users WHERE chat_id = %s
        '''
        params = (user, )
        self.execute(sql, parameters=params, commit=True)
