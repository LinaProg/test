import asyncio
import asyncpg
from aiohttp import web
from handler import Handler

async def pre_init(handler):
    conn = await asyncpg.connect(user="postgres",
                                 password="pass1234",
                                 host='postgres',
                                 port=5432)

    handler.db_conn = conn


async def app_factory():
    handler = Handler()
    await pre_init(handler)
    app = web.Application()

    app.add_routes([
        web.post('/auth.login', handler.login),
        web.post('/auth.logout', handler.logout),
        web.post('/topic.create', handler.topic_create),
        web.get('/topic.list', handler.topic_list),
        web.post('/topic.like', handler.topic_like),
        web.post('/comment.create', handler.comment_create),
        web.get('/comment.list', handler.comment_list)
    ])
    return app

web.run_app(app_factory())
