-- Create table for storing stock information
CREATE TABLE IF NOT EXISTS allStock (
    id SERIAL PRIMARY KEY,
    stock_name VARCHAR(100) NOT NULL,
    stock_symbol VARCHAR(10) NOT NULL UNIQUE,
    quantity INT NOT NULL,
    purchase_price DECIMAL(10, 2) NOT NULL,
    purchase_date DATE NOT NULL
);

-- Create table for storing user information
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a trigger to update the `updated_at` column automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


