import calendar
import logging
import re
import webbrowser
from datetime import datetime
from typing import Annotated
from urllib.parse import urlsplit, urlunsplit

import pyperclip
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations
from plyer import notification
from pydantic import Field

from .models import DateInfo, UrlOpenResult

logger = logging.getLogger(__name__)

_DAY_NAMES = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)
_DAY_NAMES_SHORT = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
_MONTH_NAMES = (
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
_MONTH_NAMES_SHORT = (
    "",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)

mcp = FastMCP(
    name="MCP System Bridge",
    instructions="This server provides tools for interacting with the local system.",
)


class _InvalidUrl(ValueError):
    """An invalid or unsupported browser URL."""


def _normalize_http_url(url: str) -> str:
    candidate = url.strip()
    if not candidate:
        raise _InvalidUrl("URL must not be empty.")
    if any(
        character.isspace()
        or character == "\\"
        or ord(character) < 32
        or ord(character) == 127
        for character in candidate
    ):
        raise _InvalidUrl(
            "URL must not contain whitespace, backslashes, or control characters."
        )

    if candidate.startswith("//"):
        candidate = f"https:{candidate}"
    elif "://" not in candidate:
        explicit_scheme = re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", candidate)
        host_with_port = re.match(r"^[^/?#]+:\d+(?:[/?#]|$)", candidate)
        if explicit_scheme and not host_with_port:
            raise _InvalidUrl("Only HTTP and HTTPS URLs are supported.")
        candidate = f"https://{candidate}"

    try:
        parsed = urlsplit(candidate)
        port = parsed.port
    except ValueError as error:
        raise _InvalidUrl("URL contains an invalid host or port.") from error

    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"}:
        raise _InvalidUrl("Only HTTP and HTTPS URLs are supported.")
    if parsed.hostname is None:
        raise _InvalidUrl("URL must include a valid host.")
    if port is not None and not 1 <= port <= 65535:
        raise _InvalidUrl("URL contains an invalid port.")

    return urlunsplit(
        (scheme, parsed.netloc, parsed.path, parsed.query, parsed.fragment)
    )


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    )
)
def open_urls(urls: list[str]) -> list[UrlOpenResult]:
    """Open HTTP or HTTPS URLs in the default browser.

    URLs without a scheme are normalized to HTTPS. Results preserve input order
    and duplicates, and a failure for one URL does not abort the remaining URLs.
    """
    results: list[UrlOpenResult] = []
    for requested_url in urls:
        try:
            normalized_url = _normalize_http_url(requested_url)
        except _InvalidUrl as error:
            results.append(
                UrlOpenResult(
                    requested_url=requested_url,
                    normalized_url=None,
                    opened=False,
                    error=str(error),
                )
            )
            continue

        try:
            opened = bool(webbrowser.open(normalized_url))
        except Exception:
            logger.exception("The default browser failed to open %r", normalized_url)
            results.append(
                UrlOpenResult(
                    requested_url=requested_url,
                    normalized_url=normalized_url,
                    opened=False,
                    error="The default browser could not open the URL.",
                )
            )
            continue

        results.append(
            UrlOpenResult(
                requested_url=requested_url,
                normalized_url=normalized_url,
                opened=opened,
                error=None if opened else "The default browser did not accept the URL.",
            )
        )
    return results


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    )
)
def copy_to_clipboard(text: str) -> str:
    """Copy text to the local system clipboard."""
    try:
        pyperclip.copy(text)
    except Exception as error:
        logger.exception("Could not copy text to the system clipboard")
        raise ToolError("Could not copy text to the system clipboard.") from error
    return "Text copied to clipboard successfully."


def _send_system_notification(**notification_params: str | int) -> None:
    notification.notify(**notification_params)


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    )
)
def send_notification(
    title: Annotated[str, Field(min_length=1)],
    message: Annotated[str, Field(min_length=1)],
    app_name: str | None = None,
    timeout: Annotated[int, Field(ge=0)] = 10,
) -> str:
    """Send a native notification through the local operating system."""
    notification_params: dict[str, str | int] = {
        "title": title,
        "message": message,
        "timeout": timeout,
    }
    if app_name:
        notification_params["app_name"] = app_name

    try:
        _send_system_notification(**notification_params)
    except Exception as error:
        logger.exception("Could not send the system notification %r", title)
        raise ToolError("Could not send the system notification.") from error
    return f"Notification sent successfully: '{title}'"


def _local_now() -> datetime:
    return datetime.now().astimezone()


def _format_utc_offset(now: datetime) -> str:
    offset = now.utcoffset()
    total_seconds = int(offset.total_seconds()) if offset is not None else 0
    sign = "+" if total_seconds >= 0 else "-"
    total_minutes = abs(total_seconds) // 60
    hours, minutes = divmod(total_minutes, 60)
    return f"{sign}{hours:02d}:{minutes:02d}"


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    )
)
def get_current_date_info() -> DateInfo:
    """Return detailed information about the current local date and time."""
    now = _local_now()
    current_date = now.date()
    day = current_date.day
    month = current_date.month
    year = current_date.year
    iso_year, week_number, weekday_iso = current_date.isocalendar()

    return DateInfo(
        full_datetime=now.strftime("%Y-%m-%d %H:%M:%S"),
        iso_date=current_date.isoformat(),
        iso_datetime=now.isoformat(),
        timestamp=int(now.timestamp()),
        year=year,
        month=month,
        day=day,
        day_of_year=current_date.timetuple().tm_yday,
        day_of_week_number=current_date.weekday(),
        day_name=_DAY_NAMES[current_date.weekday()],
        day_name_short=_DAY_NAMES_SHORT[current_date.weekday()],
        month_name=_MONTH_NAMES[month],
        month_name_short=_MONTH_NAMES_SHORT[month],
        is_leap_year=calendar.isleap(year),
        week_number=week_number,
        iso_year=iso_year,
        weekday_iso=weekday_iso,
        quarter=(month - 1) // 3 + 1,
        days_in_month=calendar.monthrange(year, month)[1],
        hour=now.hour,
        minute=now.minute,
        second=now.second,
        microsecond=now.microsecond,
        timezone_name=now.tzname(),
        utc_offset=_format_utc_offset(now),
    )


def main() -> None:
    mcp.run(transport="stdio")
