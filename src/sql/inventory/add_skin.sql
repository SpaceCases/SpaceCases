WITH current_size AS (
    SELECT
        (
            SELECT
                COUNT(*)
            FROM
                skins
            WHERE
                owner_id = $1) + (
                SELECT
                    COUNT(*)
                FROM
                    stickers
                WHERE
                    owner_id = $1) AS size,
                (
                    SELECT
                        inventory_capacity
                    FROM
                        users
                    WHERE
                        id = $1) AS capacity
),
upsert AS (
    -- Perform the insert or update only if size < capacity
    INSERT INTO skins (owner_id, name, floats)
    SELECT
        $1,
        $2,
        ARRAY[$3]::real[]
    WHERE (
        SELECT
            size
        FROM
            current_size) < (
            SELECT
                capacity
            FROM
                current_size)
        ON CONFLICT (owner_id,
            name)
            DO UPDATE SET
                floats = array_append(skins.floats, $3)
            RETURNING
                owner_id
)
    SELECT
        CASE WHEN EXISTS (
            SELECT
                1
            FROM
                upsert) THEN
            TRUE
        ELSE
            FALSE
        END AS inserted;

