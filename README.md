# DataReigns Sample MCP Server

A working example of what an **AI-ready data layer** looks like: a small sales
database exposed to AI assistants through the [Model Context Protocol](https://modelcontextprotocol.io)
(MCP), with guardrails that make it safe.

This is the pattern behind the "AI-ready data" service: instead of handing an
AI agent raw database credentials, you give it a typed, read-only tool
interface. The agent can answer business questions. It cannot drop your tables.

## What it does

Five tools over a sample SQLite sales database (~2,000 orders, 2025–2026):

| Tool | Answers |
|---|---|
| `get_schema` | What tables and columns exist |
| `top_products` | What sells best, by revenue |
| `sales_by_region` | Revenue and order count per region |
| `monthly_trend` | Month-by-month revenue trend |
| `run_query` | Any read-only `SELECT` — everything else is rejected |

## Quick start

```bash
pip install -r requirements.txt
python data/generate_data.py   # builds data/sales.db
python server.py               # runs over stdio
```

## Connect it to Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "datareigns-sales": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

Then ask things like:

- "What are our top 3 products by revenue?"
- "Which region is underperforming this year?"
- "Show me the monthly revenue trend — any dips I should know about?"

## Why clients pay for this pattern

1. **Governed access.** The agent gets tools, not credentials. `run_query`
   rejects anything that is not a `SELECT`.
2. **Typed answers.** Structured rows come back, not raw dumps — the agent
   reasons over clean data.
3. **Swappable backend.** Point `_connect()` at Postgres, BigQuery, or
   Databricks SQL and the agent interface does not change.

Built by DataReigns — data engineering consultancy, Charlotte NC.
Python, MCP SDK v2, SQLite.
