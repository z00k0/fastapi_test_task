from pydantic import BaseModel, Field
from typing import Union


class DevicesIn(BaseModel):
    dev_id: str = Field(..., title='Device ID', max_lenght=200)
    dev_type: str = Field(..., title='Device type', max_lenght=120)


class Devices(DevicesIn):
    id: int

    class Config:
        orm_mode = True


class DevicesUpd(BaseModel):
    id: int


class EndpointIn(BaseModel):
    device_id: Devices
    comment: str


class Endpoint(EndpointIn):
    id: int

    class Config:
        orm_mode = True


class EndpointNew(BaseModel):
    device_id: DevicesUpd  # = Field(..., exclude={'dev_id', 'dev_type'})
    comment: str


class EndpointUpd(BaseModel):
    device_id: DevicesUpd  # = Field(..., exclude={'dev_id', 'dev_type'})
    comment: str
    id: int
