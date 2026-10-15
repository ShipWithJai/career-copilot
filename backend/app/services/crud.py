import asyncio
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from app.models.user_resume import User
from app.db.session import AsyncSessionLocal 

class UserCreate(BaseModel):
    email: EmailStr
    password:str

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    db_user = User()
    db_user.email=user_in.email
    db_user.hashed_password=get_password_hash(user_in.password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_email(email:str,db:AsyncSession):
  stmt=select(User).where(User.email==email)
  result=await db.execute(stmt)
  return result.scalar_one_or_none()


async def main():
    async with AsyncSessionLocal() as db:
         dummy_input = UserCreate(email="Someone2@gmail.com",password="SomeoneNotYours")
         new_user = await create_user(db=db, user_in=dummy_input)
         print(f"User created with ID: {new_user.id}")
       

if __name__ == "__main__":
    asyncio.run(main())