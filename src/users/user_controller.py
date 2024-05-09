from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/users", tags=["users"])

class User(BaseModel):
    name: str
    email: str
    password: str
    ...

@router.get("/")
async def get_all():
    pass

@router.post("/")
async def create(user: User):
    pass
