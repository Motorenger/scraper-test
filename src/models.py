from locale import currency
from sqlalchemy import Column, Integer, String, Date, Text, Float

from sqlalchemy.orm import declarative_base


Base = declarative_base()

class Data(Base):
    __tablename__ = "scraped-data"

    id = Column(Integer, primary_key=True)
    img_url = Column(String)
    title = Column(String)
    date_posted = Column(Date)
    location = Column(String)
    bedrooms = Column(String)
    description = Column(Text)
    currency = Column(String(2))
    price = Column(Integer)

