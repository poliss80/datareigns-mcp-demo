#!/usr/bin/env python3
"""
DataReigns sample MCP server.

Exposes a small sales SQLite database to AI assistants through the
Model Context Protocol (MCP). Shows the core pattern clients pay for:
a governed, read-only data layer that an AI agent can query safely.

First-time setup:
    python data/generate_data.py
    python server.py          # stdio transport; wire into Claude Desktop

Built with the official MCP Python SDK (v2 API).
"""
import sqlite3
from pathlib import Path

from mcp.server.mcpserver import MCPServer

DB_PATH = Path(__file__).parent / "data" / "sales.db"
server = MCPServer("datareigns-sales")


def _connect():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"{DB_PATH} not found. Run: python data/generate_data.py"
        )
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _rows(sql, params=()):
    con = _connect()
    try:
        return [dict(r) for r in con.execute(sql, params).fetchall()]
    finally:
        con.close()


@server.tool()
def get_schema() -> str:
    """List every table and its columns in the sales database."""
    con = _connect()
    try:
        tables = [
            r[0]
            for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        ]
        out = []
        for t in tables:
            cols = [r[1] for r in con.execute(f"PRAGMA table_info({t})")]
            out.append(f"{t}({', '.join(cols)})")
        return "\n".join(out)
    finally:
        con.close()


@server.tool()
def top_products(limit: int = 5) -> list:
    """Top N products by total revenue. Answers 'what sells best'."""
    return _rows(
        """SELECT product, category,
                  SUM(quantity) AS units_sold,
                  ROUND(SUM(total), 2) AS revenue
           FROM orders GROUP BY product, category
           ORDER BY revenue DESC LIMIT ?""",
        (limit,),
    )


@server.tool()
def sales_by_region() -> list:
    """Total revenue and order count per region."""
    return _rows(
        """SELECT region, COUNT(*) AS orders,
                  ROUND(SUM(total), 2) AS revenue
           FROM orders GROUP BY region ORDER BY revenue DESC"""
    )


@server.tool()
def monthly_trend() -> list:
    """Monthly revenue trend, oldest month first."""
    return _rows(
        """SELECT substr(order_date, 1, 7) AS month,
                  COUNT(*) AS orders,
                  ROUND(SUM(total), 2) AS revenue
           FROM orders GROUP BY month ORDER BY month"""
    )


@server.tool()
def run_query(sql: str) -> list:
    """Run a read-only SQL SELECT against the sales database.

    Only SELECT statements are allowed; anything else is rejected.
    This is the guardrail that makes the data layer safe to expose
    to an AI agent.
    """
    if not sql.strip().lower().startswith("select"):
        raise ValueError("Only SELECT statements are allowed.")
    return _rows(sql)


if __name__ == "__main__":
    server.run()
