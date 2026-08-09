# MCP System Bridge

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/pypi/v/mcp-sys-bridge?color=%2334D058&label=Version)](https://pypi.org/project/mcp-sys-bridge)
[![Tests](https://github.com/leynier/mcp-sys-bridge/actions/workflows/tests.yml/badge.svg)](https://github.com/leynier/mcp-sys-bridge/actions/workflows/tests.yml)

`mcp-sys-bridge` is a local [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that lets MCP clients open web URLs, copy text to the clipboard, send native notifications, and inspect the local date and time.

## Installation

The server requires Python 3.12 or newer and runs directly with [`uvx`](https://docs.astral.sh/uv/getting-started/installation/). Add it to your MCP client configuration:

```json
{
  "mcpServers": {
    "mcp-sys-bridge": {
      "command": "uvx",
      "args": ["mcp-sys-bridge"]
    }
  }
}
```

It can also be started manually:

```bash
uvx mcp-sys-bridge
```

For a local checkout, use either entry point after `uv sync`:

```bash
uv run mcp-sys-bridge
uv run python -m mcp_sys_bridge
```

## Available tools

### `open_urls`

Opens HTTP or HTTPS URLs in the default browser. URLs without a scheme use HTTPS. Other schemes are rejected so an MCP client cannot accidentally invoke arbitrary protocol handlers.

The tool preserves input order and duplicates. Each requested URL receives its own result:

```json
[
  {
    "requested_url": "example.com:8080/docs",
    "normalized_url": "https://example.com:8080/docs",
    "opened": true,
    "error": null
  }
]
```

An invalid URL or browser failure does not stop the rest of the batch.

### `copy_to_clipboard`

Copies the provided text to the local clipboard. This replaces the current clipboard contents. Provider failures are returned to the client as MCP tool errors.

### `send_notification`

Sends a local system notification with a title, message, optional application name, and a non-negative timeout. Provider failures are returned as MCP tool errors. Some operating systems may ignore the requested timeout.

### `get_current_date_info`

Returns local calendar and clock fields, including ISO calendar values, English day and month names, timezone name, and UTC offset. `iso_datetime` is timezone-aware, for example `2026-08-08T20:30:00-06:00`.

## Platform notes

- Windows and macOS normally provide the required browser, clipboard, and notification integrations.
- Linux requires an active graphical session and compatible system providers. Clipboard support may require `wl-clipboard`, `xclip`, or `xsel`, depending on the session; desktop notifications typically require a working notification service and D-Bus integration.
- Clipboard and notification tools are expected to fail cleanly in headless sessions where those providers are unavailable.
- MCP annotations identify URL opening, clipboard writes, and notifications as side effects so compatible clients can apply their normal confirmation policy.

## Development

```bash
make tests   # Ruff plus tests with 100% line and branch coverage
make audit   # Audit the locked environment for known vulnerabilities
make build   # Build the wheel and source distribution
```

Tests mock browser, clipboard, and notification calls; they do not modify the developer's desktop state.

## Changelog

### 0.2.0

- Changed `open_urls` to return ordered structured results and restricted it to HTTP/HTTPS.
- Corrected MCP side-effect annotations and MCP error reporting.
- Made date-time output timezone-aware and added timezone metadata.
- Renamed the import package from `src` to `mcp_sys_bridge`.
- Added functional tests, dependency auditing, cross-platform CI, and OIDC-based publishing.

`src.*` imports and the dictionary result previously returned by `open_urls` are not compatible with 0.2.0. The documented `mcp-sys-bridge` command remains unchanged.

### 0.1.5

- Added the cross-platform `send_notification` tool.

### 0.1.4

- Added tool annotations.

### 0.1.3

- Added `get_current_date_info`.

### 0.1.2

- Changed `open_url` to `open_urls` for batch URL opening.

### 0.1.0

- Added URL opening and clipboard support.

## License

MIT License. See [`license`](license).
