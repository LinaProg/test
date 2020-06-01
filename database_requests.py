import asyncio
import asyncpg
from typing import Tuple, List
from hasher import get_password, create_token
from serializer import serializer
from datetime import datetime

async def auth(connection: asyncpg.connection.Connection,username: str,password: str) -> Tuple:

    password_hash = get_password(password)

    query = 'SELECT id, username, first_name, last_name, email, date_joined FROM Users WHERE username = $1 AND password = $2;'

    result = await connection.fetchrow(query,username,password_hash)

    if not result:
        return None, None

    token = create_token(username,password_hash)

    user = serializer(dict(result))

    await update_token(connection,token,result['id'])

    return user, token

async def logout(connection: asyncpg.connection.Connection,token: str) -> bool:

    result = await check_token(connection,token)
    if not result:
        return False
    await update_token(connection,None,result['id'])
    return True
    
async def check_token(connection: asyncpg.connection.Connection,token: str):
    query = 'SELECT id FROM Users WHERE token = $1;'

    result = await connection.fetchrow(query,token)
    return result

async def update_token(connection: asyncpg.connection.Connection, token:str, id: int) -> None:
    update_query = 'UPDATE Users SET token = $1 WHERE id = $2'
    await connection.execute(update_query,token,id)

async def create_topic(connection: asyncpg.connection.Connection, title:str, body: str, id: int):
    query = 'INSERT INTO Topic (title, body, creator_id) VALUES ($1,$2,$3);'
    await connection.execute(query,title,body,id)

    select_query = 'SELECT * FROM Topic WHERE title = $1 AND body = $2 AND creator_id = $3'
    res = await connection.fetchrow(select_query,title,body,id)
    return serializer(dict(res))

async def get_topics(connection: asyncpg.connection.Connection, limit: int, offset: int) -> List:

    select_query = 'SELECT * FROM Topic LIMIT $1 OFFSET $2;'
    res = await connection.fetch(select_query,limit,offset)
    results = []

    for topic in res:
        results.append(serializer(dict(topic)))

    return results

async def get_comments(connection: asyncpg.connection.Connection,topic:int, limit: int, offset: int) -> List:

    select_query = 'SELECT * FROM Comment WHERE topic_id = $1 LIMIT $2 OFFSET $3;'
    res = await connection.fetch(select_query,topic,limit,offset)
    results = []

    for topic in res:
        results.append(serializer(dict(topic)))

    return results

async def like_topic(connection: asyncpg.connection.Connection,topic:int,user_id:int,timeout:int = 10) -> Tuple:
    ''' 1: Like added 
        2: Like removed
        3: No such topic
        4: Cannot remove like '''
    is_topic = await check_topic(connection,topic)
    if not is_topic:
        return 3, None
    select_query = 'SELECT * FROM TopicLike WHERE topic_id = $1 and user_id = $2;'
    result = await connection.fetchrow(select_query,topic,user_id)
    if result:
        now = datetime.now()
        if (now-result['added']).seconds//60 > timeout:
            return 4, None
        else:
            delete_query = 'DELETE FROM TopicLike WHERE topic_id = $1 AND user_id = $2;'
            await connection.execute(delete_query,topic,user_id)
            update_query = 'UPDATE Topic SET number_of_likes = number_of_likes-1 WHERE id=$1;'
            await connection.execute(update_query,topic)
            return 2, None
    else:
        add_query = 'INSERT INTO TopicLike (topic_id, user_id) VALUES ($1,$2);'
        await connection.execute(add_query,topic,user_id)
        update_query = 'UPDATE Topic SET number_of_likes = number_of_likes+1 WHERE id=$1;'
        await connection.execute(update_query,topic)
        return 1, serializer({'topic_id':topic,'user_id':user_id})

async def create_comment(connection: asyncpg.connection.Connection,topic:int,user_id:int,body:str):
    is_topic = await check_topic(connection,topic)
    if not is_topic:
        return None
    create_query = 'insert into Comment (body, creator_id, topic_id) values ($1,$2,$3);'
    await connection.execute(create_query,body,user_id,topic)
    update_query = 'UPDATE Topic SET number_of_comments = number_of_comments+1 WHERE id=$1;'
    await connection.execute(update_query,topic)
    query = 'SELECT * from Comment WHERE body = $1 AND creator_id =$2 AND topic_id = $3;'
    comment = await connection.fetchrow(query,body,user_id,topic)
    return serializer(dict(comment))

    

async def check_topic(connection: asyncpg.connection.Connection,topic:int) -> bool:

    query = 'SELECT * FROM Topic WHERE id = $1;'
    res = await connection.fetch(query,topic)
    if res:
        return True
    else:
        return False