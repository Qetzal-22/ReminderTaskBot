from sqlalchemy.orm import Session

from app.db import crud

def verify_user_in_db(tg_id: int, db: Session):
    users = crud.get_users(db)
    for user in users:
        if user.tg_id == tg_id:
            return True
    return False

def verify_time(time: str):
    MAX_MINUTS = 59
    MAX_HOURS = 23
    MIN_TIME = 0
    if time.count(":") != 1:
        return False
    h, m = time.split(":")
    if not (h.isdigit() and m.isdigit()):
        return False

    h, m = int(h), int(m)
    if h > MAX_HOURS or m > MAX_MINUTS:
        return False

    if h < MIN_TIME or m < MIN_TIME:
        return False

    return True

def verify_repetition(repetition: str):
    if not repetition.isdigit():
        return False
    return True
