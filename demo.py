"""
Demo script to test MCP server functionality
"""
import asyncio
import json
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from database import DatabaseConnection


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_results(results: list, limit: int = 5):
    """Print query results in a formatted way"""
    if not results:
        print("No results found")
        return
    
    print(f"\nFound {len(results)} rows")
    print(f"Showing first {min(limit, len(results))} rows:\n")
    
    for i, row in enumerate(results[:limit], 1):
        print(f"Row {i}:")
        for key, value in row.items():
            print(f"  {key}: {value}")
        print()


async def test_mcp_tools():
    """Test the MCP server tools functionality"""
    
    print_section("MCP Server Demo - PostgreSQL Integration")
    
    # Initialize database connection
    db = DatabaseConnection()
    
    # Test 1: Database connection
    print_section("Test 1: Database Connection")
    if db.test_connection():
        print("✓ Database connection successful!")
    else:
        print("✗ Database connection failed!")
        return
    
    # Test 2: List all tables
    print_section("Test 2: List Tables")
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """
    tables = db.execute_query(query)
    print("Available tables:")
    for table in tables:
        # Get row count
        count_query = f"SELECT COUNT(*) as count FROM {table['table_name']}"
        count = db.execute_query(count_query)[0]['count']
        print(f"  - {table['table_name']} ({count} rows)")
    
    # Test 3: Query customers
    print_section("Test 3: Query Customers")
    query = "SELECT * FROM customers ORDER BY customer_id LIMIT 5"
    results = db.execute_query(query)
    print_results(results)
    
    # Test 4: Query network events
    print_section("Test 4: Query Network Events")
    query = """
        SELECT 
            ne.event_id,
            c.customer_name,
            ne.event_type,
            ne.event_timestamp,
            ne.data_usage_mb,
            ne.network_quality
        FROM network_events ne
        JOIN customers c ON ne.customer_id = c.customer_id
        ORDER BY ne.event_timestamp DESC
        LIMIT 5
    """
    results = db.execute_query(query)
    print_results(results)
    
    # Test 5: Query revenue
    print_section("Test 5: Query Revenue Transactions")
    query = """
        SELECT 
            r.revenue_id,
            c.customer_name,
            r.transaction_date,
            r.amount,
            r.transaction_type,
            r.payment_method
        FROM revenue r
        JOIN customers c ON r.customer_id = c.customer_id
        ORDER BY r.transaction_date DESC
        LIMIT 5
    """
    results = db.execute_query(query)
    print_results(results)
    
    # Test 6: Customer summary view
    print_section("Test 6: Customer Summary Analysis")
    query = "SELECT * FROM customer_summary ORDER BY total_revenue DESC LIMIT 5"
    results = db.execute_query(query)
    print("Top 5 customers by revenue:")
    print_results(results)
    
    # Test 7: Analytics query - Average revenue by account type
    print_section("Test 7: Revenue Analytics by Account Type")
    query = """
        SELECT 
            c.account_type,
            COUNT(DISTINCT c.customer_id) as customer_count,
            AVG(c.monthly_fee) as avg_monthly_fee,
            SUM(r.amount) as total_revenue
        FROM customers c
        LEFT JOIN revenue r ON c.customer_id = r.customer_id
        GROUP BY c.account_type
        ORDER BY total_revenue DESC
    """
    results = db.execute_query(query)
    print("\nRevenue by account type:")
    for row in results:
        print(f"\n{row['account_type']} Account:")
        print(f"  Customers: {row['customer_count']}")
        print(f"  Avg Monthly Fee: ${row['avg_monthly_fee']:.2f}")
        print(f"  Total Revenue: ${row['total_revenue']:.2f}")
    
    # Test 8: Network quality analysis
    print_section("Test 8: Network Quality Analysis")
    query = """
        SELECT 
            network_quality,
            COUNT(*) as event_count,
            SUM(data_usage_mb) as total_data_mb,
            AVG(data_usage_mb) as avg_data_mb
        FROM network_events
        WHERE data_usage_mb IS NOT NULL
        GROUP BY network_quality
        ORDER BY event_count DESC
    """
    results = db.execute_query(query)
    print("\nNetwork quality distribution:")
    for row in results:
        print(f"\n{row['network_quality'].capitalize()} Quality:")
        print(f"  Events: {row['event_count']}")
        print(f"  Total Data: {float(row['total_data_mb']):.2f} MB")
        print(f"  Avg Data per Event: {float(row['avg_data_mb']):.2f} MB")
    
    print_section("Demo Completed Successfully!")
    print("\nThe MCP server is ready to use with the following tools:")
    print("  1. query_database - Execute SQL queries")
    print("  2. list_tables - List all database tables")
    print("  3. describe_table - Get table schema")
    print("  4. get_customer_summary - Get customer analytics")
    print("\nNext steps:")
    print("  - Start the MCP server: python src/server.py")
    print("  - Connect your AI agent to the MCP server")
    print("  - Use the tools to query and analyze data")


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
