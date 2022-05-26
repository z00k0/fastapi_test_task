import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, Index, Text


metadata = sqlalchemy.MetaData()

devices = sqlalchemy.Table(
    'devices',
    metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('dev_id', String(200), index=True, ),
    Column('dev_type', String(120), index=True),
    # Index('devices_dev_id_dev_type_index', "dev_id", 'dev_type')
)

endpoints = sqlalchemy.Table(
    'endpoints',
    metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('device_id', Integer, ForeignKey('devices.c.id')),
    Column('comment', Text),
)
