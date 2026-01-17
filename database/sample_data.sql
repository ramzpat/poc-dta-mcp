-- Sample data for telco analytics

-- Insert sample customers
INSERT INTO customers (customer_name, email, phone, account_type, subscription_start_date, monthly_fee, status) VALUES
('Alice Johnson', 'alice.johnson@email.com', '+1-555-0101', 'Premium', '2024-01-15', 79.99, 'active'),
('Bob Smith', 'bob.smith@email.com', '+1-555-0102', 'Standard', '2024-02-20', 49.99, 'active'),
('Charlie Brown', 'charlie.brown@email.com', '+1-555-0103', 'Basic', '2024-03-10', 29.99, 'active'),
('Diana Prince', 'diana.prince@email.com', '+1-555-0104', 'Premium', '2024-01-05', 79.99, 'active'),
('Edward Norton', 'edward.norton@email.com', '+1-555-0105', 'Standard', '2024-04-12', 49.99, 'churned'),
('Fiona Apple', 'fiona.apple@email.com', '+1-555-0106', 'Premium', '2023-12-01', 79.99, 'active'),
('George Martin', 'george.martin@email.com', '+1-555-0107', 'Basic', '2024-05-18', 29.99, 'active'),
('Hannah Montana', 'hannah.montana@email.com', '+1-555-0108', 'Standard', '2024-02-28', 49.99, 'active'),
('Ivan Drago', 'ivan.drago@email.com', '+1-555-0109', 'Premium', '2024-03-22', 79.99, 'suspended'),
('Julia Roberts', 'julia.roberts@email.com', '+1-555-0110', 'Basic', '2024-04-05', 29.99, 'active');

-- Insert sample network events
INSERT INTO network_events (customer_id, event_type, event_timestamp, data_usage_mb, call_duration_minutes, network_quality, location) VALUES
-- Alice Johnson events
(1, 'data', '2024-11-01 10:30:00', 150.5, NULL, 'excellent', 'New York'),
(1, 'call', '2024-11-01 14:20:00', NULL, 25, 'good', 'New York'),
(1, 'data', '2024-11-02 09:15:00', 200.3, NULL, 'excellent', 'New York'),
-- Bob Smith events
(2, 'data', '2024-11-01 08:00:00', 80.2, NULL, 'good', 'Los Angeles'),
(2, 'call', '2024-11-01 12:30:00', NULL, 15, 'fair', 'Los Angeles'),
(2, 'data', '2024-11-02 16:45:00', 120.5, NULL, 'good', 'Los Angeles'),
-- Charlie Brown events
(3, 'data', '2024-11-01 11:00:00', 45.8, NULL, 'fair', 'Chicago'),
(3, 'call', '2024-11-01 15:30:00', NULL, 10, 'poor', 'Chicago'),
-- Diana Prince events
(4, 'data', '2024-11-01 07:30:00', 300.7, NULL, 'excellent', 'Boston'),
(4, 'call', '2024-11-01 19:00:00', NULL, 45, 'excellent', 'Boston'),
(4, 'data', '2024-11-02 10:00:00', 250.4, NULL, 'excellent', 'Boston'),
-- Edward Norton events (churned user)
(5, 'data', '2024-10-15 14:00:00', 50.2, NULL, 'fair', 'Seattle'),
(5, 'call', '2024-10-15 18:30:00', NULL, 5, 'poor', 'Seattle'),
-- Fiona Apple events
(6, 'data', '2024-11-01 09:00:00', 180.5, NULL, 'good', 'Miami'),
(6, 'call', '2024-11-01 13:45:00', NULL, 30, 'excellent', 'Miami'),
(6, 'data', '2024-11-02 11:30:00', 220.8, NULL, 'excellent', 'Miami'),
-- George Martin events
(7, 'data', '2024-11-01 10:00:00', 60.3, NULL, 'good', 'Austin'),
(7, 'call', '2024-11-01 16:00:00', NULL, 12, 'good', 'Austin'),
-- Hannah Montana events
(8, 'data', '2024-11-01 12:00:00', 95.6, NULL, 'good', 'Nashville'),
(8, 'call', '2024-11-01 17:30:00', NULL, 20, 'fair', 'Nashville'),
-- Ivan Drago events (suspended)
(9, 'data', '2024-10-28 15:00:00', 100.2, NULL, 'excellent', 'Denver'),
(9, 'call', '2024-10-28 20:00:00', NULL, 8, 'good', 'Denver'),
-- Julia Roberts events
(10, 'data', '2024-11-01 08:30:00', 70.4, NULL, 'fair', 'Portland'),
(10, 'call', '2024-11-01 14:00:00', NULL, 18, 'good', 'Portland');

-- Insert sample revenue transactions
INSERT INTO revenue (customer_id, transaction_date, amount, transaction_type, payment_method, description) VALUES
-- Monthly subscription payments
(1, '2024-11-01', 79.99, 'subscription', 'credit_card', 'Monthly Premium subscription'),
(2, '2024-11-01', 49.99, 'subscription', 'credit_card', 'Monthly Standard subscription'),
(3, '2024-11-01', 29.99, 'subscription', 'debit_card', 'Monthly Basic subscription'),
(4, '2024-11-01', 79.99, 'subscription', 'credit_card', 'Monthly Premium subscription'),
(6, '2024-11-01', 79.99, 'subscription', 'credit_card', 'Monthly Premium subscription'),
(7, '2024-11-01', 29.99, 'subscription', 'paypal', 'Monthly Basic subscription'),
(8, '2024-11-01', 49.99, 'subscription', 'credit_card', 'Monthly Standard subscription'),
(10, '2024-11-01', 29.99, 'subscription', 'debit_card', 'Monthly Basic subscription'),
-- Additional charges
(1, '2024-11-05', 15.00, 'overage', 'credit_card', 'Data overage charges'),
(4, '2024-11-08', 25.00, 'overage', 'credit_card', 'International call charges'),
(6, '2024-11-10', 10.00, 'overage', 'credit_card', 'Extra data package'),
-- Previous month payments
(1, '2024-10-01', 79.99, 'subscription', 'credit_card', 'Monthly Premium subscription'),
(2, '2024-10-01', 49.99, 'subscription', 'credit_card', 'Monthly Standard subscription'),
(3, '2024-10-01', 29.99, 'subscription', 'debit_card', 'Monthly Basic subscription'),
(4, '2024-10-01', 79.99, 'subscription', 'credit_card', 'Monthly Premium subscription'),
(5, '2024-10-01', 49.99, 'subscription', 'credit_card', 'Monthly Standard subscription'),
(6, '2024-10-01', 79.99, 'subscription', 'credit_card', 'Monthly Premium subscription'),
(7, '2024-10-01', 29.99, 'subscription', 'paypal', 'Monthly Basic subscription'),
(8, '2024-10-01', 49.99, 'subscription', 'credit_card', 'Monthly Standard subscription'),
(9, '2024-10-01', 79.99, 'subscription', 'credit_card', 'Monthly Premium subscription'),
(10, '2024-10-01', 29.99, 'subscription', 'debit_card', 'Monthly Basic subscription');
