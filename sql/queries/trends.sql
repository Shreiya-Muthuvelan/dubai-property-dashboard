-- What is the monthly transaction count and average price for the last 12 months?
SELECT EXTRACT(MONTH FROM instance_date) AS month, COUNT(transaction_id) AS transaction_count, ROUND(AVG(actual_worth),2) AS average_price 
FROM vw_transactions_clean GROUP BY EXTRACT(MONTH FROM instance_date);

-- Is there a month-over-month percentage change in average price? (hint: window function LAG)
SELECT EXTRACT(MONTH FROM instance_date) AS month, COUNT(transaction_id) AS transaction_count, 
ROUND(AVG(actual_worth),2) AS average_price, LAG(average_price) 
OVER(ORDER BY month) AS lag_avg_price,
ROUND(((average_price-lag_avg_price)/lag_avg_price)*100,2) as monthly_change
FROM vw_transactions_clean GROUP BY EXTRACT(MONTH FROM instance_date);

-- What is the 3-month rolling average of transaction volume?
SELECT EXTRACT(MONTH FROM instance_date) AS month, COUNT(transaction_id) AS transaction_volume_for_month,
ROUND(AVG(transaction_volume_for_month),2) OVER(ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_3_mnth_avg 
FROM vw_transactions_clean GROUP BY month;

--Which month had the highest total transaction value?
WITH monthly_transaction(month,transaction_value) AS (SELECT EXTRACT(MONTH FROM instance_date) 
AS month,SUM(actual_worth) AS transaction_value
FROM vw_transactions_clean GROUP BY month)
SELECT * FROM monthly_transaction ORDER BY transaction_value DESC LIMIT 1;

--Compare average prices year-over-year for the same month (e.g. Jan 2024 vs Jan 2025) 
SELECT EXTRACT(YEAR FROM instance_date) AS year_label,EXTRACT(MONTH FROM instance_date) AS month_label ,ROUND(AVG(actual_worth),2)
AS avg_prices , LAG(avg_prices) OVER (PARTITION BY (month_label)
ORDER BY year_label )as avg_price_prev_year FROM vw_transactions_clean
GROUP BY year_label,month_label;
