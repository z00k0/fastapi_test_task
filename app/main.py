import logging
import os
from databases import Database
from fastapi import FastAPI, status
from dotenv import load_dotenv

from app.crud.anagram import anagram_check
from app.crud.crud_devices import get_devices, create_device, update_device, delete_device, select_devices
from app.crud.crud_endpoints import get_endpoints, create_endpoint, update_endpoint, delete_endpoint
from app.pg_db import start_db, db
from app.schemas import DevicesIn, Devices, Endpoint, EndpointUpd, EndpointNew


load_dotenv()
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_SERVER = os.getenv('POSTGRES_SERVER')

# Configure logging
logging.basicConfig(
    level=os.getenv('LOGGING_LEVEL', 'DEBUG'),
    filename='../pg_db.log',
    format='%(asctime)s %(levelname)s:%(message)s',
    encoding="UTF-8",
)

# DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DB}'
# db = Database(DATABASE_URL)

app = FastAPI()


@app.on_event('startup')
async def startup_event():
    await db.connect()
    await start_db()


@app.on_event('shutdown')
async def shutdown_event():
    await db.disconnect()


@app.get('/check/')
async def check(str_1: str, str_2: str):
    resp = await anagram_check(str_1, str_2)

    return resp


@app.get('/devices/', response_model=list[Devices])
async def devices_list():
    _devices_list = await get_devices()

    return _devices_list


@app.post('/devices/', response_model=Devices, status_code=status.HTTP_201_CREATED)
async def device_add(device: DevicesIn):
    new_device_dict = await create_device(device)

    return new_device_dict


@app.put('/devices/{device_id}', response_model=Devices)
async def device_update(device_id: int, device: DevicesIn):
    updated_device = await update_device(device_id, device)

    return updated_device


@app.delete('/devices/{device_id/')
async def device_delete(device_id: int):
    return_message = await delete_device(device_id)

    return return_message


@app.get('/endpoints/', response_model=list[Endpoint])
async def endpoints_list():
    endpoints_as_dict = await get_endpoints()

    return endpoints_as_dict


@app.post('/endpoints/', response_model=Endpoint, status_code=status.HTTP_201_CREATED)
async def endpoint_create(endpoint: EndpointNew):
    _endpoint = await create_endpoint(endpoint)

    return _endpoint


@app.put('/endpoints/{endpoint_id}/', response_model=Endpoint)
async def endpoint_update(endpoint_id: int, endpoint: EndpointUpd):
    _endpoint = await update_endpoint(endpoint_id, endpoint)

    return _endpoint


@app.delete('/endpoints/{endpoint_id}')
async def endpoint_delete(endpoint_id: int):
    return_message = await delete_endpoint(endpoint_id)

    return return_message


@app.get('/devices/select/')
async def devices_select():
    _devices_list = await select_devices()
    return _devices_list
