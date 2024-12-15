WITH claim_amount AS (
    SELECT LEAST(10000 + claim_streak * 2000, 30000) AS amount
    FROM "users"
    WHERE id = $1
)
UPDATE "users"
SET 
    last_claim = CURRENT_DATE,
    balance = balance + claim_amount.amount,
    claim_streak = CASE 
        WHEN last_claim::date = CURRENT_DATE - INTERVAL '1 day' THEN claim_streak + 1
        ELSE 1
    END
FROM claim_amount
WHERE id = $1 AND last_claim::date < CURRENT_DATE
RETURNING balance, claim_streak, claim_amount.amount;