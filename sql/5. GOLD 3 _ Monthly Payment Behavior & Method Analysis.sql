-- Gold Table 3: Monthly Payment Behavior & Method Analysis
--- TABLE IN USE : SILVER_ORDER, SILVER_PAYMENT

-- COMBINE REQUIRED FIELD INTO ONE CTE

CREATE OR REPLACE TABLE `payment-failure-495302.metro_payment_analysis.GOLD_3_Monthly_Payment_Behavior` 
AS
WITH ORDERS_PAYMENT_STATUS AS(
  SELECT ORD.order_id,
    ORD.order_time_ts,
    ORD.order_amount,
    ORD.store_location,
    PAY.attempt_number,
    PAY.payment_status,
    PAY.attempt_time,
    PAY.payment_method,
    FORMAT_TIMESTAMP("%Y-%m", order_time_ts) AS YEAR_MONTH
  FROM `payment-failure-495302.metro_payment_analysis.SILVER_ORDERS` ORD
  LEFT JOIN `payment-failure-495302.metro_payment_analysis.SILVER_PAYMENTS` PAY
  ON ORD.order_id = PAY.order_id
  WHERE PAY.attempt_number IS NOT NULL 
  AND PAY.payment_status IS NOT NULL
),
MONTHLY_MATRIX AS (
  SELECT YEAR_MONTH,
    attempt_number,
    payment_method,
    COUNT(*) AS total_attempts,
    SUM(
      CASE
        WHEN payment_status IN ('SUCCESS')
        THEN 1
        ELSE 0
      END
    ) AS success_count
  FROM ORDERS_PAYMENT_STATUS
  GROUP BY YEAR_MONTH,
    attempt_number,
    payment_method
),
MONTHLY_MATRIX_WITH_SUCCESS AS (
  SELECT *,
    ROUND(SAFE_DIVIDE(success_count, total_attempts),2)  AS success_rate
  FROM MONTHLY_MATRIX
),
MONTHLY_SUCCESS_COMPARISON AS (
  SELECT *,
    ROUND(success_rate - LAG(success_rate) OVER(
      PARTITION BY attempt_number,payment_method
      ORDER BY YEAR_MONTH ASC
    ),2) AS Success_Rate_Change
  FROM MONTHLY_MATRIX_WITH_SUCCESS
)
SELECT * FROM MONTHLY_SUCCESS_COMPARISON;