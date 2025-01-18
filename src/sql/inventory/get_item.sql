-- Get a item from a user by name, does an existence check which locks the row
WITH user_exists AS (
    SELECT EXISTS (SELECT 1 FROM "users" WHERE id = $1 FOR UPDATE) AS user_exists
),
item AS (
    SELECT name, type, details
    FROM items
    WHERE owner_id = $1 AND id = $2
)
SELECT 
    user_exists.user_exists,
    item.name,
    item.type,
    item.details
FROM user_exists, item;
