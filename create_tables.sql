CREATE TABLE category (
category_id VARCHAR(20) PRIMARY KEY, 
category_name VARCHAR(100) NOT NULL
); 

CREATE TABLE channel (
    channel_id VARCHAR(20) PRIMARY KEY,
    channel_name VARCHAR(100) NOT NULL
);

CREATE TABLE store (
    store_id VARCHAR(20) PRIMARY KEY,
    store_city VARCHAR(100) NOT NULL,
    store_state VARCHAR(100) NOT NULL,
    store_type VARCHAR(50) NOT NULL
);

CREATE TABLE customer (
    customer_id VARCHAR(20) PRIMARY KEY,
    signup_date DATE NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    segment VARCHAR(50)
);

CREATE TABLE promotion (
    promo_id VARCHAR(20) PRIMARY KEY,
    promo_type VARCHAR(100),
    start_date DATE,
    end_date DATE,
    discount_value DECIMAL(8,2)
);

CREATE TABLE product (
product_id VARCHAR(20) PRIMARY KEY, 
category_id VARCHAR(20), 
brand VARCHAR(100) NOT NULL,
sku_name VARCHAR(100) NOT NULL, 
CONSTRAINT fk_product_category
FOREIGN KEY (category_id)
REFERENCES category(category_id)
); 

CREATE TABLE "order" (
    order_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    order_date DATE NOT NULL,
    store_id VARCHAR(20) NOT NULL,
    channel_id VARCHAR(20) NOT NULL,
    payment_type VARCHAR(50),
    year SMALLINT,
    week SMALLINT,

    CONSTRAINT fk_order_customer
        FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id),

    CONSTRAINT fk_order_store
        FOREIGN KEY (store_id)
        REFERENCES store(store_id),

    CONSTRAINT fk_order_channel
        FOREIGN KEY (channel_id)
        REFERENCES channel(channel_id)
);

CREATE TABLE order_item (
    order_item_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,

    CONSTRAINT fk_orderitem_order
        FOREIGN KEY (order_id)
        REFERENCES "order"(order_id),

    CONSTRAINT fk_orderitem_product
        FOREIGN KEY (product_id)
        REFERENCES product(product_id)
);

CREATE TABLE price_change (
    product_id VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL,
    week INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,

    PRIMARY KEY(product_id, year, week),

    CONSTRAINT fk_price_product
        FOREIGN KEY (product_id)
        REFERENCES product(product_id)
);

CREATE TABLE customer_session (
    session_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    session_start TIMESTAMP NOT NULL,
    session_duration_sec INTEGER,
    pages_viewed INTEGER,
    device VARCHAR(50),
    referrer VARCHAR(100),

    CONSTRAINT fk_session_customer
        FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id)
);

CREATE TABLE support_ticket (
    ticket_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    created_date DATE,
    issue_type VARCHAR(100),
    status VARCHAR(50),
    resolution_time_hr INTEGER,
    csat_score INTEGER,

    CONSTRAINT fk_ticket_customer
        FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id)
);

CREATE TABLE campaign_touch (
    touch_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    touch_date DATE,
    channel VARCHAR(50),
    campaign_name VARCHAR(150),
    outcome VARCHAR(50),

    CONSTRAINT fk_touch_customer
        FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id)
);

CREATE TABLE external_factor (
    factor_id VARCHAR(20) PRIMARY KEY,
    store_id VARCHAR(20) NOT NULL,
    factor_date DATE,
    is_holiday BOOLEAN,
    temp_c DECIMAL(5,2),
    rainfall_mm DECIMAL(8,2),
    trend_index DECIMAL(8,2),
    cpi_index DECIMAL(8,2),
    year INTEGER,
    week INTEGER,

    CONSTRAINT fk_factor_store
        FOREIGN KEY (store_id)
        REFERENCES store(store_id)
);

