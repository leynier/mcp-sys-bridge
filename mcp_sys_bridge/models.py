from pydantic import BaseModel, ConfigDict


class UrlOpenResult(BaseModel):
    """Result of trying to open one requested URL."""

    model_config = ConfigDict(extra="forbid")

    requested_url: str
    normalized_url: str | None
    opened: bool
    error: str | None


class DateInfo(BaseModel):
    """Date and time information returned by get_current_date_info."""

    model_config = ConfigDict(extra="forbid")

    full_datetime: str
    iso_date: str
    iso_datetime: str
    timestamp: int
    year: int
    month: int
    day: int
    day_of_year: int
    day_of_week_number: int
    day_name: str
    day_name_short: str
    month_name: str
    month_name_short: str
    is_leap_year: bool
    week_number: int
    iso_year: int
    weekday_iso: int
    quarter: int
    days_in_month: int
    hour: int
    minute: int
    second: int
    microsecond: int
    timezone_name: str | None
    utc_offset: str
