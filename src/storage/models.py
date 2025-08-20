"""Database models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SignalLog(Base):
    __tablename__ = "signal_log"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


class Position(Base):
    __tablename__ = "position"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    qty = Column(Integer, nullable=False)
    entry_price = Column(Float, nullable=False)
    state = Column(String, default="INIT", nullable=False)


class OrderLog(Base):
    __tablename__ = "order_log"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
