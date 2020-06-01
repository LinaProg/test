import asyncio
import asyncpg
from aiohttp import web
from handler import Handler

async def pre_init(handler):
    conn = await asyncpg.connect(user="postgres",
                                 database='test',
                                 password="pass1234",
                                 host='localhost',
                                 port=5432)

    handler.db_conn = conn


async def app_factory():
    handler = Handler()
    await pre_init(handler)
    app = web.Application()

    app.add_routes([
        web.post('/auth.login', handler.Login),
        web.post('/auth.logout', handler.Logout),
        web.post('/topic.create', handler.TopicCreate),
        web.get('/topic.list', handler.TopicList),
        web.post('/topic.like', handler.TopicLike),
        web.post('/comment.create', handler.CommentCreate),
        web.get('/comment.list', handler.CommentList)
    ])
    return app

web.run_app(app_factory())
