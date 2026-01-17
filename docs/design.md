# POC: Data Analytics MCP Server - Technical Design Document

## Document Information
**Version**: 1.0  
**Last Updated**: 2026-01-17  
**Status**: Design  
**Owner**: Technical Team

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      AI Agent (Claude)                        │
│                  (Data Scientist Agent)                       │
└───────────────────────┬──────────────────────────────────────┘
                        │ MCP Protocol
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                     MCP Server (FastMCP)                      │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │   Tools    │  │ Resources  │  │      Prompts         │  │
│  │            │  │            │  │                      │  │
│  │ • query_db │  │ • schemas  │  │ • churn_analysis    │  │
│  │ • analyze  │  │ • docs     │  │ • network_analysis  │  │
│  │ • visualize│  │ • templates│  │ • revenue_analysis  │  │
│  │ • session  │  │            │  │                      │  │
│  └────────────┘  └────────────┘  └──────────────────────┘  │
└───────────┬──────────────────┬───────────────────────────────┘
            │                  │
            ▼                  ▼
┌───────────────────┐  ┌──────────────────────┐
│   Data Layer      │  │  Session Manager     │
│                   │  │                      │
│ ┌───────────────┐ │  │ ┌──────────────────┐ │
│ │  PostgreSQL   │ │  │ │      Redis       │ │
│ │               │ │  │ │                  │ │
│ │ • Customers   │ │  │ │ • Session State  │ │
│ │ • Network     │ │  │ │ • Data Context   │ │
│ │ • Revenue     │ │  │ │ • Cache          │ │
│ └───────────────┘ │  │ └──────────────────┘ │
│                   │  │                      │
│ ┌───────────────┐ │  └──────────────────────┘
│ │  CSV/PDF      │ │
│ │  Processors   │ │
│ └───────────────┘ │
└───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│   Analytics Engine            │
│                               │
│ • pandas/numpy               │
│ • scipy/statsmodels          │
│ • scikit-learn               │
│ • matplotlib/seaborn/plotly  │
└───────────────────────────────┘
```

### 1.2 Component Overview

#### MCP Server
- **Framework**: FastMCP (Python)
- **Purpose**: Expose data analytics capabilities via MCP protocol
- **Responsibilities**:
  - Handle tool invocations from AI agent
  - Manage resources and prompts
  - Coordinate between data layer and analytics engine
  - Enforce security and access controls

#### Data Layer
- **PostgreSQL**: Primary structured data store
- **Redis**: Session state and caching
- **File Processors**: Handle CSV and PDF imports
- **Connection Pool**: Manage database connections efficiently

#### Session Manager
- **Purpose**: Privacy-preserving data access
- **Responsibilities**:
  - Create isolated session contexts
  - Manage session lifecycle (create, read, update, close)
  - Enforce TTLs and cleanup
  - Archive session data

#### Analytics Engine
- **Libraries**: pandas, numpy, scipy, statsmodels, scikit-learn
- **Responsibilities**:
  - Execute data analysis algorithms
  - Generate visualizations
  - Produce statistical reports

---

## 2. Data Model

### 2.1 Database Schema

#### Customers Table
```sql
CREATE TABLE customers (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    age INTEGER CHECK (age >= 18 AND age <= 120),
    gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other', 'Unspecified')),
    location VARCHAR(100),
    account_type VARCHAR(50) CHECK (account_type IN ('Basic', 'Premium', 'Enterprise')),
    is_churned BOOLEAN DEFAULT FALSE,
    churn_date TIMESTAMP,
    
    -- Indexes
    INDEX idx_customers_created_at (created_at),
    INDEX idx_customers_account_type (account_type),
    INDEX idx_customers_is_churned (is_churned)
);
```

#### Network_Events Table
```sql
CREATE TABLE network_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    event_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(50) CHECK (event_type IN ('call', 'sms', 'data')),
    network_quality_score FLOAT CHECK (network_quality_score >= 1.0 AND network_quality_score <= 5.0),
    duration_seconds INTEGER CHECK (duration_seconds >= 0),
    data_usage_mb FLOAT CHECK (data_usage_mb >= 0),
    
    -- Indexes
    INDEX idx_network_events_customer_id (customer_id),
    INDEX idx_network_events_timestamp (event_timestamp),
    INDEX idx_network_events_type (event_type)
);
```

#### Revenue Table
```sql
CREATE TABLE revenue (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    service_type VARCHAR(50) CHECK (service_type IN ('voice', 'data', 'sms', 'subscription')),
    payment_method VARCHAR(50) CHECK (payment_method IN ('credit_card', 'debit_card', 'bank_transfer', 'mobile_wallet')),
    
    -- Indexes
    INDEX idx_revenue_customer_id (customer_id),
    INDEX idx_revenue_transaction_date (transaction_date),
    INDEX idx_revenue_service_type (service_type)
);
```

### 2.2 Session Data Model

#### Session Metadata (Redis Hash)
```
Key: session:{session_id}
Fields:
  - session_id: UUID
  - created_at: ISO-8601 timestamp
  - expires_at: ISO-8601 timestamp
  - last_accessed: ISO-8601 timestamp
  - status: 'active' | 'expired' | 'closed'
  - data_source: string
  - access_level: 'read' | 'write'
  - user_id: string (optional)
  - metadata: JSON object
