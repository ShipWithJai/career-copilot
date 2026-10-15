from datetime import datetime
from typing import List
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.user_resume import Base
from pgvector.sqlalchemy import Vector

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    company: Mapped[str]=mapped_column(index=True,nullable=False)
    location:Mapped[str]=mapped_column(index=True,nullable=False)
    description:Mapped[str]=mapped_column(Text)
    apply_url: Mapped[str]=mapped_column(nullable=False)
    source: Mapped[str]=mapped_column(nullable=False)
    embeddings:Mapped[List[float] | None]= mapped_column(Vector(768))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

if __name__ == "__main__":
   print("sql model created")
   