-- Gold Table 2: Payment Retry Recovery
--- TABLE IN USE : SILVER_ORDER, SILVER_PAYMENT

-- COMBINE REQUIRED FIELD INTO ONE CTE

CREATE OR REPLACE TABLE `payment-failure-495302.metro_payment_analysis.GOLD_2_PAYMENT_RECOVERY` 
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
ATTEMPT_MATRIX AS (
  SELECT attempt_number, 
    COUNT(*) AS orders_reaching_attempt,
    SUM(
      CASE
        WHEN payment_status NOT IN ('CANCELLED', 'FAILED')
        THEN 1
        ELSE 0
      END
    ) AS orders_success_at_attempt,
    SUM(
      CASE
        WHEN payment_status NOT IN ('CANCELLED', 'FAILED') AND attempt_number > 1 
        THEN order_amount
        ELSE 0
      END
    ) AS recovered_revenue
    
  FROM ORDERS_WITH_OUTCOME
  GROUP BY attempt_number
)
SELECT * FROM ATTEMPT_MATRIX;