TTL: Configurable (default: 3600 seconds)
```

#### Session Data (Redis Hash)
```
Key: session:{session_id}:data:{key}
Value: JSON serialized data
TTL: Inherited from session
```

#### Session Index (Redis Set)
```
Key: session:index:{user_id}
Members: List of session_ids for user
```

---

## 3. API Design

### 3.1 MCP Tools

#### Tool: query_database

**Purpose**: Execute SQL queries against PostgreSQL

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "SQL query to execute"
    },
    "parameters": {
      "type": "object",
      "description": "Query parameters for parameterized queries"
    },
    "timeout": {
      "type": "integer",
      "default": 30,
      "description": "Query timeout in seconds"
    }
  },
  "required": ["query"]
}
```

**Output Schema**:
```json
{
  "rows": [{"column": "value"}],
  "columns": ["column1", "column2"],
  "row_count": 100
}
```

**Error Codes**:
- `QueryError`: Query execution failed
- `TimeoutError`: Query exceeded timeout
- `ValidationError`: Invalid query syntax

#### Tool: analyze_data

**Purpose**: Perform statistical analysis on datasets

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "data_source": {
      "type": "string",
      "description": "Data source or session ID"
    },
    "analysis_type": {
      "type": "string",
      "enum": ["churn_rate", "arpu", "network_quality", "correlation"],
      "description": "Type of analysis to perform"
    },
    "parameters": {
      "type": "object",
      "description": "Analysis-specific parameters"
    }
  },
  "required": ["data_source", "analysis_type"]
}
```

**Output Schema**:
```json
{
  "analysis_type": "churn_rate",
  "results": {
    "overall_churn_rate": 0.153,
    "by_segment": {...}
  },
  "metadata": {
    "data_source": "session_123",
    "row_count": 10000,
    "timestamp": "2026-01-17T10:00:00Z"
  }
}
```

#### Tool: create_visualization

**Purpose**: Generate charts and graphs

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "data": {
      "type": "object",
      "description": "Data to visualize"
    },
    "chart_type": {
      "type": "string",
      "enum": ["bar", "line", "scatter", "histogram", "heatmap"],
      "description": "Type of chart"
    },
    "title": {
      "type": "string",
      "description": "Chart title"
    },
    "x_axis": {
      "type": "string",
      "description": "X-axis column"
    },
    "y_axis": {
      "type": "string",
      "description": "Y-axis column"
    },
    "format": {
      "type": "string",
      "enum": ["png", "svg", "html"],
      "default": "png"
    }
  },
  "required": ["data", "chart_type"]
}
```

**Output Schema**:
```json
{
  "image": "base64_encoded_image",
  "format": "png",
  "dimensions": {"width": 800, "height": 600}
}
```

#### Tool: session_create

**Purpose**: Create new data access session

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "data_source": {
      "type": "string",
      "description": "Data source identifier"
    },
    "access_level": {
      "type": "string",
      "enum": ["read", "write"],
      "default": "read"
    },
    "ttl_seconds": {
      "type": "integer",
      "default": 3600,
      "description": "Session TTL in seconds"
    },
    "user_id": {
      "type": "string",
      "description": "Optional user identifier"
    }
  },
  "required": ["data_source"]
}
```

**Output Schema**:
```json
{
  "session_id": "uuid",
  "created_at": "ISO-8601 timestamp",
  "expires_at": "ISO-8601 timestamp",
  "status": "active"
}
```

#### Tool: session_read

**Purpose**: Read data from active session

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "session_id": {
      "type": "string",
      "description": "Session identifier"
    },
    "key": {
      "type": "string",
      "description": "Data key to read"
    }
  },
  "required": ["session_id", "key"]
}
```

#### Tool: session_update

