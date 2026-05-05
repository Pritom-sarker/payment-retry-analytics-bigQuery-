--- STEP 1 : CLEAN THE TABLES 

-- CLEAN ORDER TABLE REMOVE NULL ROWS, CLEAN AND FILTER INVALID ROWS
CREATE OR REPLACE TABLE `payment-failure-495302.metro_payment_analysis.silver_orders`
PARTITION BY DATE(order_time_ts)
CLUSTER BY customer_id, store_location
AS (
SELECT *,
      SAFE_CAST(order_time AS TIMESTAMP) AS order_time_ts
FROM `payment-failure-495302.metro_payment_analysis.orders`
WHERE customer_id IS NOT NULL
  AND order_amount IS NOT NULL
  AND order_amount > 0
  AND order_time IS NOT NULL
  AND order_amount != 0
  AND SAFE_CAST(order_time AS TIMESTAMP) < CURRENT_TIMESTAMP() );

--- INVALID ROWS SAVING ON QUARANTINE TABLE FOR API ERROR ANALYSIS

CREATE OR REPLACE TABLE `payment-failure-495302.metro_payment_analysis.QUARANTINE_ORDERS`
PARTITION BY DATE(order_time)
CLUSTER BY customer_id, store_location
AS(
SELECT * FROM `payment-failure-495302.metro_payment_analysis.orders` orders 
WHERE NOT EXISTS (
  SELECT 1 
  FROM `payment-failure-495302.metro_payment_analysis.silver_orders` CO
  WHERE orders.order_id = CO.order_id
));
