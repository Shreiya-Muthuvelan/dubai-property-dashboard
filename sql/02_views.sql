-- Create a clean view with just english columns
CREATE OR REPLACE VIEW vw_transactions_clean AS
                 SELECT * EXCLUDE (trans_group_ar, procedure_name_ar, property_type_ar,
                 property_sub_type_ar, property_usage_ar, reg_type_ar,area_name_ar, building_name_ar,
                 project_name_ar,master_project_ar, nearest_landmark_ar, nearest_metro_ar,nearest_mall_ar, rooms_ar
                 )FROM transactions WHERE instance_date IS NOT NULL
                   AND actual_worth IS NOT NULL AND actual_worth > 0
                   AND area_name_en IS NOT NULL
                   AND property_type_en IS NOT NULL
                   AND procedure_area IS NOT NULL AND procedure_area > 0 ;


CREATE VIEW vw_area_summary AS
SELECT area_name_en, COUNT(*) AS txn_count, AVG(actual_worth) AS avg_price
FROM vw_transactions_clean
GROUP BY area_name_en;

CREATE VIEW vw_monthly_trend AS
SELECT DATE_TRUNC('month', instance_date) AS month,
       trans_group_en, COUNT(*) AS txn_count, AVG(actual_worth) AS avg_price
FROM vw_transactions_clean
GROUP BY 1, 2;

CREATE VIEW vw_property_type_breakdown AS
SELECT property_type_en, property_sub_type_en,
       COUNT(*) AS txn_count, AVG(actual_worth) AS avg_price
FROM vw_transactions_clean
GROUP BY 1, 2;

CREATE VIEW vw_projects_lookup AS
SELECT DISTINCT project_number, project_name_en, master_project_en
FROM vw_transactions_clean
WHERE project_number IS NOT NULL;