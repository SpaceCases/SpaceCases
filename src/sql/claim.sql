WITH user_exists AS (
    SELECT
        EXISTS (
            SELECT
                1
            FROM
                "users"
            WHERE
                id = $1) AS exists
),
claim_streak AS (
    SELECT
        CASE WHEN last_claim::date = CURRENT_DATE - INTERVAL '1 day' THEN
            claim_streak + 1
        WHEN last_claim::date < CURRENT_DATE - INTERVAL '1 day' THEN
            1 -- Reset streak if break more than 1 day
        ELSE
            claim_streak -- Keep current streak if claim is made today
        END AS streak
    FROM
        "users"
    WHERE
        id = $1
),
claim_amount AS (
    SELECT
        LEAST (10000 + (claim_streak.streak - 1) * 2000, 30000) AS amount
    FROM
        claim_streak
),
updated_user AS (
    UPDATE
        "users"
    SET
        last_claim = CURRENT_DATE,
        balance = balance + claim_amount.amount,
        claim_streak = claim_streak.streak
    FROM
        claim_amount,
        claim_streak
    WHERE
        id = $1
        AND last_claim::date < CURRENT_DATE
    RETURNING
        balance,
        claim_streak.streak,
        claim_amount.amount
)
SELECT
    CASE WHEN NOT EXISTS (
        SELECT
            1
        FROM
            user_exists
        WHERE
            EXISTS) THEN
        NULL -- User not found
    WHEN NOT EXISTS (
        SELECT
            1
        FROM
            updated_user) THEN
        FALSE -- User exists but cannot claim yet
    ELSE
        TRUE -- Success
    END AS status,
    updated_user.balance,
    updated_user.streak,
    updated_user.amount
FROM
    updated_user
    FULL OUTER JOIN user_exists ON TRUE
LIMIT 1;

