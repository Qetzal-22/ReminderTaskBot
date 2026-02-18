from sqlalchemy.orm import Session
from app.db.models import User, Record
from datetime import datetime, date, timedelta


def get_users(db: Session):
    return db.query(User).all()

def get_user_by_id(user_id: int, db: Session):
    return db.query(User).filter(User.id == user_id).first()

def get_user_id_by_tg_id(tg_id: int, db: Session):
    user = db.query(User).filter(User.tg_id == tg_id).first()
    user_id = user.id
    return user_id

def get_tg_id_by_user_id(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    tg_id = user.tg_id
    return tg_id

def create_user(db: Session, tg_id: int, username: str):
    user_db = User(tg_id=tg_id, username=username)
    try:
        db.add(user_db)
        db.commit()
        db.refresh(user_db)
        return user_db
    except:
        db.rollback()
        raise

def get_records(db: Session):
    return db.query(Record).all()

def get_records_by_user_id(user_id: int, db: Session):
    return db.query(Record).filter(Record.user_id == user_id)

def get_records_now(now: datetime, db: Session):
    records = db.query(Record).filter((Record.next_reminder <= now) & (Record.next_reminder >= now-timedelta(hours=3))).all()
    return records

def get_records_old(now: datetime, db: Session):
    records = db.query(Record).filter(Record.next_reminder < (now-timedelta(hours=3)))
    return records

def get_record_by_id(record_id: int, db: Session):
    return db.query(Record).filter(Record.id == record_id).first()

def create_record(db: Session, user_id: int, title: str, time: datetime.time, repetition: int, next_reminder: datetime, day_week: str, category: str):
    create_at = datetime.now().replace(second=0, microsecond=0)

    record_db = Record(
        user_id=user_id,
        create_at=create_at,
        title=title,
        time=time,
        repetition=repetition,
        day_week=day_week,
        next_reminder=next_reminder,
        category=category
    )
    try:
        db.add(record_db)
        db.commit()
        db.refresh(record_db)
        return record_db
    except:
        db.rollback()
        raise

def update_next_reminder_record(record_id: int, next_reminder: datetime, db: Session):
    record = db.query(Record).filter(Record.id == record_id).first()
    record.next_reminder = next_reminder
    db.commit()
    db.refresh(record)
    return record

def update_title_by_id(record_id: int, new_title: str, db: Session):
    record = db.query(Record).filter(Record.id == record_id).first()
    record.title = new_title
    db.commit()
    db.refresh(record)
    return record

def delete_record(record_id: int, db: Session):
    record = db.query(Record).filter(Record.id == record_id).first()
    db.delete(record)
    db.commit()