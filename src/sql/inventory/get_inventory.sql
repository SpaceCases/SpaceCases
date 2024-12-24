WITH skins AS (
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
    ARRAY(
        SELECT ROW(name, float)
        FROM skins
    ) AS skins,
    ARRAY(
        SELECT ROW(name)
        FROM stickers
    ) AS stickers;
