import logging
import os
import aioredis
import aiopg
import sqlalchemy as sa
from databases import Database
from fastapi import FastAPI, Depends, Body, status
from dotenv import load_dotenv
from aiopg.sa import create_engine

from pg_db import create_db, fill_devices, fill_endpoints
from schemas import DevicesIn, Devices, Endpoint, EndpointIn, EndpointUpd, EndpointNew, DevicesUpd
from models import devices, endpoints
from utils import resp_to_dict

load_dotenv()
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_SERVER = os.getenv('POSTGRES_SERVER')

# Configure logging
logging.basicConfig(
    level=os.getenv('LOGGING_LEVEL', 'DEBUG'),
    filename='pg_db.log',
    format='%(asctime)s %(levelname)s:%(message)s',
    encoding="UTF-8",
)

DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DB}'
db = Database(DATABASE_URL)

app = FastAPI()


def is_anagram(str_1: str, str_2: str):
    return sorted(str_1) == sorted(str_2)


async def start_db():
    engine = await create_engine(
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host='postgres'
    )
    async with engine:
        async with engine.acquire() as conn:
            await create_db(conn)
            await fill_devices(conn)
            await fill_endpoints(conn)


@app.on_event('startup')
async def startup_event():
    await db.connect()
    await start_db()


@app.on_event('shutdown')
async def shutdown_event():
    await db.disconnect()


@app.get('/check/')
async def check(str_1: str, str_2: str):
    redis = await aioredis.from_url('redis://redis', password=REDIS_PASSWORD)
    anagram = is_anagram(str_1, str_2)
    if anagram:
        await redis.incr('anagram_counter', 1)
    anagram_counter = await redis.get('anagram_counter')

    return {'str_1': str_1, 'str_2': str_2, 'is_anagram': anagram, 'anagram_counter': anagram_counter}


@app.get('/devices/', response_model=list[Devices])
async def devices_list():
    query = devices.select()

    return await db.fetch_all(query)


@app.post('/devices/', response_model=Devices, status_code=status.HTTP_201_CREATED)
async def device_add(device: DevicesIn):
    query = devices.insert().return_defaults()
    values = {
        'dev_id': device.dev_id,
        'dev_type': device.dev_type
    }
    new_dev_id = await db.execute(query=query, values=values)

    logging.info(f'{new_dev_id=}')

    return {**device.dict(), 'id': new_dev_id}


@app.put('/devices/{device_id}', response_model=Devices)
async def device_update(device_id: int, device: DevicesIn):
    query = devices.update().where(devices.c.id == device_id).returning(devices.c.id)
    values = {
        "dev_id": device.dev_id,
        "dev_type": device.dev_type
    }
    await db.execute(query=query, values=values)

    return {**device.dict(), 'id': device_id}


@app.delete('/devices/{device_id/')
async def device_delete(device_id: int):
    query = devices.delete().where(devices.c.id == device_id)

    await db.execute(query)

    return {'message': f'Device with id: {device_id} deleted successfully.'}


@app.get('/endpoints/', response_model=list[Endpoint])
async def endpoints_list():
    join = sa.join(endpoints, devices, devices.c.id == endpoints.c.device_id)
    query = sa.select([endpoints, devices]).select_from(join)
    resp = await db.fetch_all(query)

    endpoints_as_dict = []  # mapping response to dictionary
    for row in resp:
        _endpoint = resp_to_dict(row)
        endpoints_as_dict.append(_endpoint)

    logging.info(f'{endpoints_as_dict=}')

    return endpoints_as_dict


@app.post('/endpoints/', response_model=Endpoint, status_code=status.HTTP_201_CREATED)
async def endpoint_create(endpoint: EndpointNew):
    query = endpoints.insert()
    values = {
        'device_id': endpoint.device_id.id,
        'comment': endpoint.comment
    }
    new_endpoint_id = await db.execute(query=query, values=values)
    join = sa.join(endpoints, devices, devices.c.id == endpoints.c.device_id)
    query = sa.select([endpoints, devices]).select_from(join).where(endpoints.c.id == new_endpoint_id)
    resp = await db.fetch_one(query)
    _endpoint = resp_to_dict(resp)

    return _endpoint


@app.put('/endpoints/{endpoint_id}/', response_model=Endpoint)
async def endpoint_update(endpoint_id: int, endpoint: EndpointUpd):
    query = endpoints.update().where(endpoints.c.id == endpoint_id).returning(endpoints.c.id)
    values = {
        'device_id': endpoint.device_id.id,
        'comment': endpoint.comment
    }
    _id = await db.execute(query=query, values=values)
    logging.info(f'{_id=}')

    join = sa.join(endpoints, devices, devices.c.id == endpoints.c.device_id)
    query = sa.select([endpoints, devices]).select_from(join).where(endpoints.c.id == _id)
    resp = await db.fetch_one(query)
    logging.info(f'{resp=}')

    _endpoint = resp_to_dict(resp)

    return _endpoint


@app.delete('/endpoints/{endpoint_id}')
async def endpoint_delete(endpoint_id: int):
    query = endpoints.delete().where(endpoints.c.id == endpoint_id)

    await db.execute(query)

    return {'message': f'Endpoint with id: {endpoint_id} deleted successfully.'}


@app.get('/devices/select/')
async def devices_select():
    sub_query = sa.select([devices.c.id]).join(endpoints, devices.c.id == endpoints.c.device_id).subquery()
    query = sa.select(devices.c.dev_type, sa.func.count(devices.c.dev_type).label('count')).filter(
        devices.c.id.not_in(sub_query)).group_by(devices.c.dev_type)
    dev_select = await db.fetch_all(query)

    resp = []
    for row in dev_select:
        logging.info(f'{row._mapping=}')
        _dev_type = row._mapping['dev_type']
        _count = row._mapping['count']
        resp.append({'dev_type': _dev_type, 'count': _count})
    return resp
