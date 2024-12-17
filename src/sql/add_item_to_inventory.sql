UPDATE "users"
SET inventory = inventory || ROW($2, $3)::item
WHERE id = $1 AND cardinality(inventory) < inventory_capacity
RETURNING id;
