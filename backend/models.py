from sqlalchemy import Column, BigInteger, String, Float
from database import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, index=True)
