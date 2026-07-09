PIVOT (SELECT * FROM vw_transactions_clean WHERE area_name_en IN (SELECT area_name_en FROM vw_transactions_clean 
GROUP BY area_name_en ORDER BY COUNT(*) DESC LIMIT 15)) ON property_type_en USING ROUND(AVG(actual_worth), 2)
GROUP BY area_name_en;