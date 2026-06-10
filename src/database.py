from dotenv import load_dotenv
from sqlalchemy import desc
from sqlalchemy import String
from datetime import datetime
import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    Date
)
from sqlalchemy.orm import declarative_base, sessionmaker
load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
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

class QuestionLog(Base):
    __tablename__ = "question_logs"

    id = Column(
        Integer,
        primary_key=True
    )

    question = Column(
        String,
        nullable=False
    )

    answer = Column(
        String,
        nullable=False
    )

    created_at = Column(
        Date,
        nullable=False,
        default=datetime.utcnow
    )

Base.metadata.create_all(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

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