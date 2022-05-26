import aiopg
import logging
import os
from dotenv import load_dotenv
import random
import secrets

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from aiopg.sa import create_engine
from models import devices, endpoints


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    filename='pg_db.log',
    format='%(asctime)s %(levelname)s:%(message)s',
    encoding="UTF-8",
)

load_dotenv()
# REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
# POSTGRES_DB = os.getenv('POSTGRES_DB')
# POSTGRES_USER = os.getenv('POSTGRES_USER')
# POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
# dsn = f"dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD} host=localhost"

dev_type_list = ['emeter', 'zigbee', 'lora', 'gsm']

# SQLALCHEMY_DATABASE_URL = f"postgresql+aiopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost/{POSTGRES_DB}"

# Base = declarative_base()


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
