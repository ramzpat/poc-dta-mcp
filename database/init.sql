-- Database initialization script
-- Creates schema for telco analytics data

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    account_type VARCHAR(50) NOT NULL,
    subscription_start_date DATE NOT NULL,
    subscription_end_date DATE,
    monthly_fee DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create network_events table
CREATE TABLE IF NOT EXISTS network_events (
    event_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    event_type VARCHAR(50) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    data_usage_mb DECIMAL(10, 2),
    call_duration_minutes INTEGER,
    network_quality VARCHAR(20),
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create revenue table
CREATE TABLE IF NOT EXISTS revenue (
    revenue_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    transaction_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    payment_method VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
CREATE INDEX IF NOT EXISTS idx_customers_account_type ON customers(account_type);
CREATE INDEX IF NOT EXISTS idx_network_events_customer_id ON network_events(customer_id);
CREATE INDEX IF NOT EXISTS idx_network_events_event_timestamp ON network_events(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_revenue_customer_id ON revenue(customer_id);
CREATE INDEX IF NOT EXISTS idx_revenue_transaction_date ON revenue(transaction_date);

-- Create views for common analytics queries
CREATE OR REPLACE VIEW customer_summary AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    c.account_type,
    c.status,
    c.monthly_fee,
    COUNT(DISTINCT ne.event_id) as total_events,
    SUM(r.amount) as total_revenue
FROM customers c
LEFT JOIN network_events ne ON c.customer_id = ne.customer_id
LEFT JOIN revenue r ON c.customer_id = r.customer_id
GROUP BY c.customer_id, c.customer_name, c.email, c.account_type, c.status, c.monthly_fee;
