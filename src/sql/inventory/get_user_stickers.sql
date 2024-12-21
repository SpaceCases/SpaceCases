SELECT name, count
FROM stickers
WHERE owner_id = $1;