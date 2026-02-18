from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Time, ForeignKey, Enum
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, index=True, unique=True)
    username = Column(String)
    records = relationship("Record", back_populates="user", cascade="delete, all")


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id") , index=True)
    create_at = Column(DateTime)
    title = Column(String)
    time = Column(Time)
    repetition = Column(Integer)
    day_week = Column(String)
    next_reminder = Column(DateTime)
    category = Column(Enum("task", "habit"))
    user = relationship("User", back_populates="records")