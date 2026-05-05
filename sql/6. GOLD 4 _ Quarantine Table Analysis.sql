-- GOLD 4: Quarantine Rows Analysis

CREATE OR REPLACE TABLE `payment-failure-495302.metro_payment_analysis.GOLD_4_Quarantine_Rows_Analysis` 
AS
WITH ORDERS_ERROR_TYPE AS (
  SELECT  
    "ORDERS" as table_name,
    CASE
      WHEN customer_id IS  NULL THEN "CUSTOMER ID IS NULL"
      WHEN order_amount IS  NULL THEN "ORDER AMOUNT IS NULL"
      WHEN order_amount <= 0 THEN "ORDER AMOUNT LESS THEN EQUAL ZERO"
      WHEN order_time IS NULL THEN "ORDER TIME IS NULL"
      WHEN SAFE_CAST(order_time AS TIMESTAMP) > CURRENT_TIMESTAMP() THEN "FUTURE_TIMESTAMP IN ORDER"
      ELSE "OTHER"
    END AS error_type
  FROM `payment-failure-495302.metro_payment_analysis.QUARANTINE_ORDERS` 
),
ORDERS_ERROR_MATRIX AS (
  SELECT table_name,
    error_type,
    COUNT(*) as error_type_count
  FROM ORDERS_ERROR_TYPE
  GROUP BY error_type,table_name
),
PAYMENTS_ERROR_TYPE AS (
  SELECT  
    "PAYMENT" as table_name,
    CASE
      WHEN order_id IS  NULL THEN "ORDER ID IS NULL"
      WHEN attempt_amount IS  NULL THEN "ATTEMPT AMOUNT IS NULL"
      WHEN attempt_amount <= 0 THEN "ATTEMPT AMOUNT LESS THEN EQUAL ZERO"
      WHEN attempt_time IS NULL THEN "ATTEMPT TIME IS NULL"
      WHEN SAFE_CAST(attempt_time AS TIMESTAMP) > CURRENT_TIMESTAMP() THEN "FUTURE_TIMESTAMP IN PAYMENTS"
      ELSE "OTHER"
    END AS error_type
  FROM `payment-failure-495302.metro_payment_analysis.QUARANTINE_PAYMENT` 
),
PAYMENTS_ERROR_MATRIX AS (
  SELECT table_name,
    error_type,
    COUNT(*) as error_type_count
  FROM PAYMENTS_ERROR_TYPE
  GROUP BY error_type,table_name
),
ERROR_MATRIX AS (
  SELECT * FROM PAYMENTS_ERROR_MATRIX
  UNION ALL (
    SELECT * FROM ORDERS_ERROR_MATRIX
  )
),
TOTAL_DATA AS (
  SELECT
    (SELECT COUNT(*) FROM `payment-failure-495302.metro_payment_analysis.orders`) AS total_rows_orders,
    (SELECT COUNT(*) FROM `payment-failure-495302.metro_payment_analysis.payment_attempts`) AS total_rows_payment
),
FINAL_ERROR_MATRIX AS (
  SELECT 
    EM.table_name,
    EM.error_type,
    EM.error_type_count,
    CASE 
      WHEN EM.table_name = "ORDERS" THEN ROUND(SAFE_DIVIDE(EM.error_type_count, T.total_rows_orders),2)
      WHEN EM.table_name = "PAYMENT" THEN ROUND(SAFE_DIVIDE(EM.error_type_count, T.total_rows_payment),2)
    END AS error_percentage
    FROM ERROR_MATRIX EM
    CROSS JOIN TOTAL_DATA T
  
)
SELECT * FROM FINAL_ERROR_MATRIX;