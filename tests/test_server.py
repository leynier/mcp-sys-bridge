import asyncio
import runpy
from datetime import UTC, datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from mcp_sys_bridge import server


def _assert_schema_has_only_boolean_additional_properties(value: Any) -> None:
    if isinstance(value, dict):
        if "additionalProperties" in value:
            assert isinstance(value["additionalProperties"], bool)
        for nested in value.values():
            _assert_schema_has_only_boolean_additional_properties(nested)
    elif isinstance(value, list):
        for nested in value:
            _assert_schema_has_only_boolean_additional_properties(nested)


def test_open_urls_normalizes_urls_and_preserves_duplicates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened_urls: list[str] = []

    def open_browser(url: str) -> bool:
        opened_urls.append(url)
        return True

    monkeypatch.setattr(server.webbrowser, "open", open_browser)
    requested_urls = [
        "example.com:8080/path",
        "//example.org/docs",
        "HTTPS://example.net/path?q=1",
        "https://example.net",
        "https://example.net",
    ]

    results = server.open_urls(requested_urls)

    assert opened_urls == [
        "https://example.com:8080/path",
        "https://example.org/docs",
        "https://example.net/path?q=1",
        "https://example.net",
        "https://example.net",
    ]
    assert [result.requested_url for result in results] == requested_urls
    assert all(result.opened and result.error is None for result in results)


@pytest.mark.parametrize(
    ("url", "message"),
    [
        ("", "must not be empty"),
        ("not a url", "must not contain whitespace"),
        ("ftp://example.com", "Only HTTP and HTTPS"),
        ("mailto:user@example.com", "Only HTTP and HTTPS"),
        ("https://", "valid host"),
        ("https://example.com:99999", "invalid host or port"),
        ("https://example.com:0", "invalid port"),
        ("https://exa\nmple.com", "whitespace"),
        ("https://example.com\\@evil.test", "backslashes"),
    ],
)
def test_open_urls_rejects_invalid_or_unsupported_urls(
    monkeypatch: pytest.MonkeyPatch, url: str, message: str
) -> None:
    monkeypatch.setattr(
        server.webbrowser,
        "open",
        lambda _url: pytest.fail("Invalid URLs must not reach the browser"),
    )

    result = server.open_urls([url])[0]

    assert result.requested_url == url
    assert result.normalized_url is None
    assert result.opened is False
    assert message in result.error


def test_open_urls_reports_browser_refusal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server.webbrowser, "open", lambda _url: False)

    result = server.open_urls(["example.com"])[0]

    assert result.normalized_url == "https://example.com"
    assert result.opened is False
    assert result.error == "The default browser did not accept the URL."


