-- Get a sticker from a user by name and return the count, does an existence check which locks the row
WITH user_exists AS (
    SELECT EXISTS (SELECT 1 FROM "users" WHERE id = ($1) FOR UPDATE) AS user_exists
),
stickers AS (
    SELECT COUNT(*) AS sticker_count
    FROM stickers
    WHERE owner_id = $1 AND name = $2
)
SELECT 
    (SELECT user_exists FROM user_exists) AS user_exists,
    (SELECT sticker_count FROM stickers) AS sticker_count;
