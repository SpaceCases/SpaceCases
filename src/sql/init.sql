CREATE TYPE item AS (
    "name" TEXT,
    "float" FLOAT
);

CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    last_claim DATE NOT NULL,
    claim_streak INT NOT NULL,
    balance BIGINT NOT NULL,
    inventory item[] NOT NULL,
    inventory_capacity INT NOT NULL
);
