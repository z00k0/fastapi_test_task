import logging

import sqlalchemy as sa

from app.models import endpoints, devices
from app.pg_db import db
from app.schemas import DevicesIn


async def get_devices():
    query = devices.select()

    return await db.fetch_all(query)


async def create_device(device: DevicesIn):
    query = devices.insert().return_defaults()
    values = {
        'dev_id': device.dev_id,
        'dev_type': device.dev_type
    }
    new_dev_id = await db.execute(query=query, values=values)

    logging.info(f'{new_dev_id=}')

    return {**device.dict(), 'id': new_dev_id}


async def update_device(device_id: int, device: DevicesIn):
    query = devices.update().where(devices.c.id == device_id).returning(devices.c.id)
    values = {
        "dev_id": device.dev_id,
        "dev_type": device.dev_type
    }
    await db.execute(query=query, values=values)

    return {**device.dict(), 'id': device_id}


async def delete_device(device_id: int):
    query = devices.delete().where(devices.c.id == device_id)
    await db.execute(query)
    return_message = {'message': f'Device with id: {device_id} deleted successfully.'}

    return return_message


async def select_devices():
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
