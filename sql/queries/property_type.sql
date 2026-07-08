-- What's the transaction count and average price broken down by property_type_en?
SELECT property_type_en, COUNT(transaction_id) AS transaction_count, ROUND(AVG(actual_worth),2) AS average_price 
FROM vw_transactions_clean GROUP BY property_type_en;

--Within each property type, what's the breakdown by property_sub_type_en?
SELECT property_type_en,property_sub_type_en,COUNT(transaction_id) AS transaction_count, ROUND(AVG(actual_worth),2) AS average_price 
FROM vw_transactions_clean GROUP BY property_type_en,property_sub_type_en;

--What percentage of total transactions does each property type represent?
SELECT property_type_en,COUNT(transaction_id) AS transaction_count,
ROUND((transaction_count / (SELECT COUNT(*) FROM vw_transactions_clean)) * 100, 2) AS pct_of_transactions
FROM vw_transactions_clean GROUP BY property_type_en;

-- Compare average price of properties WHERE has_parking = TRUE vs FALSE.
SELECT has_parking,ROUND(AVG(actual_worth),2) AS average_price FROM vw_transactions_clean GROUP BY has_parking;

