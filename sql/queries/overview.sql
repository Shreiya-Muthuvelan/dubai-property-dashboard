
-- What is the total number of transactions in the dataset? 
SELECT COUNT(*) AS total_records FROM vw_transactions_clean;

-- What is the total transaction value (sum of actual_worth) across all transactions?
SELECT SUM(actual_worth) AS total_transaction_value FROM vw_transactions_clean;

-- What is the average and median transaction price?
SELECT ROUND(AVG(actual_worth),2) AS avg_transaction_price , MEDIAN(actual_worth) AS median_transaction_value FROM 
vw_transactions_clean;

--What is the average price per sqft (actual_worth / procedure_area) across all transactions?
SELECT ROUND(AVG(meter_sale_price),2) AS average_price_per_sqft FROM vw_transactions_clean;

-- How many distinct areas are represented?
SELECT COUNT(DISTINCT area_name_en) AS number_of_areas FROM vw_transactions_clean;

-- Whats the breakdown of transaction count by trans_group_en (sale vs rent vs mortgage etc.)?
SELECT trans_group_en,COUNT(transaction_id) AS transaction_count FROM vw_transactions_clean GROUP BY trans_group_en;
