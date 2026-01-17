# MCP Server - PostgreSQL Integration Setup Guide

This guide will help you set up and run the MCP (Model Context Protocol) server with PostgreSQL for data analytics.

## Setup Options

### Option 1: Dev Container (Recommended for Consistent Environment)

Use VS Code Dev Containers for zero-configuration setup:

1. Install [VS Code](https://code.visualstudio.com/), [Docker Desktop](https://www.docker.com/products/docker-desktop), and the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open the repository in VS Code: `code /path/to/poc-dta-mcp`
3. Press `F1` → `Dev Containers: Reopen in Container`
4. Everything is automatically set up! Run `python demo.py` to verify

See [.devcontainer/README.md](.devcontainer/README.md) for detailed documentation.

### Option 2: Manual Setup

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd poc-dta-mcp
```

### 2. Set Up Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

The default configuration should work for local development. The `.env` file contains:
- PostgreSQL connection settings
- MCP server configuration

### 3. Start PostgreSQL with Docker

Start the PostgreSQL database using Docker Compose:

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL 15 on port 5432
- Create the `analytics_db` database
- Initialize tables (customers, network_events, revenue)
- Load sample telco data

Wait a few seconds for the database to initialize, then verify it's running:

```bash
docker-compose ps
```

### 4. Install Python Dependencies

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### 5. Run the Demo

Test the database connection and MCP tools:

```bash
python demo.py
```

This will run a series of tests demonstrating:
- Database connectivity
- Table listings
- Customer queries
- Network event analysis
- Revenue analytics
- Customer summary views

### 6. Start the MCP Server

Start the MCP server:

```bash
python src/server.py
```

The server will:
- Connect to PostgreSQL
- Expose MCP tools for data analytics
- Wait for tool calls via stdio

## MCP Tools Available

The server exposes the following tools:

### 1. `query_database`
Execute SQL queries against the PostgreSQL database.

**Input:**
```json
{
  "query": "SELECT * FROM customers LIMIT 5"
}
```

**Output:**
```json
{
  "success": true,
  "rows": 5,
  "data": [...]
}
```

### 2. `list_tables`
List all tables in the database with row counts.

**Input:** None

**Output:**
```json
{
  "success": true,
  "tables": [
    {
      "table_name": "customers",
      "column_count": 11,
      "row_count": 10
    }
  ]
}
```

### 3. `describe_table`
Get the schema/structure of a specific table.

**Input:**
```json
{
  "table_name": "customers"
}
```

**Output:**
```json
{
  "success": true,
  "table_name": "customers",
  "columns": [...]
}
```

### 4. `get_customer_summary`
Get a summary of all customers with their activity and revenue.

**Input:** None

**Output:**
```json
{
  "success": true,
  "customers": [...]
}
```

## Testing with MCP Clients

### Using Claude Desktop or Other MCP Clients

The project includes an `mcp.json` configuration file for easy testing with MCP clients.

#### Quick Setup for Claude Desktop

1. **Ensure PostgreSQL is running**:
   ```bash
   docker compose up -d
   ```

2. **Add the MCP server to Claude Desktop**:

   Open your Claude Desktop configuration file and add:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "data-analytics": {
         "command": "python",
         "args": ["src/server.py"],
         "env": {
           "POSTGRES_HOST": "localhost",
           "POSTGRES_PORT": "5432",
           "POSTGRES_DB": "analytics_db",
           "POSTGRES_USER": "analytics_user",
           "POSTGRES_PASSWORD": "analytics_password"
         }
       }
     }
   }
   ```

   **Note**: Adjust the `args` path if your project is in a different location. Use the full path to `server.py` if needed.

3. **Restart Claude Desktop** to load the new configuration.

4. **Test the MCP server** by asking Claude:
   - "List all tables in the database"
   - "Show me the first 5 customers"
   - "What's the total revenue by account type?"
   - "Describe the structure of the customers table"

#### Using the Included mcp.json

The `mcp.json` file in the project root contains the ready-to-use configuration above. You can copy its contents directly into your MCP client's configuration.

#### Testing with Other MCP Clients

For other MCP clients that support the MCP protocol:

1. Configure the client to run: `python src/server.py`
2. Set the environment variables as shown above
3. Ensure the working directory is the project root

The MCP server communicates via stdio and will automatically connect to PostgreSQL when started.

## Database Schema

### Customers Table
- `customer_id` (PK)
- `customer_name`
- `email`
- `phone`
- `account_type` (Basic, Standard, Premium)
- `subscription_start_date`
- `subscription_end_date`
- `monthly_fee`
- `status` (active, suspended, churned)

### Network Events Table
- `event_id` (PK)
- `customer_id` (FK)
- `event_type` (data, call)
- `event_timestamp`
- `data_usage_mb`
- `call_duration_minutes`
- `network_quality` (excellent, good, fair, poor)
- `location`

### Revenue Table
- `revenue_id` (PK)
- `customer_id` (FK)
- `transaction_date`
- `amount`
- `transaction_type` (subscription, overage)
- `payment_method`
- `description`

## Sample Data

The database is pre-loaded with:
- **10 customers** with different account types (Basic, Standard, Premium)
- **25+ network events** (data usage, calls)
- **20+ revenue transactions** (subscriptions, overages)

## Example Queries

Here are some useful queries to try:

```sql
-- Get all active customers
SELECT * FROM customers WHERE status = 'active';

-- Get network events with customer info
SELECT c.customer_name, ne.event_type, ne.event_timestamp, ne.network_quality
FROM network_events ne
JOIN customers c ON ne.customer_id = c.customer_id
ORDER BY ne.event_timestamp DESC;

-- Calculate total revenue by customer
SELECT c.customer_name, SUM(r.amount) as total_revenue
FROM customers c
LEFT JOIN revenue r ON c.customer_id = r.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_revenue DESC;

-- Get average data usage by network quality
SELECT network_quality, AVG(data_usage_mb) as avg_data_mb
FROM network_events
WHERE data_usage_mb IS NOT NULL
GROUP BY network_quality;
```

## Connecting an AI Agent

To connect an AI agent (like Claude) to this MCP server:

1. Configure the AI agent's MCP client to connect to the server via stdio
2. The agent can then call the exposed tools to query and analyze data
3. Example use cases:
   - "Show me all premium customers"
   - "What's the average data usage by network quality?"
   - "Calculate churn rate for each account type"
   - "Show revenue trends over time"

## Troubleshooting

### Database Connection Issues

If you can't connect to the database:

```bash
# Check if PostgreSQL is running
docker-compose ps

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Port Already in Use

If port 5432 is already in use:

1. Edit `docker-compose.yml` to use a different port (e.g., `5433:5432`)
2. Update `.env` with `POSTGRES_PORT=5433`

### Reset Database

To reset the database and reload sample data:

```bash
docker-compose down -v
docker-compose up -d
```

## Stopping the Services

Stop the PostgreSQL database:

```bash
docker-compose down
```

To also remove volumes (database data):

```bash
docker-compose down -v
```

## Next Steps

- Add more MCP tools for specific analytics tasks
- Implement data visualization tools
- Add session management for privacy-preserving access
- Create more complex analytical queries
- Add authentication and authorization

## Project Structure

```
poc-dta-mcp/
├── src/
│   ├── server.py          # MCP server implementation
│   └── database.py        # Database connection utilities
├── database/
│   ├── init.sql          # Database schema
│   └── sample_data.sql   # Sample data
├── docs/
│   ├── requirements.md   # Project requirements
│   └── design.md        # Technical design
├── demo.py              # Demo script
├── docker-compose.yml   # Docker setup
├── pyproject.toml      # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

## Support

For issues or questions, please refer to:
- `/docs/requirements.md` - Full requirements documentation
- `/docs/design.md` - Technical design details
