import os

from aiopg.sa import create_engine
from databases import Database
from dotenv import load_dotenv
import random
import secrets

from app.models import devices, endpoints


load_dotenv()
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_SERVER = os.getenv('POSTGRES_SERVER')

DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DB}'
db = Database(DATABASE_URL)

dev_type_list = ['emeter', 'zigbee', 'lora', 'gsm']


async def create_db(conn):
    await conn.execute(
        """
        DROP TABLE IF EXISTS endpoints;
        """
    )
    await conn.execute(
        """
        DROP TABLE IF EXISTS devices;
        """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS devices
        (
        id bigserial NOT NULL
        constraint devices_pk
        primary key,
        dev_id varchar(200) NOT NULL,
        dev_type varchar(120) NOT NULL
        );
        """
    )
    await conn.execute(
        """
        ALTER TABLE devices OWNER TO postgres;
        """
    )
    await conn.execute(
        """
        CREATE INDEX IF NOT EXISTS devices_dev_id_dev_type_index ON devices (dev_id, dev_type);
        """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS endpoints
        (
        id bigserial NOT NULL CONSTRAINT endpoints_pk primary key,
        device_id INTEGER CONSTRAINT endpoints_devices_id_fk REFERENCES devices ON UPDATE CASCADE ON DELETE CASCADE,
        comment text
        );
        """
    )
    await conn.execute(
        """
        ALTER TABLE endpoints OWNER TO postgres;
        """
    )


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


async def fill_devices(conn):
    for row in range(10):
        dev_type = random.choice(dev_type_list)
        dev_id = secrets.token_hex(24)

        await conn.execute(devices.insert().values(dev_id=dev_id, dev_type=dev_type))


async def fill_endpoints(conn):
    for row in range(1, 6):
        device_id = row * 2
        comment = f'comment # {row}'

        await conn.execute(endpoints.insert().values(device_id=device_id, comment=comment))
