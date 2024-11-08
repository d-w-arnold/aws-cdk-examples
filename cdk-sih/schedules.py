#!/usr/bin/env python3.9
from datetime import datetime

from pytz import timezone


class Schedules:
    _SEP_COLON_: str = ":"
    _SEP_SCORE_: str = "-"
    _SEP_UNDER_: str = "_"

    _DAY_: str = "day"
    _DAYS_: str = f"{_DAY_}s"
    _END_: str = "end"
    _START_: str = "start"
    _WEEK_: str = "week"
    _ZERO_HOUR: str = "00"

    _WEEK_DAY_FRIDAY_: str = "FRI"
    _WEEK_DAY_MONDAY_: str = "MON"
    _WEEK_DAY_SATURDAY_: str = "SAT"
    _WEEK_DAY_SUNDAY_: str = "SUN"
    _WEEK_DAY_THURSDAY_: str = "THU"
    _WEEK_DAY_TUESDAY_: str = "TUE"

    _DAY_AFTER_: str = _WEEK_DAY_TUESDAY_
    _DAY_BEFORE_: str = _WEEK_DAY_SUNDAY_
    _DAY_DEFAULT_: str = _WEEK_DAY_MONDAY_

    _ALL_DAYS_: str = _SEP_SCORE_.join([_WEEK_DAY_MONDAY_, _WEEK_DAY_SUNDAY_])
    _END_DAY_: str = _SEP_UNDER_.join([_END_, _DAY_])
    _END_WEEK_DAYS_: str = _SEP_UNDER_.join([_END_, _WEEK_, _DAYS_])
    _START_DAY_: str = _SEP_UNDER_.join([_START_, _DAY_])
    _START_END_: str = _SEP_UNDER_.join([_START_, _END_])
    _START_END_DAY_: str = _SEP_UNDER_.join([_START_, _END_, _DAY_])
    _START_END_WEEK_DAYS_: str = _SEP_UNDER_.join([_START_, _END_, _WEEK_, _DAYS_])
    _START_WEEK_DAYS_: str = _SEP_UNDER_.join([_START_, _WEEK_, _DAYS_])
    _WEEKEND_DAYS_AFTER_: str = _SEP_SCORE_.join([_WEEK_DAY_SUNDAY_, _WEEK_DAY_MONDAY_])
    _WEEKEND_DAYS_BEFORE_: str = _SEP_SCORE_.join([_WEEK_DAY_FRIDAY_, _WEEK_DAY_SATURDAY_])
    _WEEKEND_DAYS_DEFAULT_: str = _SEP_SCORE_.join([_WEEK_DAY_SATURDAY_, _WEEK_DAY_SUNDAY_])
    _WEEK_DAYS_AFTER_: str = _SEP_SCORE_.join([_WEEK_DAY_TUESDAY_, _WEEK_DAY_SATURDAY_])
    _WEEK_DAYS_BEFORE_: str = _SEP_SCORE_.join([_WEEK_DAY_SUNDAY_, _WEEK_DAY_THURSDAY_])
    _WEEK_DAYS_DEFAULT_: str = _SEP_SCORE_.join([_WEEK_DAY_MONDAY_, _WEEK_DAY_FRIDAY_])

    def __init__(self, region_tz: str) -> None:
        self.utc_offset: str = datetime.now(timezone(region_tz)).strftime("%z")[:3]
        self.pos_neg_offset: str = self.utc_offset[0]
        self.hours_offset: int = int(self.utc_offset[1:])

        # Working day operational hours

        window_ec2_ecs_values: dict[str, dict[str, int]] = {
            self._START_: 8,  # UTC hours
            self._START_WEEK_DAYS_: self._WEEK_DAYS_DEFAULT_,
            self._END_: 19,  # UTC hours
            self._END_WEEK_DAYS_: self._WEEK_DAYS_DEFAULT_,
        }
        self.window_ec2_ecs_week_days: dict[str, dict[str, int]] = self.offset_adjust(dict(window_ec2_ecs_values))
        self.window_ec2_ecs_all_days: dict[str, dict[str, int]] = self.convert_week_days_to(
            self._ALL_DAYS_, self.window_ec2_ecs_week_days
        )

        window_ec_rds_values: dict[str, dict[str, int]] = {
            self._START_: 7,  # UTC hours
            self._START_WEEK_DAYS_: self._WEEK_DAYS_DEFAULT_,
            self._END_: 20,  # UTC hours
            self._END_WEEK_DAYS_: self._WEEK_DAYS_DEFAULT_,
        }
        self.window_ec_rds_week_days: dict[str, dict[str, int]] = self.offset_adjust(dict(window_ec_rds_values))
        self.window_ec_rds_all_days: dict[str, dict[str, int]] = self.convert_week_days_to(
            self._ALL_DAYS_, self.window_ec_rds_week_days
        )
        self.window_ec_rds_weekend: dict[str, dict[str, int]] = self.offset_adjust(
            self.convert_week_days_to(self._WEEKEND_DAYS_DEFAULT_, dict(window_ec_rds_values)), weekend=True
        )

        self.window_vpn: dict[str, dict[str, int]] = self.window_ec_rds_week_days
        self.window_proxy: dict[str, dict[str, int]] = self.window_ec_rds_week_days
        self.window_pypi: dict[str, dict[str, int]] = self.window_ec_rds_week_days

        # Daily backup windows

        window_ec_redis_daily_backup_values: dict[str, dict[str, int]] = {
            self._START_: 1,  # UTC hours
            self._START_WEEK_DAYS_: self._WEEK_DAYS_DEFAULT_,
            self._END_: 2,  # UTC hours
            self._END_WEEK_DAYS_: self._WEEK_DAYS_DEFAULT_,
        }
        self.window_ec_redis_daily_backup_week_days: dict[str, dict[str, int]] = self.offset_adjust(
            dict(window_ec_redis_daily_backup_values)
        )

        self.window_ec_redis_daily_backup_all_days_timestamp: str = self.get_daily_backup_timestamp(
            self.window_ec_redis_daily_backup_week_days
        )

        window_rds_mysql_daily_backup_values: dict[str, dict[str, int]] = {
            self._START_: 22,  # UTC hours - start of window to start backup
            self._START_WEEK_DAYS_: self._WEEK_DAYS_DEFAULT_,
            self._END_: 2,
            # UTC hours - when to turn off the RDS database instance, presuming the backup to have completed
            self._END_WEEK_DAYS_: self._WEEK_DAYS_AFTER_,
        }
        self.window_rds_mysql_daily_backup_week_days: dict[str, dict[str, int]] = self.offset_adjust(
            dict(window_rds_mysql_daily_backup_values), backup_start_window=1
        )
        self.window_rds_mysql_daily_backup_all_days: dict[str, dict[str, int]] = self.convert_week_days_to(
            self._ALL_DAYS_, self.window_rds_mysql_daily_backup_week_days
        )
        self.window_rds_mysql_daily_backup_weekend: dict[str, dict[str, int]] = self.offset_adjust(
            self.convert_week_days_to(self._WEEKEND_DAYS_DEFAULT_, dict(window_rds_mysql_daily_backup_values)),
            weekend=True,
            backup_start_window=1,
        )

        self.window_rds_mysql_daily_backup_all_days_timestamp: str = self.get_daily_backup_timestamp(
            self.window_rds_mysql_daily_backup_all_days
        )
        self.window_rds_mysql_daily_backup_week_days_timestamp: str = self.get_daily_backup_timestamp(
            self.window_rds_mysql_daily_backup_week_days
        )
        self.window_rds_mysql_daily_backup_weekend_timestamp: str = self.get_daily_backup_timestamp(
            self.window_rds_mysql_daily_backup_weekend
        )

        # Weekly maintenance windows

        window_ec_redis_weekly_maintenance_values: dict[str, dict[str, int]] = {
            self._START_: 2,  # UTC hours
            self._START_DAY_: self._DAY_DEFAULT_,
            self._END_: 4,  # UTC hours
            self._END_DAY_: self._DAY_DEFAULT_,
        }
        self.window_ec_redis_weekly_maintenance: dict[str, dict[str, int]] = self.offset_adjust(
            dict(window_ec_redis_weekly_maintenance_values), weekly=True
        )
        self.window_ec_redis_weekly_maintenance_timestamp: str = self.get_weekly_maintenance_timestamp(
            self.window_ec_redis_weekly_maintenance
        )

        window_rds_mysql_weekly_maintenance_values: dict[str, dict[str, int]] = {
            self._START_: 4,  # UTC hours
            self._START_DAY_: self._DAY_DEFAULT_,
            self._END_: 6,  # UTC hours
            self._END_DAY_: self._DAY_DEFAULT_,
        }
        self.window_rds_mysql_weekly_maintenance: dict[str, dict[str, int]] = self.offset_adjust(
            dict(window_rds_mysql_weekly_maintenance_values), weekly=True
        )
        self.window_rds_mysql_weekly_maintenance_timestamp: str = self.get_weekly_maintenance_timestamp(
            self.window_rds_mysql_weekly_maintenance
        )

    def offset_adjust(
        self,
        window_props: dict[str, dict[str, int]],
        weekend: bool = False,
        weekly: bool = False,
        backup_start_window: int = None,
    ) -> dict[str, dict[str, int]]:
        if self.pos_neg_offset == "+" and self.hours_offset > 0:
            self.offset_pos_adjust_helper(
                window_props, self._START_, self._START_DAY_ if weekly else self._START_WEEK_DAYS_, weekend
            )
            self.offset_pos_adjust_helper(
                window_props, self._END_, self._END_DAY_ if weekly else self._END_WEEK_DAYS_, weekend
            )
        elif self.pos_neg_offset == self._SEP_SCORE_:
            self.offset_neg_adjust_helper(
                window_props, self._START_, self._START_DAY_ if weekly else self._START_WEEK_DAYS_, weekend
            )
            self.offset_neg_adjust_helper(
                window_props, self._END_, self._END_DAY_ if weekly else self._END_WEEK_DAYS_, weekend
            )
        if backup_start_window:
            window_props[self._START_END_] = window_props[self._START_] + backup_start_window
            if window_props[self._START_END_] >= 24:
                window_props[self._START_END_] = window_props[self._START_END_] % 24
                start_day_key = self._START_DAY_ if weekly else self._START_WEEK_DAYS_
                start_end_day_key = self._START_END_DAY_ if weekly else self._START_END_WEEK_DAYS_
                if window_props[start_day_key] == self._DAY_BEFORE_:
                    window_props[start_end_day_key] = self._DAY_DEFAULT_
                elif window_props[start_day_key] == self._DAY_DEFAULT_:
                    window_props[start_end_day_key] = self._DAY_AFTER_
        return window_props

    def offset_pos_adjust_helper(
        self, window_props: dict[str, dict[str, int]], hour_key: str, day_key: str, weekend: bool
    ) -> None:
        if window_props[hour_key] < self.hours_offset:
            window_props[hour_key] = 24 - abs(window_props[hour_key] - self.hours_offset)
            self.set_window_props(window_props, day_key, pos=True, weekend=weekend)
        else:
            window_props[hour_key] = window_props[hour_key] - self.hours_offset

    def offset_neg_adjust_helper(
        self, window_props: dict[str, dict[str, int]], hour_key: str, day_key: str, weekend: bool
    ) -> None:
        if window_props[hour_key] + self.hours_offset >= 24:
            window_props[hour_key] = (window_props[hour_key] + self.hours_offset) % 24
            self.set_window_props(window_props, day_key, pos=False, weekend=weekend)
        else:
            window_props[hour_key] = window_props[hour_key] + self.hours_offset

    def get_daily_backup_timestamp(self, window: dict[str, dict[str, int]]) -> str:
        return self._SEP_SCORE_.join(
            [
                self._SEP_COLON_.join([str(window[i]).zfill(2), self._ZERO_HOUR])
                for i in [self._START_, self._START_END_ if self._START_END_ in window else self._END_]
            ]
        )

    def get_hours(self, start_hour: int, end_hour: int) -> list[int]:
        window_hours: list[str] = []
        window: dict[str, dict[str, int]] = self.offset_adjust(
            {self._START_: start_hour, self._END_: end_hour}  # UTC hours
        )
        if window[self._START_] > window[self._END_]:
            window_hours = [str(i) for i in range(window[self._START_], 24)] + [
                str(i) for i in range(0, window[self._END_] + 1)
            ]
        elif window[self._START_] < window[self._END_]:
            window_hours = [str(i) for i in range(window[self._START_], window[self._END_] + 1)]
        return window_hours

    def get_weekly_maintenance_timestamp(self, window: dict[str, dict[str, int]]) -> str:
        return self._SEP_SCORE_.join(
            [
                self._SEP_COLON_.join([str(window[k]).lower(), str(window[v]).zfill(2), self._ZERO_HOUR])
                for k, v in {self._START_DAY_: self._START_, self._END_DAY_: self._END_}.items()
            ]
        )

    def set_window_props(self, window_props: dict[str, dict[str, int]], day_key: str, pos: bool, weekend: bool):
        if self._SEP_SCORE_ in window_props[day_key]:
            days_before: str = self._WEEKEND_DAYS_BEFORE_ if weekend else self._WEEK_DAYS_BEFORE_
            days_default: str = self._WEEKEND_DAYS_DEFAULT_ if weekend else self._WEEK_DAYS_DEFAULT_
            days_after: str = self._WEEKEND_DAYS_AFTER_ if weekend else self._WEEK_DAYS_AFTER_
            if window_props[day_key] == days_default:
                window_props[day_key] = days_before if pos else days_after
            elif window_props[day_key] == (days_after if pos else days_before):
                window_props[day_key] = days_default
        else:
            if window_props[day_key] == self._DAY_DEFAULT_:
                window_props[day_key] = self._DAY_BEFORE_ if pos else self._DAY_AFTER_
            elif window_props[day_key] == (self._DAY_AFTER_ if pos else self._DAY_BEFORE_):
                window_props[day_key] = self._DAY_DEFAULT_

    def convert_week_days_to(self, days: str, window: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
        is_all_days: bool = False
        days_map: dict[str, str] = {}
        if days == self._WEEK_DAYS_DEFAULT_:
            return window
        if days == self._ALL_DAYS_:
            is_all_days = True
        else:
            days_map = {
                self._WEEK_DAYS_BEFORE_: self._WEEKEND_DAYS_BEFORE_,
                self._WEEK_DAYS_DEFAULT_: self._WEEKEND_DAYS_DEFAULT_,
                self._WEEK_DAYS_AFTER_: self._WEEKEND_DAYS_AFTER_,
            }
        return {
            k: v if k not in {self._START_WEEK_DAYS_, self._END_WEEK_DAYS_} else (days if is_all_days else days_map[v])
            for k, v in window.items()
        }
