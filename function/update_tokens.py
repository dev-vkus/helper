from database.psql import Database
from bot.auth import update_tokens
from logger.logger import Logger


async def update_app():
    logger = Logger('update_tokens')
    db = Database()
    tokens = db.select_tokens()
    link = 'https://auth.dodois.io/connect/token'
    for token in tokens:
        try:
            token_response = await update_tokens(url=link, refresh=token[2])
            access = token_response['access_token']
            refresh = token_response['refresh_token']
            db.update_tokens(token[0], access, refresh)
            logger.info(f'OK update id={token[0]}')
        except Exception as e:
            logger.error(f'ERROR update id={token[0]} - {e}')
