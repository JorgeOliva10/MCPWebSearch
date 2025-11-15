# 📂 MCP Web Search Server

**A privacy‑focused web, social media, and archive search server exposing tools via the Model Control Protocol (MCP) for controlled access to external search capabilities.**

---  

## Table of Contents  
- [Features](#features)  
- [Installation & Quick Start](#installation--quick-start)  
- [Command‑Line Options](#command-line-options)  
- [Integration with LM Studio](#integration-with-lm-studio)  
- [MCP API Overview](#mcp-api-overview)  
  - [`initialize`](#initialize)  
  - [`tools/list`](#toolslist)  
  - [`tools/call`](#toolscall)  
- [Available Tools](#available-tools)  
  - [`web_search`](#web_search)  
  - [`social_search`](#social_search)  
  - [`archives_search`](#archives_search)  
  - [`list_engines`](#list_engines)  
  - [`list_archives_services`](#list_archives_services)  
  - [`clear_cache`](#clear_cache)  
- [Security Features](#security-features)  

---  

## 🎯 Features  
- **Parallel search** across multiple privacy‑focused web engines.  
- **Social media lookup** for public content on major platforms.  
- **Archive retrieval** from Wayback Machine, archive.today, Google Cache and others.  
- **Dynamic listing** of supported engines and archive services.  
- **Result caching** with LRU eviction to speed up repeated queries.  

---  

## 📦 Installation & Quick Start  
```bash
# Clone the repository (if applicable)
git clone https://github.com/undici77/MCPWebSearch.git
cd MCPWebSearch

# Run the startup script (adjust name if different)
./run.sh -d /path/to/working/directory
```
1️⃣ **Create & activate** a Python virtual environment (`.venv`).  
2️⃣ **Install** all required dependencies from `requirements.txt`.  
3️⃣ **Launch** the MCP Search Server (`main.py`) which listens on stdin/stdout for JSON‑RPC messages.  

> 📌 Ensure the startup script is executable: `chmod +x run.sh`  

---  

## ⚙️ Command‑Line Options  
| Option | Description |
|--------|-------------|
| `-d`, `--directory` | Path to the working directory (default: current process dir). |

*The server itself does not require additional CLI flags; all configuration is performed via JSON‑RPC.*  

---  

## 🤝 Integration with LM Studio  
Add an entry to your `mcp.json` so LM Studio can start the server automatically:

```json
{
  "mcpServers": {
    "web-search": {
      "command": "/absolute/path/to/run.sh",
      "args": [
        "-d",
        "/absolute/path/to/working/directory"
      ],
      "env": { "WORKING_DIR": "." }
    }
  }
}
```
> 📌 Make the script executable (`chmod +x /absolute/path/to/run.sh`) and run `./run.sh` once to install the virtual environment before launching LM Studio.  

---  

## 📡 MCP API Overview  
All communication follows **JSON‑RPC 2.0** over stdin/stdout.

### `initialize`  
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {}
}
```
*Response*: protocol version (`2024-11-05`), server capabilities (tool enumeration) and basic server info (`name`, `version`).  

### `tools/list`  
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```
*Response*: an array of tool definitions (name, description, input schema).  

### `tools/call`  
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "<tool_name>",
    "arguments": { … }
  }
}
```
*Note*: The tool identifier key is **`name`**, not `tool`.  

---  

## 🛠️ Available Tools  

### web_search  
**Search the web using multiple privacy‑focused engines in parallel.**  

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | ✅ | Search query (max 500 characters). |
| `engine` | string | ❌ (default `all`) | Engine to use (`duckduckgo`, `brave`, `startpage`, `ecosia`, `mojeek`, `yandex` or `all`). |
| `max_results` | integer | ❌ (default 20) | Max results per engine (1‑50). |

**Example**  
```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "tools/call",
  "params": {
    "name": "web_search",
    "arguments": {
      "query": "privacy focused search engines",
      "engine": "duckduckgo",
      "max_results": 15
    }
  }
}
```
*The server returns a formatted text block containing titles, URLs and snippets from each selected engine.*  

---  

### social_search  
**Search public content on major social‑media platforms.**  

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | ✅ | Search query (max 500 characters). |
| `platform` | string | ❌ (default `all`) | Platform to search (`twitter`, `reddit`, `youtube`, `github`, `stackoverflow`, `medium`, `pinterest`, `tiktok`, `instagram`, `facebook`, `linkedin` or `all`). |

**Example**  
```json
{
  "jsonrpc": "2.0",
  "id": 11,
  "method": "tools/call",
  "params": {
    "name": "social_search",
    "arguments": {
      "query": "AI ethics research",
      "platform": "reddit"
    }
  }
}
```
*The response contains direct URLs that can be opened in a browser.*  

---  

### archives_search  
**Find archived versions of a URL across multiple web‑archive services.**  

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `url` | string | ✅ | Complete URL (must include `http://` or `https://`). |
| `service` | string | ❌ (default `all`) | Archive service (`wayback`, `archive_today`, `google_cache`, `bing_cache`, `yandex_cache`, `cachedview`, `ghostarchive` or `all`). |
| `check_availability` | boolean | ❌ (default false) | When true, the server queries the Wayback Machine API for snapshot statistics. |

**Example**  
```json
{
  "jsonrpc": "2.0",
  "id": 12,
  "method": "tools/call",
  "params": {
    "name": "archives_search",
    "arguments": {
      "url": "https://example.com",
      "service": "wayback",
      "check_availability": true
    }
  }
}
```
*The response lists archive URLs and, if requested, snapshot counts and timestamps.*  

---  

### list_engines  
**List all available privacy‑focused search engines.**  

| Name | Type | Required | Description |
|------|------|----------|-------------|
*(No parameters)* | — | — | — |

**Example**  
```json
{
  "jsonrpc": "2.0",
  "id": 13,
  "method": "tools/call",
  "params": {
    "name": "list_engines",
    "arguments": {}
  }
}
```
*The server returns a markdown‑formatted overview of each engine and usage notes.*  

---  

### list_archives_services  
**List all supported web‑archive services.**  

| Name | Type | Required | Description |
|------|------|----------|-------------|
*(No parameters)* | — | — | — |

**Example**  
```json
{
  "jsonrpc": "2.0",
  "id": 14,
  "method": "tools/call",
  "params": {
    "name": "list_archives_services",
    "arguments": {}
  }
}
```
*The response includes a description of each service, its ID and key features.*  

---  

### clear_cache  
**Clear the internal search‑result cache.**  

| Name | Type | Required | Description |
|------|------|----------|-------------|
*(No parameters)* | — | — | — |

**Example**  
```json
{
  "jsonrpc": "2.0",
  "id": 15,
  "method": "tools/call",
  "params": {
    "name": "clear_cache",
    "arguments": {}
  }
}
```
*The server replies with a confirmation message.*  

---  

## 🔐 Security Features  
- **Query sanitisation** – strips control characters, removes HTML tags and enforces `MAX_QUERY_LENGTH` (500).  
- **Strict URL validation** – accepts only `http://` or `https://` schemes with a valid domain.  
- **Blocked patterns** – regexes prevent `<script>` injection, `javascript:` URIs and event‑handler attributes.  
- **Input schema enforcement** – each tool validates required fields via the JSON‑RPC `inputSchema`.  
- **Rate limiting** – an asyncio semaphore caps concurrent external requests (`MAX_CONCURRENT_SEARCHES`).  

---

*© 2025 Undici77 – All rights reserved.*