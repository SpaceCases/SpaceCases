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
    INSERT INTO stickers (owner_id, name, count)
    SELECT
        $1,
        $2,
        1
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
                count = stickers.count + 1
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

