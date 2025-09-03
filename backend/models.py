from sqlalchemy import Column, SmallInteger, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String)
    time_series = relationship("TimeSeriesPoint", back_populates="item")

class TimeSeriesPoint(Base):
    __tablename__ = "time_series_points"
    id = Column(BigInteger, primary_key=True, index=True)
    item_id = Column(BigInteger, ForeignKey("items.id"))
    timestamp = Column(Integer, index=True)
    favorited = Column(Integer)
    rap = Column(Integer)
    best_price = Column(BigInteger)
    num_sellers = Column(SmallInteger)

    item = relationship("Item", back_populates="time_series")
