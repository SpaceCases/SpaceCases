WITH capacity_check AS (
    SELECT
        ((SELECT COUNT(*) FROM skins WHERE owner_id = $1) + 
         (SELECT COUNT(*) FROM stickers WHERE owner_id = $1)) < 
        (SELECT inventory_capacity FROM "users" WHERE id = $1) AS is_within_capacity
)
INSERT INTO stickers (owner_id, name)
SELECT $1, $2
FROM capacity_check
WHERE capacity_check.is_within_capacity
RETURNING owner_id;