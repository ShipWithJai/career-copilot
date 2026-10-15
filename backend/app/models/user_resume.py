from datetime import datetime
from typing import List
from sqlalchemy import String,DateTime,ForeignKey,func,Text,JSON
from sqlalchemy.orm import DeclarativeBase ,Mapped,mapped_column,relationship

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__= "users"
    id:Mapped[int]=mapped_column(primary_key=True)
    hashed_password:Mapped[str]=mapped_column(nullable=False)
    email:Mapped[str]=mapped_column(String(255),unique=True,index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,server_default=func.now())
    resumes:Mapped[List["Resume"]]=relationship(back_populates="user")
    
class Resume(Base):
    __tablename__="resumes"
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"))
    title:Mapped[str]=mapped_column(String(255),nullable=False)
    content:Mapped[str]=mapped_column(Text,nullable=False)
    user:Mapped["User"]=relationship(back_populates="resumes")
    parsed_data:Mapped[dict|None] = mapped_column(JSON,nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    
if __name__ == "__main__":
    print("Resume model loaded successfully")
    
