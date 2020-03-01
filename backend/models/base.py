"""
Base model for interacting with MongoDB
"""

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseConfig, BaseModel, Field


class RWModel(BaseModel):
    class Config(BaseConfig):
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda dt: dt.replace(tzinfo=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        }


class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime] = Field(..., alias="created_at")
    updated_at: Optional[datetime] = Field(..., alias="updated_at")


class DBModelMixin(RWModel, DateTimeModelMixin):
    _id: str
    board_id: str

    class Meta:
        collection: str = ''

    @classmethod
    async def find_one(cls, conn: AsyncIOMotorClient, q_filter: dict) -> dict:
        return await conn[cls.Meta.collection].find_one(q_filter)

    @classmethod
    async def find(cls, conn: AsyncIOMotorClient, q_filter: dict, limit: int = 10) -> list:
        x = conn[cls.Meta.collection].find(q_filter)
        return await x.to_list(limit)

    @classmethod
    async def insert_one(cls, conn: AsyncIOMotorClient, data: dict) -> str:
        # TODO: verify inserted data for unique fields values
        result = await conn[cls.Meta.collection].insert_one(data)

        return result
