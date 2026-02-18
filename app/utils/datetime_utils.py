from datetime import datetime, timedelta
from app.db.models import Record
from math import ceil

def get_week_days() -> dict:
    today = datetime.today()
    monday = today - timedelta(days=today.weekday())
    week_days = {
        "0": today,
        "1": today,
        "2": today,
        "3": today,
        "4": today,
        "5": today,
        "6": today
    }
    for name, day in zip(week_days, range(7)):
        week_days[name] = (monday + timedelta(days=day)).replace(second=0, microsecond=0)

    return week_days

def calc_next_reminder_week(now: datetime, record: Record) -> datetime:
    day_week = record.day_week.split(",")
    now_week = get_week_days()
    for day in day_week:
        if now_week[day] > now:
            next_reminder = now_week[day]
            return next_reminder

    if record.next_reminder <= now:
        next_reminder = now_week[day_week[0]] + timedelta(days=7)  # если не нашли дату на этой недели то берем первую дату следующей
        return next_reminder

def calc_next_reminder_interval(now: datetime, record: Record) -> datetime:
    now = now + timedelta(seconds=1)
    lost_reminder = (now - record.next_reminder).total_seconds() / 3600
    count_repetition = ceil(lost_reminder / record.repetition)
    new_next_reminder = record.next_reminder + timedelta(hours=record.repetition*count_repetition)
    return new_next_reminder

