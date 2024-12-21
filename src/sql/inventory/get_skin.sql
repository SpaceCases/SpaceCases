SELECT
    name,
    floats
FROM
    skins
WHERE
    owner_id = $1
    AND name = $2;

