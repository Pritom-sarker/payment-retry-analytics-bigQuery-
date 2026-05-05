-- Gold Table 1: Store-Level Revenue Leakage
--- TABLE IN USE : SILVER_ORDER, SILVER_PAYMENT

-- COMBINE REQUIRED FIELD INTO ONE CTE

CREATE OR REPLACE TABLE `payment-failure-495302.metro_payment_analysis.GOLD_1_STORE_LEVEL_ANALYSIS` 
AS
WITH ORDERS_PAYMENT_STATUS AS(
  SELECT ORD.order_id,
    ORD.order_amount,
    ORD.store_location,
    PAY.attempt_number,
    PAY.payment_status,
    PAY.attempt_time
  FROM `payment-failure-495302.metro_payment_analysis.SILVER_ORDERS` ORD
  LEFT JOIN `payment-failure-495302.metro_payment_analysis.SILVER_PAYMENTS` PAY
  ON ORD.order_id = PAY.order_id
  WHERE PAY.attempt_number IS NOT NULL 
  AND PAY.payment_status IS NOT NULL
),
RANK_ORDERS_PAYMENT_STATUS AS (
  SELECT *,
    ROW_NUMBER() OVER(
      PARTITION BY order_id
      ORDER BY attempt_number DESC
    ) AS rank_
  FROM ORDERS_PAYMENT_STATUS
),
ORDERS_WITH_OUTCOME AS  (
  SELECT * 
  FROM RANK_ORDERS_PAYMENT_STATUS 
  WHERE RANK_ = 1
),
STORE_ORDER_MATRIX AS (
  SELECT store_location,
    SUM(
      CASE
        WHEN payment_status IN ('CANCELLED', 'FAILED')
        THEN order_amount
        ELSE 0
      END
    ) AS lost_revenue,
    SUM(
      CASE
        WHEN attempt_number > 1 AND payment_status NOT IN ('CANCELLED', 'FAILED')
        THEN order_amount
        ELSE 0
      END
    ) AS recovered_revenue,
    SUM(order_amount) AS total_order_value
  FROM ORDERS_WITH_OUTCOME
  GROUP BY store_location
),
GOLD_STORE_LEVEL_MATRIX AS (
  SELECT *,
    ROUND(lost_revenue/total_order_value,2) AS leakage_rate
  FROM STORE_ORDER_MATRIX
)
SELECT * FROM GOLD_STORE_LEVEL_MATRIX;