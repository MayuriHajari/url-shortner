from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from db import Base

class URL(Base):
    __tablename__ = "url_shortener"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(Text, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())