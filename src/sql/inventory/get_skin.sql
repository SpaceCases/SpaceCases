-- Get a skin from a user by name, does an existence check which locks the row
WITH user_exists AS (
    SELECT EXISTS (SELECT 1 FROM "users" WHERE id = ($1) FOR UPDATE) AS user_exists
),
skins AS (
    SELECT float
    FROM skins
    WHERE owner_id = $1 AND name = $2
)
SELECT 
    (SELECT user_exists FROM user_exists) AS user_exists,
    ARRAY(
        SELECT float
        FROM skins
    ) AS skins