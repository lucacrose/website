from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Numeric
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
    timestamp = Column(BigInteger, index=True)
    favorited = Column(BigInteger)
    rap = Column(BigInteger)
    best_price = Column(Numeric(precision=19, scale=0))
    num_sellers = Column(BigInteger)

    item = relationship("Item", back_populates="time_series")
