from aiohttp import web
import json
import asyncio
from database_requests import auth, check_token, logout, create_topic, get_topics, get_comments, like_topic, create_comment
from multidict import MultiDict
import configparser


class Handler():

    db_conn = None
    timeout = 10

    async def login(self, request):
        data = await request.post()

        headers = MultiDict({'Authorization': ''})

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return web.json_response(status=400, headers=headers)

        user, token = await auth(self.db_conn, username, password)

        if not user:
            return web.json_response(status=401, headers=headers)

        data_to_response = {'data': user}
        headers = MultiDict({'Authorization': token})

        if not token:
            return web.json_response(status=401, headers=headers)

        return web.json_response(status=200, headers=headers, data=data_to_response)

    async def logout(self, request):
        header = request.headers
        authorization = header.get('Authorization')
        headers = MultiDict({'Authorization': ''})

        if not authorization:
            return web.json_response(status=401, headers=headers)

        is_auth = await logout(self.db_conn, authorization)
        if not is_auth:
            return web.json_response(status=401, headers=headers)
        else:
            return web.json_response(status=200, headers=headers)

    async def topic_create(self, request):
        data = await request.post()
        title = data.get('title')
        body = data.get('body')

        header = request.headers
        authorization = header.get('Authorization')
        if authorization: 
            headers = MultiDict({'Authorization': authorization})
        else:
            headers = MultiDict({'Authorization': ''})

        if not title or not body or not authorization:
            return web.json_response(status=400, headers=headers)

        user = await check_token(self.db_conn, authorization)
        if not user:
            return web.json_response(status=400, headers=headers)

        topic = await create_topic(self.db_conn, title, body, user['id'])
        data_to_response = {'data': topic}

        return web.json_response(status=200, headers=headers, data=data_to_response)

    async def topic_list(self, request):
        # data = await request.text()
        data = (await request.text()).split('&')
        data_list = {}
        limit = None
        offset= None
        if data and data[0]: 
            for line in data:
                temp = line.split('=')
                data_list[temp[0]]=temp[1]
            limit = data_list.get('limit')
            offset = data_list.get('offset')


        header = request.headers
        authorization = header.get('Authorization')
        if authorization: 
            headers = MultiDict({'Authorization': authorization})
        else:
            headers = MultiDict({'Authorization': ''})


        if not limit:
            limit = 100
        else:
            try:
                limit = int(limit)
            except ValueError:
                return web.json_response(status=400, headers=headers)
        if not offset:
            offset = 0
        else:
            try:
                limit = int(limit)
            except ValueError:
                return web.json_response(status=400, headers=headers)

        topics = await get_topics(self.db_conn, limit, offset)
        data_to_response = {'data': topics}

        return web.json_response(status=200, headers=headers, data=data_to_response)

    async def topic_like(self, request):
        data = await request.post()
        topic_id = data.get('topic_id')

        header = request.headers
        authorization = header.get('Authorization')
        if authorization: 
            headers = MultiDict({'Authorization': authorization})
        else:
            headers = MultiDict({'Authorization': ''})

        if not topic_id or not authorization:
            return web.json_response(status=400, headers=headers)

        if not topic_id:
            return web.json_response(status=400, headers=headers)
        else:
            try:
                topic_id = int(topic_id)
            except ValueError:
                return web.json_response(status=400, headers=headers)

        user = await check_token(self.db_conn, authorization)
        if not user:
            return web.json_response(status=400, headers=headers)

        res, like = await like_topic(self.db_conn, topic_id, user['id'], self.timeout)

        if res == 1:
            data_to_response = {'data': like}
            return web.json_response(status=200, headers=headers, data=data_to_response)
        elif res == 2:
            data_to_response = {'data': None}
            return web.json_response(status=200, headers=headers, data=data_to_response)
        elif res == 3:
            return web.json_response(status=400, headers=headers)
        else:
            return web.json_response(status=403, headers=headers)

    async def comment_create(self, request):
        data = await request.post()
        topic_id = data.get('topic_id')
        body = data.get('body')

        header = request.headers
        authorization = header.get('Authorization')
        if authorization: 
            headers = MultiDict({'Authorization': authorization})
        else:
            headers = MultiDict({'Authorization': ''})

        if not topic_id or not authorization or not body:
            return web.json_response(status=400, headers=headers)
        else:
            try:
                topic_id = int(topic_id)
            except ValueError:
                return web.json_response(status=400, headers=headers)

        user = await check_token(self.db_conn, authorization)
        if not user:
            return web.json_response(status=400, headers=headers)

        comment = await create_comment(self.db_conn, topic_id, user['id'], body)
        if not comment:
            return web.json_response(status=400, headers=headers)
        else:
            data_to_response = {'data': comment}
            return web.json_response(status=200, headers=headers, data=data_to_response)

    async def comment_list(self, request):
        data = (await request.text()).split('&')
        data_list = {}
        limit = None
        offset= None
        topic_id = None
        if data and data[0]: 
            for line in data:
                temp = line.split('=')
                data_list[temp[0]]=temp[1]
            topic_id = data_list.get('topic_id')
            limit = data_list.get('limit')
            offset = data_list.get('offset')

        header = request.headers
        authorization = header.get('Authorization')
        if authorization: 
            headers = MultiDict({'Authorization': authorization})
        else:
            headers = MultiDict({'Authorization': ''})

        if not topic_id:
            return web.json_response(status=400, headers=headers)
        else:
            try:
                topic_id = int(topic_id)
            except ValueError:
                return web.json_response(status=400, headers=headers)

        if not limit:
            limit = 100
        else:
            try:
                limit = int(limit)
            except ValueError:
                return web.json_response(status=400, headers=headers)
        if not offset:
            offset = 0
        else:
            try:
                limit = int(limit)
            except ValueError:
                return web.json_response(status=400, headers=headers)

        comments = await get_comments(self.db_conn, topic_id, limit, offset)
        data_to_response = {'data': comments}

        return web.json_response(status=200, headers=headers, data=data_to_response)


