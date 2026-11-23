from dataclasses import dataclass
from datetime import timedelta

from backend.models.timeframe import Timeframe


@dataclass(frozen=True)
class UpdateSchedule:
    interval: timedelta
    cron: dict


UPDATE_SCHEDULE: dict[Timeframe, UpdateSchedule] = {
    Timeframe.H1: UpdateSchedule(timedelta(hours=1), {"minute": 1}),
    Timeframe.H4: UpdateSchedule(timedelta(hours=4), {"hour": "*/4", "minute": 1}),
    Timeframe.M30: UpdateSchedule(timedelta(minutes=30), {"minute": "1,31"}),
    Timeframe.M15: UpdateSchedule(timedelta(minutes=15), {"minute": "1,16,31,46"}),
    Timeframe.D1: UpdateSchedule(timedelta(days=1), {"hour": 0, "minute": 1}),
}