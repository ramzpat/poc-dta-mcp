"""
Example MCP Client - Demonstrates how to interact with the MCP server

This is a simplified example showing the concept of MCP tool invocation.
In production, you would use the official MCP Python SDK client.
"""
import json
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from database import DatabaseConnection


class SimpleMCPClient:
    """A simple MCP client simulator for demonstration purposes"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """
        Simulate calling an MCP tool
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as a dictionary
            
        Returns:
            Tool response as a dictionary
        """
        print(f"\n📞 Calling MCP Tool: {tool_name}")
        print(f"📋 Arguments: {json.dumps(arguments, indent=2)}")
        
        try:
            if tool_name == "query_database":
                query = arguments.get("query", "")
                if not query.strip().upper().startswith("SELECT"):
                    return {"error": "Only SELECT queries are allowed"}
                
                results = self.db.execute_query(query)
                return {
                    "success": True,
                    "rows": len(results),
                    "data": results
                }
            
            elif tool_name == "list_tables":
                query = """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name;
                """
                results = self.db.execute_query(query)
                
                tables = []
                for result in results:
                    table_name = result['table_name']
                    count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                    count_result = self.db.execute_query(count_query)
                    tables.append({
                        "table_name": table_name,
                        "row_count": count_result[0]['count']
                    })
                
                return {"success": True, "tables": tables}
            
            elif tool_name == "describe_table":
                table_name = arguments.get("table_name", "")
                query = """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = %s
                    ORDER BY ordinal_position;
                """
                results = self.db.execute_query(query, (table_name,))
                return {
                    "success": True,
                    "table_name": table_name,
                    "columns": results
                }
            
            elif tool_name == "get_customer_summary":
                query = "SELECT * FROM customer_summary ORDER BY customer_id"
                results = self.db.execute_query(query)
                return {"success": True, "customers": results}
            
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        
        except Exception as e:
            return {"error": str(e), "type": type(e).__name__}


def print_response(response: dict):
    """Pretty print the response"""
    print(f"\n📤 Response:")
    print(json.dumps(response, indent=2, default=str))


def main():
    """Demonstrate MCP tool usage"""
    
    print("=" * 70)
    print("  MCP CLIENT EXAMPLE - Tool Invocation Demo")
    print("=" * 70)
    
    client = SimpleMCPClient()
    
    # Example 1: List all tables
    print("\n" + "=" * 70)
    print("Example 1: List all tables in the database")
    print("=" * 70)
    
    response = client.call_tool("list_tables", {})
    print_response(response)
    
    # Example 2: Describe a table
    print("\n" + "=" * 70)
    print("Example 2: Get schema for 'customers' table")
    print("=" * 70)
    
    response = client.call_tool("describe_table", {"table_name": "customers"})
    print_response(response)
    
    # Example 3: Query customers
    print("\n" + "=" * 70)
    print("Example 3: Query active premium customers")
    print("=" * 70)
    
    response = client.call_tool(
        "query_database",
        {
            "query": "SELECT customer_name, email, monthly_fee FROM customers WHERE status = 'active' AND account_type = 'Premium'"
        }
    )
    print_response(response)
    
    # Example 4: Analytics query
    print("\n" + "=" * 70)
    print("Example 4: Calculate average revenue by account type")
    print("=" * 70)
    
    response = client.call_tool(
        "query_database",
        {
            "query": """
                SELECT 
                    c.account_type,
                    COUNT(DISTINCT c.customer_id) as customer_count,
                    AVG(r.amount) as avg_transaction,
                    SUM(r.amount) as total_revenue
                FROM customers c
                LEFT JOIN revenue r ON c.customer_id = r.customer_id
                GROUP BY c.account_type
                ORDER BY total_revenue DESC
            """
        }
    )
    print_response(response)
    
    # Example 5: Get customer summary
    print("\n" + "=" * 70)
    print("Example 5: Get customer summary view")
    print("=" * 70)
    
    response = client.call_tool("get_customer_summary", {})
    if response.get("success"):
        print(f"\n📤 Response: Found {len(response['customers'])} customers")
        print("\nTop 3 customers by revenue:")
        for i, customer in enumerate(response['customers'][:3], 1):
            print(f"\n  {i}. {customer['customer_name']}")
            print(f"     Account Type: {customer['account_type']}")
            print(f"     Total Events: {customer['total_events']}")
            print(f"     Total Revenue: ${customer['total_revenue']}")
    else:
        print_response(response)
    
    print("\n" + "=" * 70)
    print("Demo completed!")
    print("=" * 70)
    print("\nThis example shows how an AI agent would interact with the MCP server.")
    print("The actual MCP protocol uses JSON-RPC over stdio, but the concept is the same:")
    print("  1. Agent calls a tool with arguments")
    print("  2. Server executes the tool logic")
    print("  3. Server returns results to the agent")
    print("\nNext: Connect a real AI agent (like Claude) to use these tools!")


if __name__ == "__main__":
    main()
