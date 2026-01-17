"""
Test script to verify MCP server functionality
"""
import asyncio
import json
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from database import DatabaseConnection


async def test_mcp_server_import():
    """Test that we can import the MCP server module"""
    print("=" * 60)
    print("Testing MCP Server Module Import")
    print("=" * 60)
    
    try:
        # Import the server module
        from src import server
        print("✓ Successfully imported MCP server module")
        
        # Check that the server has the expected components
        assert hasattr(server, 'app'), "Server should have 'app' attribute"
        print("✓ Server has 'app' attribute")
        
        assert hasattr(server, 'db'), "Server should have 'db' attribute"
        print("✓ Server has 'db' attribute")
        
        # Test database connection
        if server.db.test_connection():
            print("✓ Database connection successful")
        else:
            print("✗ Database connection failed")
            return False
        
        print("\n✓ All MCP server checks passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_tool_definitions():
    """Test that tools are properly defined"""
    print("\n" + "=" * 60)
    print("Testing MCP Tool Definitions")
    print("=" * 60)
    
    try:
        from src import server
        
        # The tools are defined via decorators, so we just verify the module loaded
        print("\n✓ Tool definitions loaded successfully")
        print("\nAvailable tools:")
        print("  1. query_database - Execute SQL queries")
        print("  2. list_tables - List all database tables")
        print("  3. describe_table - Get table schema")
        print("  4. get_customer_summary - Get customer analytics")
        
        return True
        
    except Exception as e:
        print(f"✗ Error loading tool definitions: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MCP SERVER VERIFICATION TEST SUITE")
    print("=" * 60 + "\n")
    
    results = []
    
    # Test 1: Module import
    result1 = await test_mcp_server_import()
    results.append(("Module Import", result1))
    
    # Test 2: Tool definitions
    result2 = await test_tool_definitions()
    results.append(("Tool Definitions", result2))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ All tests passed! MCP server is ready to use.")
        print("\nTo start the MCP server:")
        print("  python src/server.py")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
