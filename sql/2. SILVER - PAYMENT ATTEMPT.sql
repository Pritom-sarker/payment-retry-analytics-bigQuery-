
--- CLEAN INVALID ROWS FROM PAYMENT TABLE
CREATE OR REPLACE TABLE `payment-failure-495302.metro_payment_analysis.SILVER_PAYMENTS`
PARTITION BY DATE(attempt_time_ts)
CLUSTER BY payment_method
AS
WITH DRAFT_PAYMENTS AS (
  SELECT *,
        SAFE_CAST(attempt_time AS TIMESTAMP) AS attempt_time_ts,
        ROW_NUMBER() OVER(
          PARTITION BY order_id, attempt_number, payment_method
        ) AS RANK_
  FROM `payment-failure-495302.metro_payment_analysis.payment_attempts`
  WHERE order_id IS NOT NULL
    AND attempt_amount IS NOT NULL
    AND attempt_amount > 0
    AND attempt_time IS NOT NULL
    AND attempt_amount != 0
    AND SAFE_CAST(attempt_time AS TIMESTAMP) < CURRENT_TIMESTAMP()
)
--- REMOVE DUPLICATE ROWS FROM PAYMENT TABLE
SELECT * FROM DRAFT_PAYMENTS
WHERE RANK_ = 1;

-- --- SAVE THE INVALID ROWS INTO A QUARANTINE TABLE
CREATE OR REPLACE TABLE `payment-failure-495302.metro_payment_analysis.QUARANTINE_PAYMENT`
PARTITION BY  DATE(attempt_time)
CLUSTER BY payment_method
AS (
  SELECT PA.*,
    CP.RANK_
  FROM `payment-failure-495302.metro_payment_analysis.payment_attempts` PA
  LEFT JOIN `payment-failure-495302.metro_payment_analysis.SILVER_PAYMENTS` CP
  ON pa.payment_attempt_id = CP.payment_attempt_id
  WHERE  CP.payment_attempt_id IS NULL
);