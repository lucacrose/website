from sqlalchemy import Column, String, Float
from database import Base

class Item(Base):
    __tablename__ = "items"
    abbreviation = Column(String(4), primary_key=True, index=True)
    name = Column(String, index=True)
    value = Column(Float)
