INSERT INTO skins (owner_id, name, floats)
VALUES ($1, $2, ARRAY[$3]::REAL[])
ON CONFLICT (owner_id, name) 
DO UPDATE SET floats = array_append(skins.floats, $3)
RETURNING owner_id;