def test_open_urls_isolates_browser_exceptions(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_to_open(_url: str) -> bool:
        raise RuntimeError("provider details")

    monkeypatch.setattr(server.webbrowser, "open", fail_to_open)

    result = server.open_urls(["example.com"])[0]

    assert result.normalized_url == "https://example.com"
    assert result.opened is False
    assert result.error == "The default browser could not open the URL."


def test_copy_to_clipboard_success(monkeypatch: pytest.MonkeyPatch) -> None:
    copied: list[str] = []
    monkeypatch.setattr(server.pyperclip, "copy", copied.append)

    result = server.copy_to_clipboard("hello")

    assert copied == ["hello"]
    assert result == "Text copied to clipboard successfully."


def test_copy_to_clipboard_raises_tool_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_to_copy(_text: str) -> None:
        raise RuntimeError("provider details")

    monkeypatch.setattr(server.pyperclip, "copy", fail_to_copy)

    with pytest.raises(ToolError, match="Could not copy text"):
        server.copy_to_clipboard("hello")


def test_send_notification_success(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(
        server, "_send_system_notification", lambda **kwargs: calls.append(kwargs)
    )

    result = server.send_notification(
        "Build complete", "Everything passed", app_name="CI", timeout=4
    )

    assert calls == [
        {
            "title": "Build complete",
            "message": "Everything passed",
            "timeout": 4,
            "app_name": "CI",
        }
    ]
    assert result == "Notification sent successfully: 'Build complete'"


def test_system_notification_adapter(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, str | int]] = []
    fake_notification = SimpleNamespace(notify=lambda **kwargs: calls.append(kwargs))
    monkeypatch.setattr(server, "notification", fake_notification)

    server._send_system_notification(title="Title", message="Message", timeout=3)

    assert calls == [{"title": "Title", "message": "Message", "timeout": 3}]


def test_send_notification_raises_tool_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_to_notify(**_kwargs: Any) -> None:
        raise RuntimeError("provider details")

    monkeypatch.setattr(server, "_send_system_notification", fail_to_notify)

    with pytest.raises(ToolError, match="Could not send the system notification"):
        server.send_notification("Title", "Message")


def test_get_current_date_info_is_timezone_aware_and_deterministic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_time = datetime(
        2021,
        1,
        1,
        23,
        59,
        58,
        123456,
        tzinfo=timezone(timedelta(hours=-6), "CST"),
    )
    monkeypatch.setattr(server, "_local_now", lambda: current_time)

    result = server.get_current_date_info()

    assert result.iso_datetime == "2021-01-01T23:59:58.123456-06:00"
    assert result.iso_year == 2020
    assert result.week_number == 53
    assert result.day_name == "Friday"
    assert result.day_name_short == "Fri"
    assert result.month_name == "January"
    assert result.month_name_short == "Jan"
    assert result.quarter == 1
    assert result.days_in_month == 31
    assert result.timezone_name == "CST"
    assert result.utc_offset == "-06:00"


def test_format_utc_offset_supports_positive_and_missing_offsets() -> None:
    positive = datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    naive = datetime(2026, 1, 1, tzinfo=UTC).replace(tzinfo=None)

    assert server._format_utc_offset(positive) == "+05:30"
    assert server._format_utc_offset(naive) == "+00:00"


def test_mcp_contract_and_schemas(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_to_copy(_text: str) -> None:
        raise RuntimeError("private provider details")

    monkeypatch.setattr(server.pyperclip, "copy", fail_to_copy)

    async def inspect_server() -> None:
        async with Client(server.mcp) as client:
            tools = {tool.name: tool for tool in await client.list_tools()}

            assert set(tools) == {
                "open_urls",
                "copy_to_clipboard",
                "send_notification",
                "get_current_date_info",
            }
            assert tools["open_urls"].annotations.readOnlyHint is False
            assert tools["open_urls"].annotations.openWorldHint is True
            assert tools["copy_to_clipboard"].annotations.destructiveHint is True
            assert tools["copy_to_clipboard"].annotations.idempotentHint is True
            assert tools["send_notification"].annotations.readOnlyHint is False
            assert tools["send_notification"].annotations.openWorldHint is False
            assert tools["get_current_date_info"].annotations.readOnlyHint is True
            assert tools["get_current_date_info"].annotations.openWorldHint is False

            url_schema = tools["open_urls"].outputSchema
            _assert_schema_has_only_boolean_additional_properties(url_schema)
            assert url_schema["properties"]["result"]["type"] == "array"

            notification_schema = tools["send_notification"].inputSchema
            assert notification_schema["properties"]["title"]["minLength"] == 1
            assert notification_schema["properties"]["timeout"]["minimum"] == 0

            date_result = await client.call_tool("get_current_date_info", {})
            assert date_result.is_error is False
            assert date_result.data.iso_datetime.endswith(
                server._format_utc_offset(
                    datetime.fromisoformat(date_result.data.iso_datetime)
                )
            )

            clipboard_result = await client.call_tool(
                "copy_to_clipboard", {"text": "hello"}, raise_on_error=False
            )
            clipboard_error = " ".join(
                content.text for content in clipboard_result.content
            )
            assert clipboard_result.is_error is True
            assert "Could not copy text" in clipboard_error
            assert "private provider details" not in clipboard_error

    asyncio.run(inspect_server())


def test_main_runs_stdio_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    transports: list[str] = []
    monkeypatch.setattr(
        server.mcp, "run", lambda transport: transports.append(transport)
    )

    server.main()

    assert transports == ["stdio"]


def test_package_module_entrypoint(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(server, "main", lambda: calls.append("main"))

    runpy.run_module("mcp_sys_bridge.__main__", run_name="mcp_sys_bridge.not_main")
    assert calls == []

    runpy.run_module("mcp_sys_bridge.__main__", run_name="__main__")
    assert calls == ["main"]
