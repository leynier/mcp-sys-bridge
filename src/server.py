import calendar
import webbrowser
from datetime import datetime
from urllib.parse import urlparse, urlunparse

import pyperclip
from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from plyer import notification

from .models import DateInfo

mcp = FastMCP(
    name="MCP System Bridge",
    instructions="This server provides tools for managing the system.",
)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def open_urls(urls: list[str]) -> dict[str, str]:
    """
    Open a list of URLs in the default browser.
    """
    results = {}
    for url in urls:
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            parsed_url = urlparse(f"https://{url}")
        if not parsed_url.netloc:
            results[url] = "Error: Invalid URL. Please provide a valid URL."
            continue
        processed_url = urlunparse(parsed_url)
        try:
            webbrowser.open(processed_url)
            results[url] = "URL opened successfully."
        except Exception as e:
            results[url] = f"Error opening URL: {e}"
    return results


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def copy_to_clipboard(text: str) -> str:
    """
    Copy text to the clipboard.
    """
    try:
        pyperclip.copy(text)
        return "Text copied to clipboard successfully."
    except Exception as e:
        return f"Error copying text to clipboard: {e}"


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def send_notification(
    title: str,
    message: str,
    app_name: str | None = None,
    timeout: int = 10,
) -> str:
    """
    Send a system notification.

    Displays a native operating system notification with the specified title and message.
    Works across Windows, macOS, and Linux platforms.

    Args:
        title: The title of the notification (required)
        message: The message body of the notification (required)
        app_name: The name of the application sending the notification (optional)
        timeout: Duration in seconds to display the notification (default: 10)

    Returns:
        A success message if the notification was sent successfully, or an error message if it failed.

    Examples:
        send_notification("Task Complete", "Your build has finished successfully")
        send_notification("Warning", "Low disk space detected", app_name="System Monitor", timeout=5)
    """
    try:
        notification_params = {
            "title": title,
            "message": message,
            "timeout": timeout,
        }

        if app_name:
            notification_params["app_name"] = app_name

        notification.notify(**notification_params)
        return f"Notification sent successfully: '{title}'"
    except Exception as e:
        return f"Error sending notification: {e}"


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def get_current_date_info() -> DateInfo:
    """
    Get comprehensive information about the current date.

    Returns:
        DateInfo: A dictionary containing comprehensive date and time information:
            - full_datetime (str): Full date and time in YYYY-MM-DD HH:MM:SS format
            - iso_date (str): ISO 8601 date format (YYYY-MM-DD)
            - iso_datetime (str): ISO 8601 datetime format with timezone
            - timestamp (int): Unix timestamp (seconds since epoch)
            - year (int): Current year (e.g., 2024)
            - month (int): Current month (1-12)
            - day (int): Current day of the month (1-31)
            - day_of_year (int): Day number in the year (1-366)
            - day_of_week_number (int): Day of the week (0=Monday, 6=Sunday)
            - day_name (str): Full name of the day (e.g., "Monday")
            - day_name_short (str): Short name of the day (e.g., "Mon")
            - month_name (str): Full name of the month (e.g., "January")
            - month_name_short (str): Short name of the month (e.g., "Jan")
            - is_leap_year (bool): True if current year is a leap year
            - week_number (int): ISO 8601 week number (1-53)
            - iso_year (int): ISO 8601 year (may differ from calendar year)
            - weekday_iso (int): ISO weekday (1=Monday, 7=Sunday)
            - quarter (int): Quarter of the year (1-4)
            - days_in_month (int): Total days in the current month
            - hour (int): Current hour (0-23)
            - minute (int): Current minute (0-59)
            - second (int): Current second (0-59)
            - microsecond (int): Current microsecond (0-999999)
    """
    now = datetime.now()
    current_date = now.date()

    # Basic date information
    day = current_date.day
    month = current_date.month
    year = current_date.year

    # Day of the year (1-366)
    day_of_year = current_date.timetuple().tm_yday

    # Day of the week (0=Monday, 6=Sunday)
    day_of_week_number = current_date.weekday()

    # Day names
    day_name_english = current_date.strftime("%A")
    day_name_short_english = current_date.strftime("%a")

    # Month names
    month_name_english = current_date.strftime("%B")
    month_name_short_english = current_date.strftime("%b")

    # Check if leap year
    is_leap_year = calendar.isleap(year)

    # Week number (ISO 8601)
    year_iso, week_number, weekday_iso = current_date.isocalendar()

    # Days in current month
    days_in_month = calendar.monthrange(year, month)[1]

    # Quarter
    quarter = (month - 1) // 3 + 1

    # Full datetime string
    full_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

    # ISO format
    iso_date = current_date.isoformat()
    iso_datetime = now.isoformat()

    # Timestamp
    timestamp = int(now.timestamp())

    return DateInfo(
        full_datetime=full_datetime,
        iso_date=iso_date,
        iso_datetime=iso_datetime,
        timestamp=timestamp,
        year=year,
        month=month,
        day=day,
        day_of_year=day_of_year,
        day_of_week_number=day_of_week_number,
        day_name=day_name_english,
        day_name_short=day_name_short_english,
        month_name=month_name_english,
        month_name_short=month_name_short_english,
        is_leap_year=is_leap_year,
        week_number=week_number,
        iso_year=year_iso,
        weekday_iso=weekday_iso,
        quarter=quarter,
        days_in_month=days_in_month,
        hour=now.hour,
        minute=now.minute,
        second=now.second,
        microsecond=now.microsecond,
    )


def main() -> None:
    mcp.run(transport="stdio")
