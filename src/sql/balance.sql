-- obtain a user's balance
SELECT
    balance
FROM
    "users"
WHERE
    id = $1
