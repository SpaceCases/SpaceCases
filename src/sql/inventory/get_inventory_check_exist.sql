-- Get items from users inventory, while also checking the user exists and their inventory capacity.
-- Will lock the user row for the duration of the query
WITH user_exists AS (
    SELECT EXISTS (SELECT 1 FROM "users" WHERE id = ($1) FOR UPDATE) AS user_exists
),
user_capacity AS (
    SELECT inventory_capacity
    FROM "users"
    WHERE id = $1
),
skins AS (
    SELECT name, float
    FROM skins
    WHERE owner_id = $1
),
stickers AS (
    SELECT name
    FROM stickers
    WHERE owner_id = $1
)
SELECT 
    (SELECT user_exists FROM user_exists) AS user_exists,
    (SELECT inventory_capacity FROM user_capacity) AS inventory_capacity,
    ARRAY(
        SELECT ROW(name, float)
        FROM skins
    ) AS skins,
    ARRAY(
        SELECT ROW(name)
        FROM stickers
    ) AS stickers;
