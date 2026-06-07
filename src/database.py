from sqlalchemy import desc
from sqlalchemy import String

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    Date
)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///data/gold_prices.db"

engine = create_engine(
    DATABASE_URL,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class GoldPrice(Base):
    __tablename__ = "gold_prices"

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, nullable=False)
    city = Column(String, nullable=False)
    price_24k = Column(Float, nullable=False)
    price_22k = Column(Float, nullable=False)

class GoldPrice(Base):
    __tablename__ = "gold_prices"

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, nullable=False)
    city = Column(String, nullable=False)
    price_24k = Column(Float, nullable=False)
    price_22k = Column(Float, nullable=False)

Base.metadata.create_all(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)


def get_last_n_days(session, n=7):
    return (
        session.query(GoldPrice)
        .order_by(desc(GoldPrice.date))
        .limit(n)
        .all()
    )

def get_last_n_days(session, days):
    return (
        session.query(GoldPrice)
        .order_by(GoldPrice.date.desc())
        .limit(days)
        .all()
    )

def get_all_prices(session):
    return (
        session.query(GoldPrice)
        .order_by(GoldPrice.date.desc())
        .all()
    )