**Purpose**: Update session data

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "session_id": {
      "type": "string",
      "description": "Session identifier"
    },
    "key": {
      "type": "string",
      "description": "Data key"
    },
    "value": {
      "description": "Data value (any JSON serializable type)"
    }
  },
  "required": ["session_id", "key", "value"]
}
```

#### Tool: session_close

**Purpose**: Close and cleanup session

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "session_id": {
      "type": "string",
      "description": "Session identifier"
    },
    "archive": {
      "type": "boolean",
      "default": true,
      "description": "Whether to archive session data"
    }
  },
  "required": ["session_id"]
}
```

### 3.2 MCP Resources

#### Resource: database_schema
- **URI**: `schema://database/main`
- **MIME Type**: `text/markdown`
- **Description**: Complete database schema documentation

#### Resource: analysis_templates
- **URI**: `templates://analysis/{type}`
- **MIME Type**: `application/json`
- **Description**: Analysis configuration templates

#### Resource: data_dictionary
- **URI**: `docs://data_dictionary`
- **MIME Type**: `text/markdown`
- **Description**: Data field definitions and business rules

### 3.3 MCP Prompts

#### Prompt: churn_analysis
- **Name**: `churn_analysis`
- **Description**: Step-by-step customer churn analysis workflow
- **Arguments**: None

#### Prompt: network_analysis
- **Name**: `network_analysis`
- **Description**: Network performance analysis workflow
- **Arguments**: None

#### Prompt: revenue_optimization
- **Name**: `revenue_optimization`
- **Description**: Revenue analysis and optimization workflow
- **Arguments**: None

---

## 4. Security Architecture

### 4.1 Authentication

```
┌───────────┐
│ AI Agent  │
└─────┬─────┘
      │ API Key (X-API-Key header)
      ▼
┌────────────────────┐
│  API Gateway       │
│  (FastAPI)         │
└─────┬──────────────┘
      │ Validate API Key
      ▼
┌────────────────────┐
│  MCP Server        │
└────────────────────┘
```

**API Key Management**:
- Store hashed API keys in environment variables
- Rotate keys periodically
- Log all authentication attempts
- Rate limit by API key

### 4.2 Authorization

**Role-Based Access Control (RBAC)**:
- **Admin**: Full access to all tools and data
- **Analyst**: Read-only data access, create sessions
- **Viewer**: Read-only session access

**Implementation**:
```python
@require_role(['Admin', 'Analyst'])
async def query_database(input: QueryInput):
    pass

@require_role(['Admin'])
async def delete_session(session_id: str):
    pass
```

### 4.3 Data Protection

#### At Rest
- Encrypt sensitive session data with Fernet (AES-128)
- Use PostgreSQL encryption for PII columns
- Secure Redis with authentication and TLS

#### In Transit
- All connections use TLS 1.3
- MCP protocol over HTTPS
- Database connections over SSL

#### In Logs
- Mask PII in application logs
- Never log full SQL parameters
- Sanitize error messages

### 4.4 SQL Injection Prevention

```python
# BAD - String concatenation
query = f"SELECT * FROM customers WHERE age > {age}"

# GOOD - Parameterized query
query = "SELECT * FROM customers WHERE age > %(age)s"
result = await conn.fetch(query, age=age)
```

**Additional Safeguards**:
- Input validation with Pydantic
- Query allowlist for common patterns
- Prohibit multiple statements
- Reject queries with comments

---

## 5. Performance Considerations

### 5.1 Database Optimization

**Connection Pooling**:
```python
pool = await asyncpg.create_pool(
    host=DB_HOST,
    min_size=5,
    max_size=20,
    command_timeout=60
)
```

**Query Optimization**:
- Index frequently queried columns
- Use EXPLAIN ANALYZE for slow queries
- Implement pagination for large result sets
- Cache frequent queries in Redis

**Example Indexes**:
```sql
CREATE INDEX idx_customers_churned_created 
ON customers(is_churned, created_at);

CREATE INDEX idx_network_events_customer_timestamp 
ON network_events(customer_id, event_timestamp);
```

### 5.2 Caching Strategy

**Redis Caching Layers**:
1. **Query Result Cache**: Cache frequent query results (TTL: 5 minutes)
2. **Analysis Cache**: Cache expensive analysis results (TTL: 1 hour)
3. **Session Data**: Temporary session contexts (TTL: configurable)

**Cache Invalidation**:
- Time-based expiration (TTL)
- Event-based invalidation (on data updates)
- Manual cache clear for admin operations

### 5.3 Async Operations

