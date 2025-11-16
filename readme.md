# MCP System Bridge

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/pypi/v/mcp-sys-bridge?color=%2334D058&label=Version)](https://pypi.org/project/mcp-sys-bridge)
[![Last commit](https://img.shields.io/github/last-commit/leynier/mcp-sys-bridge.svg?style=flat)](https://github.com/leynier/mcp-sys-bridge/commits)
[![Commit activity](https://img.shields.io/github/commit-activity/m/leynier/mcp-sys-bridge)](https://github.com/leynier/mcp-sys-bridge/commits)
[![Stars](https://img.shields.io/github/stars/leynier/mcp-sys-bridge?style=flat&logo=github)](https://github.com/leynier/mcp-sys-bridge/stargazers)
[![Forks](https://img.shields.io/github/forks/leynier/mcp-sys-bridge?style=flat&logo=github)](https://github.com/leynier/mcp-sys-bridge/network/members)
[![Watchers](https://img.shields.io/github/watchers/leynier/mcp-sys-bridge?style=flat&logo=github)](https://github.com/leynier/mcp-sys-bridge)
[![Contributors](https://img.shields.io/github/contributors/leynier/mcp-sys-bridge)](https://github.com/leynier/mcp-sys-bridge/graphs/contributors)

A bridge implementation of the **Model Context Protocol (MCP)** that exposes native operating system features such as clipboard management, URL handling and date information retrieval.

---

## Table of Contents

* [Overview](#overview)
* [Key Features](#key-features)
* [Installation](#installation)
* [Quick Start](#quick-start)
* [Available Tools](#available-tools)
* [Changelog](#changelog)
* [License](#license)

---

## Overview

`mcp-sys-bridge` provides a minimal set of tools for MCP compatible clients, allowing them to interact with the underlying OS in a safe manner.

---

## Key Features

* 🚀 **URL Opening** — open one or multiple URLs in the default browser.
* 📋 **Clipboard Support** — copy text directly to the clipboard.
* 🔔 **System Notifications** — send native OS notifications (Windows, macOS, Linux).
* 📆 **Date Info** — retrieve detailed information about the current date and time.

---

## Installation

`mcp-sys-bridge` runs directly with [uvx](https://docs.astral.sh/uv/getting-started/installation);
no package installation is required. Add the server to your MCP configuration:

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

Ensure `uv` is installed following the [uv documentation](https://docs.astral.sh/uv/getting-started/installation).

---

## Quick Start

Start the bridge manually:

```bash
uvx mcp-sys-bridge
```

---

## Available Tools

- `open_urls` — open a list of URLs in the default browser.
- `copy_to_clipboard` — copy text to the clipboard.
- `send_notification` — send a native system notification with customizable title, message, app name, and timeout.
- `get_current_date_info` — return rich information about the current date such as day number, week number, quarter and more.

---

## Changelog

### 0.1.5

- Added `send_notification` tool to send native system notifications across Windows, macOS, and Linux.
- Added `plyer` dependency for cross-platform notification support.

### 0.1.4

- Defined annotations to declare tools as read-only.

### 0.1.3

- Added `get_current_date_info` tool to get comprehensive information about the current date.

### 0.1.2

- Change `open_url` to `open_urls` to open a list of URLs in the default browser.

### 0.1.1

- Improve the `open_url` tool to handle URLs without a scheme and validate that the URL is valid.

### 0.1.0

- Added `open_url` tool.
- Added `copy_to_clipboard` tool.

---

## License

MIT License. See [`license`](license).

