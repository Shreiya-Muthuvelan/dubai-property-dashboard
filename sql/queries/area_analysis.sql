
--What are the top 10 areas by transaction count?
SELECT area_name_en AS area_name, COUNT(transaction_id) AS transaction_count FROM vw_transactions_clean GROUP BY area_name 
ORDER BY transaction_count DESC LIMIT 10;

-- What are the top 10 areas by average price?
SELECT area_name_en AS area_name, ROUND(AVG(actual_worth),2) AS average_price FROM vw_transactions_clean GROUP BY area_name 
ORDER BY average_price DESC LIMIT 10;

-- What are the top 10 areas by total transaction value?
SELECT area_name_en AS area_name, ROUND(SUM(actual_worth),2) AS total_transaction_value FROM vw_transactions_clean GROUP BY area_name 
ORDER BY total_transaction_value DESC LIMIT 10;

--For a specific area (pick one, e.g. "Dubai Marina"), what's the average price per sqft compared to the overall market average?
WITH avg_sqft_area(area_name,average_price_per_sqft)
AS (SELECT area_name_en,ROUND(AVG(meter_sale_price),2) AS average_price_per_sqft FROM vw_transactions_clean GROUP BY area_name_en),
avg_value(average_market_value_per_sqft) AS (SELECT ROUND(AVG(meter_sale_price),2) FROM vw_transactions_clean)
SELECT * FROM avg_sqft_area 
CROSS JOIN avg_value;

-- Which areas have the highest price volatility (hint: standard deviation of actual_worth per area — STDDEV)?*/
SELECT area_name_en,ROUND(AVG(actual_worth),2) AS avg_prices, ROUND(STDDEV(actual_worth), 2) AS price_stddev FROM vw_transactions_clean
GROUP BY area_name_en ORDER BY price_stddev DESC LIMIT 10;