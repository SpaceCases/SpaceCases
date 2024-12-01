UPDATE "users"
SET balance = balance + $1 
WHERE id = $2
RETURNING id, balance