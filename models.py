import time
import uuid

from pydantic import BaseModel, validator


class Post(BaseModel):
    title: str
    content: str
    public_key: str
    chain: str = 'root'
    id: str = None
    date_created: int = None

    @validator('id', always=True)
    def validate_id(cls, value: str):
        if value is None:
            value = str(uuid.uuid4())
        return value

    @validator('date_created', always=True)
    def validate_date_created(cls, value: int):
        if value is None:
            value = int(time.time())
        return value


class Credentials(BaseModel):
    public_key: str
    seed_hex: str
    access_level: int
    access_level_hmac: str
