from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from app.models.user_resume import User
from app.db.session import get_db
from app.services.crud import create_user
from app.api.routes.deps import get_current_user

class UserCreate(BaseModel):
    email: EmailStr
    password:str

class UserResponse(BaseModel):
    id: int
    email: EmailStr

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
     new_user = await create_user(db=db,user_in=user_in)
     return new_user

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"email":current_user.email,"id":current_user.id}
    