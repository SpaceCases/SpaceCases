CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    last_claim DATE NOT NULL,
    claim_streak INT NOT NULL,
    balance BIGINT NOT NULL
);