**All I/O operations are async**:
```python
# Database queries
result = await pool.fetch(query)

# Redis operations
value = await redis.get(key)

# File operations
async with aiofiles.open(path) as f:
    content = await f.read()
```

**Benefits**:
- Handle multiple concurrent requests
- Non-blocking I/O for better throughput
- Efficient resource utilization

---

## 6. Scalability

### 6.1 Horizontal Scaling

**MCP Server**:
- Stateless design allows multiple instances
- Load balance with nginx or AWS ALB
- Share session state via Redis cluster

**Database**:
- Read replicas for query distribution
- Partition large tables by date or region
- Use connection pooling per instance

**Redis**:
- Redis Cluster for distributed caching
- Sentinel for high availability
- Separate cache and session Redis instances

### 6.2 Vertical Scaling

**MCP Server**:
- Increase worker processes
- Allocate more CPU/memory
- Use uvloop for faster async

**Database**:
- Increase connection pool size
- Optimize query execution plans
- Add more CPU/RAM for complex queries

### 6.3 Data Volume Handling

**Strategies**:
- Stream large datasets instead of loading to memory
- Use chunked processing for file imports
- Implement data retention policies
- Archive old data to cold storage

---

## 7. Monitoring and Observability

### 7.1 Metrics

**Application Metrics**:
- Request latency (p50, p95, p99)
- Error rate by tool
- Active session count
- Cache hit/miss ratio
- Database query performance

**Infrastructure Metrics**:
- CPU and memory usage
- Database connection pool utilization
- Redis memory usage
- Network I/O

**Business Metrics**:
- Analysis requests per day
- Most used tools
- Average session duration
- Data volume processed

### 7.2 Logging

**Log Levels**:
- **DEBUG**: Detailed diagnostic information
- **INFO**: Significant events (tool invocations, sessions)
- **WARNING**: Unexpected but handled events
- **ERROR**: Errors that affect functionality
- **CRITICAL**: System failures

**Structured Logging**:
```python
logger.info(
    "Tool invoked",
    extra={
        'tool_name': 'query_database',
        'user_id': user_id,
        'session_id': session_id,
        'execution_time_ms': 150
    }
)
```

### 7.3 Distributed Tracing

**OpenTelemetry Integration**:
- Trace requests across MCP server, database, Redis
- Identify bottlenecks in request flow
- Visualize dependencies with Jaeger

---

## 8. Deployment Architecture

### 8.1 Local Development

```
docker-compose.yml:
  - mcp-server (FastMCP app)
  - postgresql (database)
  - redis (session storage)
  - pgadmin (database management)
  - redis-commander (Redis management)
```

### 8.2 Production (Future)

```
┌──────────────────────────────────┐
│      Load Balancer (ALB)         │
└────────────┬─────────────────────┘
             │
     ┌───────┴────────┐
     │                │
┌────▼─────┐    ┌────▼─────┐
│ MCP      │    │ MCP      │
│ Server 1 │    │ Server 2 │
└────┬─────┘    └────┬─────┘
     │               │
     └───────┬───────┘
             │
     ┌───────┴────────┐
     │                │
┌────▼─────┐    ┌────▼─────┐
│PostgreSQL│    │  Redis   │
│ (Primary)│    │ Cluster  │
└────┬─────┘    └──────────┘
     │
┌────▼─────┐
│PostgreSQL│
│(Replica) │
└──────────┘
```

---

## 9. Testing Strategy

### 9.1 Unit Tests
- Test individual tool functions
- Mock external dependencies
- Aim for >80% coverage

### 9.2 Integration Tests
- Test end-to-end workflows
- Use test database with sample data
- Verify tool interactions

### 9.3 Performance Tests
- Load testing with 100+ concurrent requests
- Stress testing to find limits
- Database query performance validation

### 9.4 Security Tests
- SQL injection attempt tests
- Authentication bypass tests
- Authorization tests for RBAC

---

## 10. Future Enhancements

1. **Real-time Data Streaming**: Integrate Kafka for live data ingestion
2. **ML Model Deployment**: Add tool for deploying trained models
3. **Natural Language to SQL**: Convert natural language queries to SQL
4. **Advanced Visualizations**: Interactive dashboards with Plotly Dash
5. **Multi-tenancy**: Support multiple organizations with data isolation
6. **Data Quality Monitoring**: Automated data quality checks
7. **Automated Reporting**: Schedule and distribute reports
8. **Cloud Deployment**: AWS/Azure/GCP deployment guides

---

**Document Status**: Ready for Implementation
