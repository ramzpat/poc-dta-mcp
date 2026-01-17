"""
MCP Server for Data Analytics with PostgreSQL
"""
import json
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from database import DatabaseConnection

# Initialize the MCP server
app = Server("data-analytics-mcp")

# Initialize database connection
db = DatabaseConnection()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="query_database",
            description="Execute SQL queries against the PostgreSQL database. Returns results as JSON.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute (SELECT statements only for safety)",
                    }
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="list_tables",
            description="List all tables in the database with their row counts",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="describe_table",
            description="Get the schema/structure of a specific table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to describe",
                    }
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="get_customer_summary",
            description="Get a summary of all customers with their activity and revenue",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "query_database":
            query = arguments.get("query", "")
            
            # Basic safety check - only allow SELECT queries
            if not query.strip().upper().startswith("SELECT"):
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "Only SELECT queries are allowed for safety"
                        })
                    )
                ]
            
            results = db.execute_query(query)
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "rows": len(results),
                        "data": results
                    }, default=str)
                )
            ]
        
        elif name == "list_tables":
            query = """
                SELECT 
                    table_name,
                    (SELECT COUNT(*) 
                     FROM information_schema.columns 
                     WHERE table_schema = t.table_schema 
                     AND table_name = t.table_name) as column_count
                FROM information_schema.tables t
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """
            results = db.execute_query(query)
            
            # Get row counts for each table
            for result in results:
                table_name = result['table_name']
                count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                count_result = db.execute_query(count_query)
                result['row_count'] = count_result[0]['count']
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "tables": results
                    }, default=str)
                )
            ]
        
        elif name == "describe_table":
            table_name = arguments.get("table_name", "")
            
            query = """
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = %s
                ORDER BY ordinal_position;
            """
            results = db.execute_query(query, (table_name,))
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "table_name": table_name,
                        "columns": results
                    }, default=str)
                )
            ]
        
        elif name == "get_customer_summary":
            query = "SELECT * FROM customer_summary ORDER BY customer_id"
            results = db.execute_query(query)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "customers": results
                    }, default=str)
                )
            ]
        
        else:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Unknown tool: {name}"
                    })
                )
            ]
    
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "type": type(e).__name__
                })
            )
        ]


async def main():
    """Run the MCP server"""
    # Test database connection before starting
    if not db.test_connection():
        print("Error: Could not connect to database")
        return
    
    print("Database connection successful!")
    print("Starting MCP server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
