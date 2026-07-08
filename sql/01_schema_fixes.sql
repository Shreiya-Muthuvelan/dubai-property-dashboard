
ALTER TABLE transactions ALTER COLUMN has_parking SET DATA TYPE BOOLEAN USING (has_parking::BOOLEAN);
ALTER TABLE transactions ALTER COLUMN instance_date SET DATA TYPE DATE USING (instance_date::DATE);
ALTER TABLE transactions ALTER COLUMN actual_worth TYPE DOUBLE USING TRY_CAST(actual_worth AS DOUBLE);