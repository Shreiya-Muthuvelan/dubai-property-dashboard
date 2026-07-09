
-- What is the median, 25th percentile, and 75th percentile price overall? (hint: PERCENTILE_CONT)
SELECT QUANTILE_CONT(actual_worth,0.5) as median_price,QUANTILE_CONT(actual_worth,0.25) as quantile_25,
QUANTILE_CONT(actual_worth,0.74) as quantile_75 FROM vw_transactions_clean;

-- What does the price distribution look like in buckets (e.g. <500K, 500K–1M, 1M–2M, 2M+)? 
SELECT 
    CASE 
        WHEN actual_worth < 500000 THEN '< 500K'
        WHEN actual_worth < 1000000 THEN '500K - 1M'
        WHEN actual_worth < 2000000 THEN '1M - 2M'
        WHEN actual_worth < 5000000 THEN '2M - 5M'
        ELSE '5M+'
END AS price_bucket,COUNT(*) AS transaction_count
FROM vw_transactions_clean GROUP BY price_bucket ORDER BY MIN(actual_worth);  

-- What are the outlier transactions — e.g. top 1% most expensive, using QUALIFY with a window function?
SELECT area_name_en, property_type_en, actual_worth, procedure_area,PERCENT_RANK() OVER (ORDER BY actual_worth) AS pct_rank
FROM vw_transactions_clean QUALIFY pct_rank >= 0.99 ORDER BY actual_worth DESC;