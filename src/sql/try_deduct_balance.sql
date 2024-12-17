WITH user_exists AS (
    -- Check if the user exists
    SELECT EXISTS (SELECT 1 FROM "users" WHERE id = $1) AS exists
),
balance_checker AS (
    -- Check if the user has enough balance
    SELECT 
        id, 
        balance >= $2 AS has_enough
    FROM "users"
    WHERE id = $1
),
updated_user AS (
    -- Deduct balance if the user has enough
    UPDATE "users"
    SET balance = balance - $2
    FROM balance_checker
    WHERE "users".id = balance_checker.id 
      AND balance_checker.has_enough = TRUE
    RETURNING TRUE AS deducted
)
SELECT 
    CASE 
        WHEN NOT EXISTS (SELECT 1 FROM user_exists WHERE exists) THEN NULL     -- Return NULL if the user does not exist
        WHEN EXISTS (SELECT 1 FROM updated_user) THEN TRUE  -- Balance deducted
        ELSE FALSE  -- User exists, but insufficient balance
    END AS result
FROM user_exists
LEFT JOIN updated_user ON TRUE
LIMIT 1;