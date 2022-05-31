import logging

import sqlalchemy as sa

from app.models import endpoints, devices
from app.schemas import EndpointNew, EndpointUpd
from app.utils import resp_to_dict
from app.pg_db import db


async def get_endpoints():
    join = sa.join(endpoints, devices, devices.c.id == endpoints.c.device_id)
    query = sa.select([endpoints, devices]).select_from(join)
    resp = await db.fetch_all(query)

    endpoints_as_dict = []  # mapping response to dictionary
    for row in resp:
        _endpoint = resp_to_dict(row)
        endpoints_as_dict.append(_endpoint)

    logging.info(f'{endpoints_as_dict=}')

    return endpoints_as_dict


async def create_endpoint(endpoint: EndpointNew):
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


async def update_endpoint(endpoint_id: int, endpoint: EndpointUpd):
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


async def delete_endpoint(endpoint_id: int):
    query = endpoints.delete().where(endpoints.c.id == endpoint_id)
    await db.execute(query)
    return_message = {'message': f'Endpoint with id: {endpoint_id} deleted successfully.'}

    return return_message
