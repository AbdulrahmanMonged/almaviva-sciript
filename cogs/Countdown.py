from datetime import datetime, timedelta


class Countdown:
    def __init__(self, det_h=0, det_min=0) -> None:
        self.det_h: int = det_h
        self.det_min: int = det_min

    def get_remaining_time(self):
        current_date = datetime.now()
        next_date = current_date.replace(
            hour=self.det_h, minute=self.det_min, second=0
        ) - (current_date + timedelta(days=1))
        hours, remainder = divmod(next_date.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return (hours, minutes, seconds)

    def time_to_start_program(self):
        current_date = datetime.now()
        next_date = current_date.replace(
            hour=self.det_h, minute=self.det_min, second=0
        ) - (current_date + timedelta(days=1))
        return next_date.seconds * 1000

    def get_days_in_month(self):
        current_day = datetime.now()
        next_month = current_day.replace(month=current_day.month + 1)
        return list(
            map(str, range(current_day.day, (next_month - current_day).days + 1))
        )
