INSERT INTO stickers (owner_id, name, count)
    VALUES ($1, $2, 1)
ON CONFLICT (owner_id, name)
    DO UPDATE SET
        count = stickers.count + 1
    RETURNING
        owner_id;

